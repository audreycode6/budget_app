# BudgeTing

### A Python/Flask application backed by PostgreSQL that allows users to create and manage budgets across different time horizons (monthly or annually).

### Users can:

- _create and edit budgets_
- _track gross income, deductions, bills, savings, and debt_
- _demo budget creation without an account (persistence requires authentication)_

# Local Development

**Requirements:**

- Python 3.12+
- Poetry
- PostgreSQL

**Typical Development Workflow:**

1. Install project dependencies and create `.env`:

```shell
poetry install
cp .env.sample .env
# edit .env to set DATABASE_URL and SECRET_KEY
```

2. Start PostgreSQL and create the database (_see **PostgreSQL Setup** below_)
3. Apply migrations:

```shell
poetry run app db-migrate -m "Initial migration"
poetry run app db-upgrade
```

4. Start the server: `poetry run app start`
5. Run tests as you develop: `poetry run app test`

## Dependency Management (Poetry)

This project uses [Poetry](https://python-poetry.org/docs/) for dependency management and packaging.

1. Install dependencies: `poetry install`
2. To create new project: `poetry new project_name`

## PostgreSQL Setup (macOS + Homebrew)

1. Install [PostgreSQL](https://www.postgresql.org/).
2. Start the service: `brew services start postgresql@14` _replace postgresql@14 with your own version_
3. At initial setup, create the database: `createdb budget_db`

## Environment Variables

Create a `.env` file using `.env.sample` as a reference.

Required variables:

- **DATABASE_URL**:
  - The `DATABASE_URL` environment variable tells SQLAlchemy where your database lives and how to connect to it. It’s used by Flask to establish a connection when the app starts, as well as by Alembic during migrations. _During deployment, replace this with your production database URL provided by your hosting service._
  - `DATABASE_URL=postgresql://username:pw@localhost:5432/budget_db`
    - `username` your PostgreSQL username
    - `:pw` pw for PostgreSQL or remove if no pw
    - `/budget_db` your database name
- **SECRET_KEY**:
  - Flask uses to keep track of state in session and display flash messages
  - `SECRET_KEY=secret_key`, replace `secret_key` value with your own private key.

## CLI Commands

This project provides a helper CLI exposed via Poetry to standardize common development tasks
(running the server, tests, and database migrations).

All commands should be run **from the project root** using:

```bash
poetry run app <command>
```

To see the command options/ description: `poetry run app -h`

- Contributors should prefer the CLI unless debugging internals. As fallback, use explicit path & commands: e.g `poetry run flask --app <path> <command>`

### Database Migrations

This project uses Flask-Migrate (Alembic) to manage schema changes.
[Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) (which uses [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) under the hood) tracks these schema changes.

**Migrations Usage:**

- _Before you start, make sure PostgreSQL is running and verify your database exists._

1. **Intial setup:**
   Create the migrations/ folder (only run once at setup): `poetry run flask --app budget_app.app db init`

   - **Model definitions**: `models.py` (_i.e however your app organizes SQLAlchemy models_) holds the schema for the table structures, (user, budget, budget_item), to add to the db. Changes to these models require generating a new migration.

2. **Generate a new migration**:

```shell
poetry run app db-migrate -m "Note about new changes"
```

- _After generating migrations, commit the new files in the migrations/ directory so others and CI pick them up._

4. **Apply migrations**:

```shell
poetry run app db-upgrade
```

5. **Rollback** (_optional_):

```shell
poetry run app db-downgrade
```

- Reverts the most recent migration (useful for testing or undoing structural changes).

6. **View current migration history**:
   `poetry run flask --app budget_app.app db history`
   - Lists all migrations applied and pending, in chronological order.

### Running the Server

```shell
poetry run app start
```

### Running Tests

- _The CLI internally invokes `unittest` with project-specific defaults._

Run **all tests** (with verbosity `-v`):

```shell
poetry run app test -v
```

Run a **specific test module**:

```shell
poetry run app test-module <module path here>
```

- auth_test.py ex: `poetry run app test-module budget_app.routes.handlers.http.auth_test`

### Project Structure Notes

This project uses explicit `__init__.py` files to define Python packages and support unittest discovery and absolute imports.

- _A future refactor may adopt [pytest](https://docs.pytest.org/en/stable/) for lighter-weight test discovery._

<TODO>
# Deployment Setup

(brief explanation of what the production environment will use)
