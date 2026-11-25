# bnpl-tracker

A Buy Now, Pay Later tracker. A purchase with a provider such as Klarna, Afterpay or PayPal Pay in 3 is split into instalments, each with a due date. The tracker records those purchases, marks instalments paid, detects late payments and their fees, reminds you when an instalment is due soon or overdue, and shows the total debt per provider and per month.

## Team

| Member | Module | Shared job |
| --- | --- | --- |
| Teun Schulten | `purchases` — record purchases and split them into instalments | Repository and project board, PR review rules |
| Carolina Romo | `providers` — BNPL providers (Klarna, Afterpay, PayPal Pay in 3) and their rules (number of instalments, fees) | Documentation (README) and the final presentation |
| Justin Van Vuren | `schedule` — due dates, marking instalments paid, upcoming payments | Shared data model and database (`models`, `db`) |
| Adrián Bernal | `fees` — detect late payments and calculate late fees | Test setup and sample data |
| Apollo Brown | `overview` — total debt per provider and per month | Ruff, shared dependencies and CI (GitHub Actions) |
| Máximo Beras-Goico | `reminders` — alerts for instalments that are due soon or overdue | The command line that ties the modules together |

Each member owns one module, as a package under `src/bnpl/<module>/`. The package has a docstring that names the responsibility and the owner; the owner implements the domain logic, the module's database table, the FastAPI router and, later, the page. `models` is the shared data model and `db` is the shared database (Justin Van Vuren). `cli` is the command line that will call the modules (Máximo Beras-Goico). `api` is the one FastAPI application that includes every module's router.

## Conventions

This is the team's agreement for how the product is built. Follow it in every module.

### Stack

- Python 3.14 (pinned in `.python-version`) and [uv](https://docs.astral.sh/uv/)
- SQLAlchemy for the shared database. The default is a local SQLite file (`bnpl.db`). The URL is `DATABASE_URL`, so it can later be a PostgreSQL database on Azure without changing the modules.
- FastAPI for the HTTP API, run with uvicorn
- Ruff for linting, with the rules `E`, `F`, `I`, `B`, `UP` and `SIM`
- GitHub Actions runs `uv run ruff check` on pull requests and on pushes to `main`

### Package names

The application package is `bnpl`, under `src/bnpl/`.

| Package | Owner | Role |
| --- | --- | --- |
| `bnpl.purchases` | Teun Schulten | record purchases and split them into instalments |
| `bnpl.providers` | Carolina Romo | providers and their rules |
| `bnpl.schedule` | Justin Van Vuren | due dates, marking instalments paid, upcoming payments |
| `bnpl.fees` | Adrián Bernal | late payments and late fees |
| `bnpl.overview` | Apollo Brown | total debt per provider and per month |
| `bnpl.reminders` | Máximo Beras-Goico | alerts for instalments due soon or overdue |
| `bnpl.db` | Justin Van Vuren | shared connection, session and declarative base |
| `bnpl.models` | Justin Van Vuren | shared data model |
| `bnpl.api` | shared (see below) | the one FastAPI application |
| `bnpl.cli` | Máximo Beras-Goico | the command line |

`bnpl.api` is the single application the team runs. Each module adds its router there. Putting that include list in `bnpl.api` overlaps with Máximo's shared job (the interface that ties the modules together); the router of each module still belongs to that module's owner. `bnpl.db` is Justin's shared job; a minimal skeleton is only there so modules can declare their tables before the full model lands.

### API routes

Every module exposes its HTTP API under `/api/<module>/`. The two endpoints Milestone 2 requires are:

- `POST /api/<module>/` — create an item and write it to the database
- `GET /api/<module>/` — list the items already stored (read from the database)

Hard-coded data does not count. Later endpoints stay under the same prefix, for example `/api/purchases/`. Interactive docs are at `/docs` when the API is running.

### Money and dates

- **Money:** `decimal.Decimal` in Python, never `float`. In SQLite an amount is stored as a whole number of cents (an integer: `100.00` → `10000`), because SQLite has no exact decimal type. In PostgreSQL the same amounts are stored as `NUMERIC`. In the JSON API, amounts are decimal strings, for example `"100.00"`, not JSON numbers.
- **Dates:** `datetime.date` in Python and a SQL `DATE` in the database. In the JSON API, dates are ISO 8601 calendar dates, `YYYY-MM-DD`, for example `"2026-11-25"`.

## Run it

The project uses [uv](https://docs.astral.sh/uv/) and Python 3.14 (pinned in `.python-version`).

```sh
uv sync
uv run bnpl
uv run ruff check
```

`uv run bnpl` prints help. Module commands are added as each member implements their package.

Start the API from the repository root:

```sh
uv sync
uv run uvicorn bnpl.api:app --reload
```

The API is at [http://127.0.0.1:8000](http://127.0.0.1:8000), and the interactive docs are at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). To use another database, set `DATABASE_URL` before you start the server, for example `DATABASE_URL=sqlite:///bnpl.db`. The default is a SQLite file called `bnpl.db` in the folder where you run the command. That file is gitignored.

Pull requests run `uv run ruff check` (see `.github/workflows/ruff.yml`).

## Team rules

How we work in one repository. These rules match the workflow already agreed in Milestone 1, and they are now enforced on `main`.

- **Trunk-based development, not Gitflow.** There is one long-lived branch, `main`. We do not use `develop`, release branches or a second merge into `main`.
- **`main` is protected.** A ruleset named "Protect main" is active on this repository. Changes reach `main` only through a pull request. The pull request needs at least one approving review from another member. The only allowed merge method is **Create a merge commit**. Force-pushes and deleting `main` are blocked. Nobody is on the bypass list, including the repository owner.
- **A short-lived branch per task.** Start the branch from an up-to-date `main`. One branch per issue or per small task, named after the work, for example `feature/purchases`. Delete the branch after it is merged.
- **Small pull requests.** A pull request should do one thing, so it is easy to review. Each module arrives through its own reviewed pull request.
- **Every pull request is reviewed.** At least one other member reads and approves the change before it is merged. The author does not approve their own work and does not merge without that review.
- **Bring `main` in often.** While a branch is open, merge `main` into it (or rebase it onto `main`) so the branch does not drift. Merge back into `main` in small, frequent steps, not in a long-lived feature branch at the end.
- **Do not push commits directly to `main`,** and do not change history on `main`.
