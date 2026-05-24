# Database Migrations — Alembic Async

## Prerequisites

PostgreSQL 16+ running, database created:

```bash
psql -U postgres -c "CREATE DATABASE competescope;"
```

`.env` must contain a valid `DATABASE_URL`:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/competescope
```

## Quick Start

All commands run from the **project root** (`compete-scope-agent/`).

### 1. Generate the first migration (autogenerate)

```bash
cd backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate
alembic revision --autogenerate -m "init_tasks_reports_logs"
```

Alembic reads `backend/db/models.py` (the three tables), diffs against the live database, and writes a migration script into `backend/alembic/versions/`.

### 2. Review the generated migration

Open `backend/alembic/versions/<hash>_init_tasks_reports_logs.py` and verify:
- `upgrade()` creates `tasks`, `reports`, `execution_logs` tables
- Columns, types, constraints match the model definitions
- Enum type `task_status_enum` is created

### 3. Apply the migration

```bash
alembic upgrade head
```

Verify in psql:

```sql
\d tasks
\d reports
\d execution_logs
```

## Everyday Commands

| Command | What it does |
|---------|-------------|
| `alembic current` | Show current revision applied to the DB |
| `alembic history` | List all revisions in order |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back the last migration |
| `alembic downgrade base` | Roll back ALL migrations (empty DB) |
| `alembic revision --autogenerate -m "desc"` | Generate a new migration from model changes |
| `alembic upgrade +1` | Apply the next unapplied migration |
| `alembic stamp head` | Mark DB as up-to-date without running migrations |

## Workflow After Model Changes

```
# 1. Edit backend/db/models.py (add column / table)
# 2. Generate migration
cd backend && alembic revision --autogenerate -m "add_column_foo"
# 3. Review  the generated script
# 4. Apply
alembic upgrade head
# 5. Commit the migration file to git
```

## How It Works (async)

`backend/alembic/env.py`:
1. Imports all models → populates `Base.metadata`
2. `run_migrations_online()` creates an async engine from `settings.DATABASE_URL`
3. Inside `do_run_migrations()`, Alembic diffs `Base.metadata` vs live DB schema
4. `--autogenerate` writes the Python migration script

The `alembic.ini` `sqlalchemy.url` is a fallback — the real URL comes from `config.Settings` (`.env` file).

## Troubleshooting

**"Can't locate revision"** — Run from `backend/` directory where `alembic.ini` lives.

**"No changes detected"** — Models match the DB exactly. This is expected if you just ran `upgrade head`.

**"relation already exists"** — The migration was already applied. Check with `alembic current`.

**Enum type errors** — PostgreSQL enums require `create_type=True` on the SQLAlchemy Enum column. This is already set for `TaskStatus`.
