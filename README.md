# $ BudgeTing $

_Full-Stack Budgeting App_

**Live:** https://budget-thing.site

## Features

- **Multi-timeframe budgets** - Create, edit, and delete monthly or annual budgets
- **Income tracking** - Log gross income and view automatic calculations of expenses by category and net income after deductions
- **Expense management** - Create, update, and remove expenses across bills, savings, and debt categories
- **User authentication** - Secure signup/login with session management and error handling

## Demo

### User Authentication

![User authentication](src/budget_app/static/demos/account_creation.gif)

### Budget Creation

![Budget creation](src/budget_app/static/demos/budget_creation.gif)

### Error Handling

![Error handling](src/budget_app/static/demos/handle_bad_request.gif)

## Tech Stack

**Backend:** Python 3.12+, Flask, SQLAlchemy, Flask-Migrate  
**Database:** PostgreSQL  
**Testing:** unittest  
**Dev Tools:** Poetry  
**Deployment:** Docker Compose, gunicorn, Caddy, AWS Lightsail  
**Frontend:** HTML, CSS, JavaScript _(currently minimal, focus is backend)_

## Deployment

### Production setup

- **Host:** AWS Lightsail (Ubuntu, 1 GB RAM, static IP, 2 GB swap file). The firewall opens only ports 22 (SSH, to manage the server), 80 (HTTP, which Caddy redirects to HTTPS and Let's Encrypt uses to verify the domain) and 443 (HTTPS). Everything else stays closed.
- **HTTPS (`caddy`):** Caddy is the only service exposed to the internet. It gets and renews a Let's Encrypt certificate automatically, redirects HTTP to HTTPS, and forwards requests to the app. The domains are set in `Caddyfile`.
- **App (`web`):** Built from `Dockerfile` and served by gunicorn with 2 workers. Its port is bound to `127.0.0.1`, so it can only be reached through Caddy.
- **Database (`db`):** Postgres 17 in its own container. Data lives in the `pgdata` volume, so it survives restarts and rebuilds.
- **Restarts:** Every service uses `restart: unless-stopped`, so Docker brings it back after a crash or reboot.
- **DNS:** Namecheap A records for `@` and `www`, both pointing at the static IP.
- **Secrets:** Kept in `.env.docker` on the server (see `.env.sample`).

### Running the production setup

[Docker](https://docs.docker.com/get-started/docker-overview/) packages the app with its Python version and dependencies into an image, so it runs the same way on my Mac and on the server, and the server needs nothing installed but Docker. `docker-compose.yml` defines the 3 containers above (`web`, `db`, `caddy`), and Compose starts them together with one command.

> [!NOTE]
> For day-to-day coding and tests without Docker, see **Local Development**.

**Locally**, create `.env.docker` from `.env.sample` and keep `SESSION_COOKIE_SECURE=false` to be able to log in over plain HTTP. Then start the app and database and apply migrations:

```shell
docker compose up -d --build web db   # leaves out caddy, which needs the real domain
docker compose run --rm web flask --app budget_app.app db upgrade
```

The app runs at http://localhost:3000.

**On the server**, SSH in and deploy or update from the repo folder:

```shell
ssh -i <your-key>.pem ubuntu@<static-ip>
cd ~/budget_app
git pull
docker compose up -d --build          # starts all 3 services, including caddy
docker compose run --rm web flask --app budget_app.app db upgrade   # safe every deploy; only applies new migrations
```

The app is now live and secured with HTTPS. Only the containers that changed are replaced, so the site is down for a few seconds at most. The data and `.env.docker` are left untouched, and migrations run while the site stays up.

## Local Development

**Requirements:**

- Python 3.12+
- Poetry
- PostgreSQL

**First-time setup:**

1. Install project dependencies:

   ```shell
   poetry install
   ```

2. Start PostgreSQL and create the database (_see **PostgreSQL Setup** below_):

   ```shell
   createdb budget_db
   ```

3. Create your `.env` (_see **Environment Variables** below_):

   ```shell
   cp .env.sample .env
   ```

   Then edit `DATABASE_URL`: change the host from `db` to `localhost`, and match your own PostgreSQL user and database.

4. Apply the existing migrations to build the schema:

   ```shell
   poetry run app db-upgrade
   ```

   > This repo already contains its migrations in `migrations/versions/`. You do **not** run `db-migrate` during setup — that command _generates_ a new migration from model changes, and on a fresh clone it has nothing to generate.

5. Start the server: `poetry run app start` (defaults to http://localhost:3000)

**Day-to-day:**

- Run the server: `poetry run app start`
- Run tests as you develop: `poetry run app test`
- After changing `models.py`, generate and apply a migration (_see **Database Migrations** below_)

### Dependency Management (Poetry)

This project uses [Poetry](https://python-poetry.org/docs/) for dependency management and packaging.

- Install the project and its dependencies into a virtualenv: `poetry install`
- Add a new dependency: `poetry add <package>`
- Run anything inside the virtualenv: `poetry run <command>`

Poetry creates the virtualenv for you; there is no need to make one by hand. The `app` command used throughout this README is the CLI entry point declared under `[tool.poetry.scripts]` in `pyproject.toml`, which is why it only exists after `poetry install`.

### PostgreSQL Setup (macOS + Homebrew)

1. Install [PostgreSQL](https://www.postgresql.org/).
2. Start the service: `brew services start postgresql@14` _replace postgresql@14 with your own version_
3. At initial setup, create the database: `createdb budget_db`

### Environment Variables

Create a `.env` file using `.env.sample` as a reference: `cp .env.sample .env`.

Required variables:

- **DATABASE_URL**:
  - Tells SQLAlchemy where your database lives and how to connect to it. Used by Flask when the app starts, and by Alembic during migrations.
  - `DATABASE_URL=postgresql://username:pw@localhost:5432/budget_db`
    - `username` your PostgreSQL role — on a Homebrew install this is usually your macOS username, not `postgres`
    - `:pw` your password, or omit the `:pw` entirely if your local setup has no password (e.g. `postgresql://audrey@localhost:5432/budget_db`)
    - `/budget_db` your database name
  - Under Docker Compose, the host is `db` (the database service name) instead of `localhost`.
- **SECRET_KEY**:
  - Used by Flask to sign the session cookie and carry flash messages. Any non-guessable string works locally; use a real random value in production.
  - `SECRET_KEY=secret_key`, replace `secret_key` value with your own private key.
- **APP_PORT**:
  - Port the development server binds to. Defaults to `3000` in `.env.sample`.
- **SESSION_COOKIE_SECURE**:
  - Makes the session cookie HTTPS-only. Set `true` in production. Keep `false` locally, or you can't log in over plain HTTP.
- **POSTGRES_USER**, **POSTGRES_PASSWORD**, **POSTGRES_DB** (_Docker only_):
  - Used by the `db` container to create the database user and database on first start. They must match the values in `DATABASE_URL`. Not needed without Docker.

#### Troubleshooting

**`FATAL: role "<name>" does not exist`** — a long SQLAlchemy/psycopg2 traceback ending in this line means `DATABASE_URL` names a PostgreSQL role that isn't on your machine. It is a config problem, not a broken install: the placeholder from `.env.sample` was left in place, or the username doesn't match your actual role. Fix the username in `.env` and re-run.

**`FATAL: database "<name>" does not exist`** — same idea, for the database half of the URL. Run `createdb budget_db`.

**`connection refused` on port 5432** — PostgreSQL isn't running. Start it (`brew services start postgresql@14`) and confirm with `pg_isready`.

### CLI Commands

This project provides a helper CLI exposed via Poetry to standardize common development tasks
(running the server, tests, and database migrations).

All commands should be run **from the project root** using:

```bash
poetry run app <command>
```

To see the command options/ description: `poetry run app -h`

- Contributors should prefer the CLI unless debugging internals. As fallback, use explicit path & commands: e.g `poetry run flask --app <path> <command>`

### Database Migrations

This project uses [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) (which uses [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) under the hood) to manage schema changes.

**Migrations Usage:**

_Before you start, make sure PostgreSQL is running and verify your database exists._

- **Setting up a cloned repo:**

  The `migrations/` directory is committed, so there is nothing to initialize. Just apply what's already there:

  ```shell
  poetry run app db-upgrade
  ```

  - **Model definitions**: `models.py` (_i.e however your app organizes SQLAlchemy models_) holds the schema for the table structures, (user, budget, budget_item), to add to the db. Changes to these models require generating a new migration.

- **Generate a new migration** (_only after changing `models.py`_):

  ```shell
  poetry run app db-migrate -m "Note about new changes"
  ```

  _After generating migrations, commit the new files in the migrations/ directory so others and CI pick them up._

- **Apply migrations**:

  ```shell
  poetry run app db-upgrade
  ```

- **Rollback** (_optional_):

  ```shell
  poetry run app db-downgrade
  ```

  - Reverts the most recent migration (useful for testing or undoing structural changes).

- **View current migration history**:

  ```shell
  poetry run flask --app budget_app.app db history
  ```

  - Lists all migrations applied and pending, in chronological order.

- **Check which revision your database is currently at**:

  ```shell
  poetry run flask --app budget_app.app db current
  ```

  - Useful when you are unsure whether your local database is up to date with `migrations/versions/`.

### Running Tests

> [!NOTE]
> The test suite requires no database; service tests use in-memory SQLite.

The CLI internally invokes `unittest` with project-specific defaults. Explicit `__init__.py` files define the Python packages, which is what makes unittest discovery and absolute imports work.

Run **all tests** (with verbosity `-v`):

```shell
poetry run app test -v
```

Run a **specific test module**:

```shell
poetry run app test-module <module path here>
```

- testing `auth_test.py` example: `poetry run app test-module budget_app.routes.handlers.http.auth_test`

> [!NOTE]
> A future refactor may adopt [pytest](https://docs.pytest.org/en/stable/) for lighter-weight test discovery.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

This is a portfolio project, feedback is welcome! Open an issue or submit a PR.

## Author

**Audrey** - [GitHub](https://github.com/audreycode6) | [LinkedIn](https://www.linkedin.com/in/audrey-theriault-allaire/)
