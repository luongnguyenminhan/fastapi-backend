# Task Module Refactor: Task → MeetingItem

**File name:** 2025-03-09_1_task_refactor_to_meeting_items.md  
**Created at:** 2025-03-09_00:00:00  
**Created by:** anlnm  
**Main branch:** main  
**Task Branch:** feature/refactor-task-to-meeting-item_2025-03-09_1  
**Yolo Mode:** Ask

## Task Description
Refactor the entire Task module to be more generic as MeetingItem. This allows meeting items to represent multiple types of entities (tasks, questions, action items, etc.) instead of just tasks. Remove non-essential fields (reminder_at, due_date, priority) and make columns more nullable to support generic use cases.

---

## Current Architecture Analysis

### Task Model Structure (app/models/task.py)
**Table:** `v2_tasks`

**Current Fields:**
- `id` (INT, PK, auto-increment)
- `created_at` (DateTime, TZ, server_default=now(), NOT NULL)
- `updated_at` (DateTime, TZ, onupdate)
- `title` (VARCHAR(255), NOT NULL)
- `description` (TEXT, nullable)
- `creator_id` (FK → v2_users.id, NOT NULL)
- `assignee_id` (FK → v2_users.id, nullable)
- `status` (VARCHAR(50), default="todo")
- `priority` (VARCHAR(50), default="Trung bình") ⚠️ **REMOVE**
- `meeting_id` (FK → v2_meetings.id, nullable)
- `due_date` (DateTime, TZ, nullable) ⚠️ **REMOVE**
- `reminder_at` (DateTime, TZ, nullable) ⚠️ **REMOVE**

**Relationships:**
- `creator` → User (creator_id FK)
- `assignee` → User (assignee_id FK)
- `meeting` → Meeting (meeting_id FK)
- `projects` → TaskProject (one-to-many)

### TaskProject Model (app/models/task.py)
**Table:** `v2_tasks_projects`

**Current Fields:**
- `task_id` (FK → v2_tasks.id, PK)
- `project_id` (FK → v2_projects.id, PK)

**Relationships:**
- `task` → Task
- `project` → Project (back_populates="tasks")

---

## Dependency Map: Modules Using Task Model

### 1. **Task Module** (app/modules/task/)
- **CRUD:** app/modules/task/crud/task.py
  - `crud_create_task()`
  - `crud_get_task()`
  - `crud_get_tasks()` - queries by due_date_gte, due_date_lte
  - `crud_update_task()`
  - `crud_delete_task()`
  - `crud_check_direct_access()`, `crud_check_meeting_access()`, `crud_check_project_access()`

- **Schemas:** app/modules/task/schemas/task.py
  - `TaskCreate` - includes priority, due_date, reminder_at
  - `TaskUpdate` - includes due_date, reminder_at
  - `TaskResponse` - includes all fields
  - `BulkTaskCreate`, `BulkTaskUpdate`, `BulkTaskDelete`, `BulkTaskResponse`

- **Services:** app/modules/task/services/task.py
  - `create_task()`
  - `update_task()`
  - `delete_task()`
  - `get_task()` / `get_tasks()` / `get_tasks_by_meeting()` / `serialize_task()`
  - `bulk_create_tasks()`
  - `check_task_access()`

- **Routes:** app/modules/task/routes/v1/task.py
  - GET `/tasks` - with filters: due_date_gte, due_date_lte
  - POST `/tasks`
  - GET `/tasks/{task_id}`
  - PUT `/tasks/{task_id}`
  - DELETE `/tasks/{task_id}`
  - POST `/tasks/bulk/create`
  - PUT `/tasks/bulk/update`
  - DELETE `/tasks/bulk/delete`

### 2. **Meetings Module** (app/modules/meetings/)
- **CRUD:** app/modules/meetings/crud/meeting_note.py
  - `crud_delete_meeting_tasks()` - deletes tasks associated with meeting
  - Uses Task model directly

- **Services:** app/modules/meetings/services/meeting_note.py
  - Creates Task objects from extracted meeting items
  - Passes priority field to TaskCreate
  - Line 26: `priority=item_dict.get("priority", "Trung bình")`

- **Utils:** app/modules/meetings/utils/meeting.py
  - Imports Task model

- **Agent Schema:** app/modules/meetings/utils/meeting_agent/agent_schema.py
  - `Task` class (Pydantic) - includes priority, due_date
  - Used for LLM task extraction
  - `TaskItems` wrapper

- **Agent Prompts:** app/modules/meetings/utils/meeting_agent/meeting_prompts.py
  - Instructs LLM to extract tasks with priority values: "Cao", "Trung bình", "Thấp"
  - Example: "priority (bắt buộc): "Cao", "Trung bình", hoặc "Thấp" (mặc định "Trung bình" nếu không rõ)"
  - Response schema includes: description, priority, due_date

### 3. **Common Module** (app/modules/common/)
- **Statistics CRUD:** app/modules/common/crud/statistics.py
  - `crud_get_task_aggregates()` - counts tasks by status, uses due_date for overdue/due_today/due_this_week
  - `crud_get_task_period_counts()`
  - `crud_get_task_chart_data()`
  - `crud_get_task_stats_by_project()`

- **Statistics Services:** app/modules/common/services/statistics.py
  - Imports Task, TaskProject
  - Aggregates task statistics for dashboards

### 4. **Users Module** (app/modules/users/)
- **CRUD:** app/modules/users/crud/user.py
  - Line 105: imports TaskProject
  - Line 117: imports Task
  - Uses for user task relationships

- **Schemas:** app/modules/users/schemas/user.py
  - `TaskResponse` class (different from task module version)

