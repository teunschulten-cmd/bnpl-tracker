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

Each member's module is one file in `src/bnpl/`. The file has a docstring that names the responsibility and the owner; the owner implements it. `models.py` is the shared data model (Justin Van Vuren). `cli.py` is the command line that will call the modules (Máximo Beras-Goico).

## Run it

The project uses [uv](https://docs.astral.sh/uv/) and Python 3.14 (pinned in `.python-version`).

```sh
uv run bnpl
uv run ruff check
```

`uv run bnpl` prints help. Module commands are added as each member implements their file.

Pull requests run `uv run ruff check` (see `.github/workflows/ruff.yml`).

## Team workflow

- One branch per issue. Do the work for that issue on its branch.
- Every change reaches `main` through a pull request.
- At least one teammate reviews the pull request before it is merged.
- Merge with a merge commit (on GitHub: **Create a merge commit**).
