# Chat Knowledge Gate Implementation Plan
**Task ID:** chat-knowledge-gate-v1  
**Created:** 2025-02-02  
**Status:** PLANNING  
**Approach:** Hybrid Approach 2 + 3 with Agno Agentic Search

---

## Task Description

Refactor chat message processing to implement intelligent, agent-controlled knowledge retrieval system using Agno's built-in agentic capabilities. Replace forced context injection with optional knowledge access via custom tools, enabling natural conversation flow while maintaining access to extracted important notes.

**Goals:**
1. Eliminate forced context injection causing bias in casual queries
2. Implement agent-controlled knowledge access (not auto-injected)
3. Cache important_notes from Qdrant for quick agent access
4. Reduce latency for non-retrieval queries (casual chat)
5. Leverage Agno's MemoryTools + agentic search patterns
6. Minimal code changes, maximum flexibility

---

## Current State Analysis

### Problems
- **Query Expansion on Every Chat:** Even "hello cậu" triggers `perform_query_expansion_search`
- **Forced Context Injection:** All retrieved documents automatically injected into prompt
- **Agent Bias:** LLM biased toward document content instead of natural responses
- **High Latency:** 5-minute responses for simple greetings due to retrieval overhead
- **No Intent Detection:** No differentiation between casual vs knowledge-seeking queries

### Current Flow
```
User Message → [ALWAYS] Query Mentions → [ALWAYS] Expansion Search 
→ [ALWAYS] Build Enhanced Content → [FORCE] Inject into Prompt 
→ Agent Response (biased by documents)
```

### Key Files Involved
- `app/utils/llm.py` - Agent creation (create_general_chat_agent)
- `app/jobs/tasks/chat_tasks.py` - Message processing (process_chat_message)
- `app/modules/chat/services/chat.py` - Document querying
- `app/modules/chat/schemas/chat.py` - Mention schema

---

## Proposed Solution Architecture

### Hybrid Approach 2 + 3: Knowledge Gate Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ User Message + Optional Mentions                            │
└────────────────────┬────────────────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │ Mention-Based Query (Fast) │
        │ - Only if mentions exist   │
        │ - Extract important_notes  │
        │ - Cache to Redis           │
        └────────┬───────────────────┘
                 ↓
        ┌──────────────────────────┐
        │ Create Agent with Tools  │
        │ - MemoryTools (disabled) │
        │ - KnowledgeGateTool      │
        └────────┬─────────────────┘
                 ↓
        ┌──────────────────────────────┐
        │ Agent.run(query, history)    │
        │                              │
        │ Agent DECIDES:               │
        │ - Casual? Direct response    │
        │ - Knowledge? Call tools      │
        └──────────────────────────────┘
```

### Key Components

#### 1. **KnowledgeGateTool** (NEW)
- Custom Agno tool for agent to access cached important_notes
- Retrieves from Redis cache (populated from Qdrant payloads)
- Agent calls explicitly when needed
- No auto-injection into context

#### 2. **Simplified query_documents_for_mentions()**
- Query only mention-based documents (no expansion)
- Extract important_notes from payloads
- Cache to Redis with mention_id as key
- Return documents for caching only

#### 3. **Updated create_general_chat_agent()**
- `add_memories_to_context=False` (KEY: Agno won't auto-inject)
- Add KnowledgeGateTool to tools list
- Update system prompt with tool usage guidelines
- Enable `search_knowledge=True` (agent decides when to search)

#### 4. **Simplified process_chat_message()**
- Remove expansion search logic
- Keep mention-based query
- Pass to agent WITHOUT context enhancement
- Agent self-manages knowledge access

---

## Implementation Strategy

### Phase 1: Create KnowledgeGateTool
**Responsibility:** Access important_notes cache, provide search capability

**File:** `app/utils/knowledge_gate.py` (NEW)

```
- KnowledgeGateTool class
  - get_important_notes(mention_type, entity_id) → str
  - search_knowledge(query, mention_ids) → str
  - _fetch_from_redis(key) → List[str]
  - _fetch_from_qdrant(filters) → List[str]
