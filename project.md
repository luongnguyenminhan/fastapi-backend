# Software Requirements Specification (SRS)
## Project: Markdown Note Sharing Web App

---

## 1. Overview

### 1.1 Purpose
Build a web application that allows users to:
- Create and manage markdown-based notes
- Render notes in a readable format
- Share notes via unique links

### 1.2 Scope
Core features:
- Authentication (register/login)
- CRUD notes
- Markdown rendering
- Share notes via link (public/private access control)

Out of scope (for now):
- Realtime collaboration
- Version history
- Rich media uploads


---

## 2. System Architecture

### 2.1 Tech Stack
- Frontend: React + react-markdown
- Backend: FastAPI
- Database: MySQL / PostgreSQL
- Cache (optional): Redis
- Storage format: Markdown (plain text)

### 2.2 High-Level Flow
User → Frontend → API → Database

---

## 3. Functional Requirements

### 3.1 Authentication
- User can register (email + password)
- User can login/logout
- JWT-based authentication
- Password must be hashed (bcrypt)

---

### 3.2 Notes Management

#### Create Note
- User creates note with:
  - title
  - content (markdown)
- Stored as plain text

#### Read Note
- User can view:
  - raw markdown (edit mode)
  - rendered markdown (preview mode)

#### Update Note
- User edits note content

#### Delete Note
- Soft delete preferred (optional)

---

### 3.3 Markdown Rendering
- Use react-markdown to render content
- Support:
  - headings
  - lists
  - code blocks
  - links
- Sanitize input (prevent XSS)

---

### 3.4 Sharing Notes

#### Generate Share Link
- Each note can generate:
  - public URL (UUID-based)

Example:
`/note/{share_id}`

#### Access Control
- Modes:
  - Private (only owner)
  - Public (anyone with link)

#### Optional (if you’re not lazy)
- Expiry time for link
- Read-only vs editable link

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Load note < 500ms
- Support 1000+ notes per user

### 4.2 Security
- Input sanitization (markdown XSS risk)
- Auth required for all private routes
- Share link must be unguessable (UUID v4)

### 4.3 Scalability
- Stateless API
- Ready for horizontal scaling