### 5. **Models Init** (app/models/__init__.py)
- Exports Task, TaskProject

---

## Usage Patterns

### Priority Field Usage
- **Agent Schema:** default "Trung bình"
- **Meeting Service:** extracts from item_dict
- **Meeting Prompt:** instructs LLM to extract as required field
- **CRUD:** no special handling
- **Routes:** no filtering by priority

### Due Date Field Usage
- **Queries:** CRUD filters by due_date_gte, due_date_lte
- **Routes:** GET /tasks endpoint accepts these filters
- **Statistics:** aggregates overdue, due_today, due_this_week
- **Agent Schema:** parsed from string to datetime

### Reminder At Field Usage
- **Routes:** included in TaskCreate/TaskUpdate schemas
- **CRUD:** no special handling
- **Services:** no notification logic visible
- ⚠️ **APPEARS UNUSED** - no validation or reminders triggered

---

## Fields to Remove
1. ✅ `priority` - Used only in initial extraction, not queried/filtered/aggregated
2. ✅ `due_date` - Significant usage but can be made optional for generic items
3. ✅ `reminder_at` - Appears completely unused

---

## Files Requiring Refactoring

### Models (Database Schema)
1. `app/models/task.py` - Core model
   - Rename Task → MeetingItem
   - Rename TaskProject → MeetingItemProject
   - Rename table: v2_tasks → v2_meeting_items
   - Rename table: v2_tasks_projects → v2_meeting_items_projects
   - Remove: priority, due_date, reminder_at fields
   - Make columns nullable where appropriate

### Schemas
2. `app/modules/task/schemas/task.py`
   - TaskCreate, TaskUpdate, TaskResponse
   - Remove priority, due_date, reminder_at
   - Update to work with nullable fields

### CRUD Operations
3. `app/modules/task/crud/task.py`
   - Update all queries to reference MeetingItem
   - Remove due_date filtering logic
   - Update relationship loads

### Services
4. `app/modules/task/services/task.py`
   - Update all references
   - Remove due_date-based logic

### Routes
5. `app/modules/task/routes/v1/task.py`
   - Remove due_date_gte, due_date_lte query parameters
   - Update request/response models

### Meetings Integration
6. `app/modules/meetings/services/meeting_note.py`
   - Update task creation to use MeetingItem
   - Remove priority assignment (use schema default or omit)

7. `app/modules/meetings/crud/meeting_note.py`
   - Rename crud_delete_meeting_tasks → crud_delete_meeting_items
   - Update relationship names

8. `app/modules/meetings/utils/meeting_agent/agent_schema.py`
   - Update Task schema to remove priority, due_date
   - Consider renaming to MeetingItem for consistency

9. `app/modules/meetings/utils/meeting_agent/meeting_prompts.py`
   - Remove priority extraction instructions
   - Update expected response schema

### Statistics
10. `app/modules/common/crud/statistics.py`
    - Remove due_date-based aggregations (overdue, due_today, due_this_week)
    - Update query logic for generic MeetingItem

11. `app/modules/common/services/statistics.py`
    - Update Task references to MeetingItem

### Users Module
12. `app/modules/users/crud/user.py`
    - Update imports and relationships

13. `app/models/__init__.py`
    - Update exports: Task → MeetingItem, TaskProject → MeetingItemProject

14. `app/models/user.py`
    - Update relationships: created_tasks → created_meeting_items, assigned_tasks → assigned_meeting_items

15. `app/models/meeting.py`
    - Update relationship: tasks → meeting_items

16. `app/models/project.py`
    - Update relationship: tasks → meeting_items (via TaskProject → MeetingItemProject)

---

## Complex Dependencies to Handle

### Statistics Module ⚠️
The statistics module heavily relies on due_date filtering:
- Overdue calculation: `Task.status != "done" AND Task.due_date < now`
- Due today: `Task.due_date between today_start and today_start + 1 day`
- Due this week: `Task.due_date between today_start and today_start + 7 days`

**Decision:** Make due_date optional, update statistics queries to check for NULL values, keep aggregation logic but return 0 for date-based metrics when field is absent.

### Agent Schema vs Model Schema ⚠️
There are TWO Task classes:
1. `app.models.task.Task` - SQLModel (database)
2. `app.modules.meetings.utils.meeting_agent.agent_schema.Task` - Pydantic (LLM)

**Decision:** Rename database model to MeetingItem, rename agent schema Task to match or clarify its purpose (possibly MeetingItemData or TaskData for extraction).

### Meeting Item Type Handling ⚠️
Current model doesn't distinguish between task type, question type, etc.
**Decision:** Keep model simple (flexible), add optional `item_type` field for future categorization (not part of this phase).

---

## ⚠️ WARNING: CRITICAL PROTOCOL RULES ⚠️

This task MUST follow RIPER-5 protocol:
1. **RESEARCH MODE** (Current) - Information gathering only
2. **INNOVATE MODE** - Brainstorm approaches
3. **PLAN MODE** - Create detailed implementation specs
4. **EXECUTE MODE** - Implement changes exactly as planned
5. **REVIEW MODE** - Validate against plan

**Transition signals required:** ENTER [MODE_NAME] MODE

---

## Analysis
✅ Research phase complete. Key dependencies identified:
- 16 files require changes across 5 modules
- Statistics module is most complex due date usage
- Agent schema adds naming ambiguity
- No existing "type" field, system assumes all items are tasks

---

## Current execution step: "1. Research Complete"

---

## Task Progress
[Ready for INNOVATE mode to discuss refactoring approaches]

---

## Final Review:
[Pending completion - awaiting mode transitions]
