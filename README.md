# seds-celestia-assignments-2026

The Solutions to the Assigments for SEDS Celestia Simulations made by me.

| Week | Folder | Topic |
|---|---|---|
| 1 | [`week_1/`](./week_1/) | Bouncing balls: rigid bodies, semi-implicit Euler, collisions |
| 2 | [`week2/`](./week2/) | The Sandbox: falling-sand cellular automaton |

## Setup

Everything runs on Python 3.12 with `numpy` and `pygame`. The environment is
managed by [uv](https://docs.astral.sh/uv/); it creates `.venv/` and installs
the pinned versions from `uv.lock` the first time you run anything.

```
uv sync
```

Run any week's script through `uv run` so it picks up the project venv rather
than whatever `python` happens to be on your PATH:

```
uv run python week_1/main.py
uv run python week_1/bouncingball_sarthak.py
uv run python week2/temp.py
```

If you would rather activate the venv once per terminal:

```
.venv\Scripts\Activate.ps1      # PowerShell
python week2/temp.py
```

`.venv/` and `__pycache__/` are ignored by git; `pyproject.toml`,
`uv.lock` and `.python-version` are committed so the setup travels with the
repo.
