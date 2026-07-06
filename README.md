# Collaboration Platform Backend

A **production-style collaboration platform backend** built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**.

This project demonstrates modern backend engineering practices including secure authentication, role-based access control (RBAC), layered architecture, task lifecycle management, and audit logging.

Designed as a portfolio project to showcase production-ready backend development skills beyond CRUD applications.

---

##  Features

###  Authentication

- User Registration
- Secure Password Hashing (Argon2)
- JWT Authentication
- Access & Refresh Tokens
- Refresh Token Rotation
- Logout
- Logout from All Devices
- Maximum 5 Active Refresh Tokens per User
- Refresh Tokens stored as SHA-256 hashes

---

###  Organizations

- Create Organizations
- Organization Membership
- Owner / Admin / Member Roles
- RBAC Authorization
- Add Members to Organization
- List User Organizations

---

###  Teams

- Create Teams
- Organization scoped teams
- Add Members to Teams
- List Team Members
- Organization validation
- Team Membership validation

---

###  Task Management

- Create Tasks
- View Task
- List Organization Tasks
- Assign Team
- Assign User
- Update Status
- Update Priority
- Reopen Task
- Business Rule Validation

---

###  Audit Trail

Every important task action is recorded.

- Task Created
- Team Assigned
- User Assigned
- Status Changed
- Priority Changed
- Task Reopened

---

#  System Architecture

```text
                    +----------------------+
                    |      FastAPI API     |
                    +----------+-----------+
                               |
        +----------------------+----------------------+
        |                      |                      |
+-------v-------+      +-------v-------+      +-------v-------+
| Authentication|      | Organizations |      |    Tasks      |
+-------+-------+      +-------+-------+      +-------+-------+
        |                      |                      |
        +----------------------+----------------------+
                               |
                      +--------v---------+
                      |  Service Layer   |
                      +--------+---------+
                               |
                      +--------v---------+
                      | Repository Layer |
                      +--------+---------+
                               |
                      +--------v---------+
                      | PostgreSQL DB    |
                      +------------------+
```

---

#  Project Structure

```text
app
│
├── core
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   └── security.py
│
├── models
│
├── modules
│   ├── auth
│   ├── users
│   ├── organizations
│   ├── teams
│   └── tasks
│
├── migrations
│
└── main.py
```

---

#  Architecture

This project follows a layered architecture.

```text
                HTTP Request
                     │
                     ▼
                API Routes
                     │
                     ▼
              Business Services
                     │
                     ▼
               Repository Layer
                     │
                     ▼
               PostgreSQL Database
```

### Route Layer

Responsible for:

- Request validation
- Dependency Injection
- Response Models
- HTTP Exceptions

---

### Service Layer

Responsible for:

- Business Logic
- Authorization
- Transactions
- Validations

---

### Repository Layer

Responsible for:

- Database Queries
- CRUD Operations
- SQLAlchemy ORM

---

#  Authentication Flow

```text
           Login
             │
             ▼
     Verify Credentials
             │
             ▼
   Generate Access Token
   Generate Refresh Token
             │
             ▼
Hash Refresh Token (SHA256)
             │
             ▼
 Save Hash in PostgreSQL
             │
             ▼
 Return Tokens
```

Refresh Flow

```text
Refresh Token
      │
      ▼
Hash Token
      │
      ▼
Compare Hash in Database
      │
      ▼
Generate New Access Token
Generate New Refresh Token
      │
      ▼
Delete Old Refresh Token
      │
      ▼
Store New Refresh Token
```

---

#  Organization Hierarchy

```text
Organization
│
├── Owner
├── Admin
├── Members
│
├── Team A
│   ├── User
│   ├── User
│
├── Team B
│   ├── User
│   ├── User
│
└── Tasks
```

---

#  Task Lifecycle

```text
Create Task
     │
     ▼
Assign Team
     │
     ▼
Assign User
     │
     ▼
TODO
     │
     ▼
IN_PROGRESS
     │
 ┌───┴────┐
 ▼        ▼
ON_HOLD COMPLETED
 │         │
 └────┬────┘
      ▼
   Reopen
      │
      ▼
     TODO
```

---

#  Business Rules

### Authentication

- Refresh Tokens are hashed before storage.
- Maximum 5 active refresh tokens per user.
- Refresh Token Rotation implemented.

### Organizations

- Every organization has one Owner.
- Only Owner/Admin can create teams.
- Only Owner/Admin can add organization members.

### Teams

- Users must belong to an organization before joining a team.
- Teams belong to exactly one organization.

### Tasks

- Task can exist without a team.
- User cannot be assigned until a team is assigned.
- Assigned user must belong to the assigned team.
- Reopening clears the assigned user.
- Team assignment is preserved if the team still exists.