```

### Phase 2: Update Agent Creation
**Responsibility:** Configure Agno agent with knowledge tools

**File:** `app/utils/llm.py`

```
- Modify create_general_chat_agent()
  - Import KnowledgeGateTool
  - Initialize knowledge_gate instance
  - Add to agent.tools list
  - Set add_memories_to_context=False
  - Update system description/instructions
```

### Phase 3: Simplify Chat Processing
**Responsibility:** Remove forced context injection, use agent autonomy

**File:** `app/jobs/tasks/chat_tasks.py`

```
- Modify process_chat_message()
  - Remove enhanced_content building
  - Keep mention-based query
  - Cache important_notes to Redis
  - Pass clean query to agent.run()
```

### Phase 4: Optimize Retrieval
**Responsibility:** Lightweight mention-only query with caching

**File:** `app/modules/chat/services/chat.py`

```
- Modify query_documents_for_mentions()
  - Remove expansion search
  - Extract important_notes from payloads
  - Cache to Redis per mention
  - Keep mention query only
```

---

## Detailed Implementation Checklist

### 1. Create KnowledgeGateTool (NEW FILE)
- [ ] Create `app/utils/knowledge_gate.py`
- [ ] Import required modules (redis, qdrant-client, logging)
- [ ] Define KnowledgeGateTool class
- [ ] Implement `get_important_notes(mention_type, entity_id)` method
  - [ ] Build Redis key: `knowledge:important_notes:{mention_type}:{entity_id}`
  - [ ] Try fetch from Redis first
  - [ ] If miss, query Qdrant with filters
  - [ ] Extract important_notes from payload
  - [ ] Cache to Redis (24h TTL)
  - [ ] Return formatted string or empty list
- [ ] Implement `search_knowledge(query, mention_ids)` method
  - [ ] For each mention_id, fetch important_notes
  - [ ] Combine results
  - [ ] Return formatted search results string
- [ ] Implement `_fetch_from_redis(key)` helper
- [ ] Implement `_fetch_from_qdrant(mention_type, entity_id)` helper
- [ ] Add proper error handling and logging
- [ ] Add docstrings to all methods

### 2. Update Agent Creation (llm.py)
- [ ] Add import: `from app.utils.knowledge_gate import KnowledgeGateTool`
- [ ] Modify `create_general_chat_agent()` function
  - [ ] Initialize: `knowledge_gate = KnowledgeGateTool()`
  - [ ] Add to agent initialization:
    - [ ] `tools=[knowledge_gate]`
    - [ ] `enable_user_memories=True`
    - [ ] `add_memories_to_context=False`
    - [ ] `search_knowledge=True`
  - [ ] Update description/instructions with:
    - [ ] Available tools: knowledge_gate methods
    - [ ] When to use: knowledge-seeking queries only
    - [ ] Rules: prefer natural conversation, use tools judiciously
- [ ] Test agent initialization

### 3. Simplify Chat Message Processing (chat_tasks.py)
- [ ] Modify `process_chat_message()` function
  - [ ] Keep mention parsing logic
  - [ ] Call: `query_documents_for_mentions()` with `include_query_expansion=False`
  - [ ] Remove mention_results + expansion_results combining
  - [ ] Remove optimized_contexts building
  - [ ] Remove enhanced_content building (KEY CHANGE)
  - [ ] Change agent.run() call to: `agent.run(content, history=history)`
    - No context injection
    - No optimized_contexts parameter
  - [ ] Cache important_notes to Redis (done in query_documents_for_mentions)
- [ ] Update logging to track agent-controlled retrieval

### 4. Optimize Document Retrieval (chat.py)
- [ ] Modify `query_documents_for_mentions()` signature
  - [ ] Keep `include_query_expansion: bool` parameter
  - [ ] Default to `False`
  - [ ] If called with `True`, still support old behavior (backward compat)
- [ ] Add Redis caching for important_notes
  - [ ] After retrieving documents
  - [ ] Extract `important_notes` from payload
  - [ ] Cache: `redis.set(f"knowledge:important_notes:{mention_id}", json.dumps(notes), ex=86400)`
  - [ ] Add to imports: `from app.utils.redis import get_async_redis_client`
- [ ] Remove/comment out expansion search call (when `include_query_expansion=False`)
- [ ] Return mention_results directly without expansion

### 5. Update Mention Query Parameters (chat_tasks.py)
- [ ] Update `query_documents_for_mentions()` call:
  ```python
  mention_candidates = await query_documents_for_mentions(
      mention_models,
      current_user_id=user_id_str or None,
      db=db,
      content=None,  # Changed from content
      include_query_expansion=False,  # Changed from True
  )
  ```

### 6. Remove Expansion Search Override (chat_tasks.py)
- [ ] Remove: `include_query_expansion=False` parameter in original call
- [ ] Keep only mention-based query
- [ ] Remove expansion_candidates logic
- [ ] Remove combined_candidates merging
- [ ] Remove context optimization (optimize_contexts_with_llm)

### 7. Add Redis Helper Function (redis.py)
- [ ] Add async function: `cache_important_notes()`
  - Parameters: mention_type, entity_id, important_notes
  - Action: Set Redis key with 24h TTL
  - Returns: bool (success)
- [ ] Add function: `get_cached_important_notes()`
  - Parameters: mention_type, entity_id
  - Returns: List[str] or empty list

### 8. Update System Prompt (llm.py)
- [ ] Add section to agent description about knowledge tools
- [ ] Add usage guidelines:
  - "Use knowledge_gate.get_important_notes() when user mentions specific meeting/project/file"
  - "Use knowledge_gate.search_knowledge() when user asks for detailed information"
  - "For casual queries, rely on conversation history and natural response"
  - "Prioritize conversation flow over document content"

### 9. Testing & Validation
- [ ] Unit test KnowledgeGateTool methods
- [ ] Test Redis caching/retrieval
- [ ] Test agent with casual query (no retrieval)
- [ ] Test agent with mention (tool access available)
- [ ] Test tool response formatting
- [ ] Test backward compatibility (if expansion_search=True still works)
- [ ] Performance test: measure latency for casual queries

### 10. Documentation & Logging
- [ ] Add docstrings to KnowledgeGateTool
- [ ] Add detailed logging in process_chat_message()
  - [ ] Log when mention found
  - [ ] Log when important_notes cached
  - [ ] Log when agent calls knowledge tools
  - [ ] Log agent decision (retrieval needed or not)
- [ ] Update code comments for future maintainers
- [ ] Add error handling for Redis/Qdrant failures

---

## File Structure & Changes

### New Files
```
app/
  utils/
    knowledge_gate.py  (NEW - ~150 LOC)
```

### Modified Files
```
app/
  utils/
    llm.py  (~20 LOC added, 0 removed)
    redis.py  (~15 LOC added - helper functions)
  jobs/
    tasks/
      chat_tasks.py  (~40 LOC removed, ~10 LOC modified)
  modules/
    chat/
      services/
        chat.py  (~5 LOC modified, expansion search optional)
```

### No Changes Needed
```
app/
  modules/
    chat/
      schemas/
        chat.py  (Mention class unchanged)
  models/
    chat.py  (Chat models unchanged)
```

---

## Integration Points

### 1. Redis Cache Integration
- **Location:** `KnowledgeGateTool._fetch_from_redis()`
- **Key format:** `knowledge:important_notes:{mention_type}:{entity_id}`
- **TTL:** 86400 seconds (24 hours)
- **Fallback:** Qdrant query if cache miss

### 2. Qdrant Integration
- **Location:** `KnowledgeGateTool._fetch_from_qdrant()`
- **Query:** Filter by mention_type, entity_id from payload
- **Extract:** `important_notes` field from payload
- **Transform:** List[str] to formatted string

### 3. Agno Agent Integration
- **Location:** `create_general_chat_agent()` in llm.py
- **Configuration:**
  - `add_memories_to_context=False`
  - `search_knowledge=True`
  - `tools=[knowledge_gate]`
- **Agent Behavior:** Self-decides when to use tools

### 4. Chat Message Processing
- **Location:** `process_chat_message()` in chat_tasks.py
- **Flow:** Query mentions → Cache important_notes → Call agent.run(content, history)
- **No Enhancement:** Raw content + history, no context injection

---

## Success Criteria

✅ **Casual queries ("hello cậu") respond in <2 seconds**  
✅ **Agent naturally replies without document bias**  
✅ **Mention-based queries show contextual awareness**  
✅ **Agent controls knowledge access (not forced)**  
✅ **Important notes cached and accessible**  
✅ **Backward compatible (no breaking changes)**  
✅ **Code complexity reduced (expansion search optional)**  

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Agent doesn't use tools | Medium | Clear prompt instructions + examples |
| Redis cache miss | Low | Fallback to Qdrant query |
| Latency regression | Low | Test casual queries < 2s |
| Breaking changes | Low | Backward compat in query_documents_for_mentions |
| Tool response formatting | Medium | Test agent tool usage patterns |

---

## Current Execution Step: "Phase 4 Complete"

- Status: **IN PROGRESS**
- Date: 2025-02-02
- Progress: 4 of 10 phases completed (40%)

---

## Task Progress

**[2025-02-02_00:00:00]**
- Task: Chat Knowledge Gate Implementation Planning
- Status: PLANNING COMPLETE
- Next: EXECUTE MODE

**[2025-02-02_EXEC_PHASE_1]**
- Task: Create KnowledgeGateTool
- Files: app/utils/knowledge_gate.py (NEW - 300 LOC)
- Status: ✅ SUCCESSFUL
- Changes: 
  - KnowledgeGateTool class with Redis + Qdrant clients
  - get_important_notes(mention_type, entity_id) - retrieve cached notes with fallback
  - search_knowledge(query, mention_ids) - search across mentions
  - _fetch_from_redis, _fetch_from_qdrant helpers
  - _cache_to_redis with 24h TTL
  - Singleton pattern with get_knowledge_gate_tool()

**[2025-02-02_EXEC_PHASE_2]**
- Task: Update Agent Creation in llm.py
- Files: app/utils/llm.py (~25 LOC added)
- Status: ✅ SUCCESSFUL
- Changes:
  - Import: from app.utils.knowledge_gate import get_knowledge_gate_tool
  - Initialize: knowledge_gate = get_knowledge_gate_tool()
  - Agent config: 
    - add_memories_to_context=False (KEY - memories NOT auto-injected)
    - tools=[knowledge_gate]
    - search_knowledge=True
  - Updated system description with tool usage guidelines
  - Added instructions: use tools for knowledge-seeking only, not for casual queries

**[2025-02-02_EXEC_PHASE_3]**
- Task: Simplify Chat Message Processing in chat_tasks.py
- Files: app/jobs/tasks/chat_tasks.py (~150 LOC removed, ~35 LOC added)
- Status: ✅ SUCCESSFUL
- Changes:
  - REMOVED: expansion_candidates logic
  - REMOVED: context deduplication + aggregation
  - REMOVED: LLM rerank optimization
  - REMOVED: enhanced_content building
  - ADDED: Important notes caching to Redis for agent access
  - CHANGED: agent.run(content, history) - NO context injection
  - Logging: Track mention counts, knowledge caching, agent-controlled access

**[2025-02-02_EXEC_PHASE_4]**
- Task: Optimize Document Retrieval in chat.py
- Files: app/modules/chat/services/chat.py (~10 LOC modified)
- Status: ✅ SUCCESSFUL
- Changes:
  - Modified query_documents_for_mentions()
  - include_query_expansion: default changed from True → False
  - Expansion search now LEGACY/OPTIONAL (only if explicitly enabled)
  - Docstring: Clarified agent-controlled knowledge access pattern
  - Backward compatible: can still enable expansion if needed

---

## Remaining Phases (6 of 10)

- [ ] Phase 5: Update Mention Query Parameters
- [ ] Phase 6: Remove Expansion Search Override
- [ ] Phase 7: Add Redis Helper Functions  
- [ ] Phase 8: Update System Prompt with Examples
- [ ] Phase 9: Testing & Validation
- [ ] Phase 10: Documentation & Logging Enhancement
