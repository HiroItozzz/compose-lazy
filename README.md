# Compose Lazy
> 🚀 A smart `docker compose` wrapper — interactive selection × multi-repository workspace management



## Overview
A CLI tool designed to streamline workflows for developers who frequently use `docker compose`.  
In addition to short aliases for common commands, it features interactive selection of compose files, profiles, and services, and a workspace system that lets you operate any registered repository from anywhere in the filesystem — no `cd` required.  
Available on PyPI — install instantly with `pipx install compose-lazy` or `uv tool install compose-lazy`.

[日本語版README](README_ja.md)もあります。

## Highlights

### Basic Commands
Installing compose-lazy adds three commands to your PATH automatically.

| Command | Description |
|---|---|
| `dcpu` | Alias for `docker compose up` |
| `dcpe` | Alias for `docker compose exec` |
| `dcp` | Alias for other subcommands (`build`, `logs`, `stop`, etc.) |

Each command supports multiple options. See the [List of Commands](#list-of-commands) for details.

### Multi-Repo Workspace
Register named groups of repositories as a *workspace* and operate all of them at once —
**from any directory, without `cd`**.

Once registered, compose-lazy remembers each repository's path and compose files.
You can launch, exec into, or check the status of any container regardless of where you currently are in the filesystem.

```bash
# Register a repository with specific compose files
$ dcp ws register
Please enter a new directory path: /path/to/repo
✅️ Found 2 docker-compose files!
    1. docker-compose.yml
    2. docker-compose.prod.yml
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1

✅️ Found 1 registered workspace!
    1. myproject
Or '0' for a new entry.
Enter your choice or 'q' to quit: 0
Please enter a new workspace name: myproject

✅️ Registered new path to myproject: /path/to/repo (docker-compose.yml)

# Launch all repos in a workspace with their registered compose files
$ dcp ws up
✅️ Found 1 registered workspace!
    1. myproject
Enter your choice or 'q' to quit: 1

───── 📂 myproject ────────────────────────────────────────────────────────────────────────────────────
▷ Executing `docker compose -f docker-compose.yml up -d` in MYPROJECT.

# Exec into a service in a selected repo interactively
$ dcp ws exec
✅️ Found 2 repositories!
    1. /path/to/repo-a
    2. /path/to/repo-b
Enter your choice or 'q' to quit: 1

✅️ Found 2 services!
    1. app
    2. db
Enter your choice or 'q' to quit: 1
Please enter the rest of `docker compose exec app ...`: bash
▷ Executing `docker compose -f docker-compose.yml exec app bash` in REPO-A.
```

Workspace configuration is stored in `~/.config/compose-lazy`.

### Interactive Selection
Running `-f`, `-pf`, or `-s` without arguments auto-detects compose files, profiles, and services, letting you choose interactively.

```bash
$ dcpu -f   # Run compose file selection
✅️ Found 2 compose files!
    1. docker-compose.yml
    2. docker-compose.prod.yml
Enter your choices (e.g., 1,3,4) or 'q' to quit: 2
▷ Executing `docker compose -f docker-compose.prod.yml up`.

$ dcp re -pf   # Run profile selection
✅️ Found 2 profiles!
    1. dev
    2. prod
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1
▷ Executing `docker compose --profile dev restart`.

$ dcp l -s   # Run `s`ervice selection
✅️ Found 3 services!
    1. app
    2. db
    3. frontend
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1,2
▷ Executing `docker compose logs app db`.
```

For `exec`/`run`, interactive selection starts automatically when no service name is given.

```bash
$ dcpe   # `e`xec
✅️ Found 3 services!
    1. app
    2. db
    3. frontend
Enter your choice or 'q' to quit: 1
▷ Executing `docker compose exec app bash`.
```


## 🔧 Install compose-lazy
### Quick Install
```bash
# Using pipx
pipx install compose-lazy
# OR using uv
uv tool install compose-lazy
```
### Not familiar with Python tooling?

If you don't have `pipx` or `uv` installed yet:

<details>
<summary>Windows</summary>

```bash
python -m pip install --user pipx
python -m pipx ensurepath
# Restart terminal, then:
pipx install compose-lazy
```
</details>

<details>
<summary>macOS</summary>

```bash
brew install pipx
pipx ensurepath
pipx install compose-lazy
```
</details>

<details>
<summary>Linux (Ubuntu/Debian)</summary>

```bash
pip install pipx
pipx ensurepath
pipx install compose-lazy
```
</details>

## Features

- **Interactive Selection**: auto-detect and interactively select compose files, profiles, and services
- **Multi-Repo Workspace**: run docker compose commands across multiple repositories at once with `dcp ws`
- **Location-Independent**: operate any registered repository from anywhere — no need to `cd` into the project directory
- **Short Aliases**: `dcp u`, `dcp b`, `dcp e` — fewer keystrokes for common commands
- **Dedicated Commands**: `dcpu` and `dcpe` for frequent up/exec workflows
- **Cross-Platform**: Works on Windows, macOS, and Linux

## FAQ
### Why use pipx or uv tool instead of pip?

Both `pipx` and `uv tool` install CLI tools in isolated environments, so compose-lazy won't conflict with other Python packages. The commands (`dcp`, `dcpu`, `dcpe`) are available globally without activating a virtual environment. `uv tool` is the faster alternative if you already use uv.

## Requirements

- Python 3.11+
- Docker with Compose V2 (`docker compose` — not `docker-compose`)
- A `docker-compose.yml` (or `*compose*.yml/yaml`) in the current directory for interactive selection features

## List of Commands

> **Common options** (available for all commands): `-s`, `-f FILE...`, `-pf PROFILE...`, `-p PROJECT`
>
> ⚠️ Note: `-f`, `-pf`, `-p` are passed before the subcommand in the actual docker compose syntax,  
> but in compose-lazy they are specified after the subcommand (e.g. `dcp up -f FILE`).

| Bash Command                         | Executed Docker Command                                  |
|--------------------------------------|----------------------------------------------------------|
| dcp                                  | - (Show help)                                            |
| dcpu [SERVICE...] [-d] [-b] [-w]     | docker compose up [SERVICE...]                           |
| dcpe [SERVICE]                       | docker compose exec SERVICE bash                         |
| dcpe [SERVICE] [COMMANDS...]         | docker compose exec SERVICE [COMMANDS...]                |
| dcp up(u) [SERVICE...]               | docker compose up [SERVICE...]                           |
| dcp up(u) -d                         | docker compose up -d                                     |
| dcp up(u) -b                         | docker compose up --build                                |
| dcp up(u) -w                         | docker compose up --wait                                 |
| dcp build(b) [SERVICE...]            | docker compose build [SERVICE...]                        |
| dcp exec(e) [SERVICE]                | docker compose exec SERVICE bash                         |
| dcp exec(e) [SERVICE] [COMMANDS...]  | docker compose exec SERVICE [COMMANDS...]           |
| dcp run [SERVICE]                    | docker compose run SERVICE bash                          |
| dcp restart(re) [SERVICE...]         | docker compose restart [SERVICE...]                      |
| dcp ps [SERVICE...] [-a] [-st STATUS]| docker compose ps [SERVICE...] [--all] [--status ...]    |
| dcp logs(l) [SERVICE...] [-fo]       | docker compose logs [SERVICE...] [-f]                    |
| dcp stop(s) [SERVICE...]             | docker compose stop [SERVICE...]                         |
| dcp down [-ro]                       | docker compose down [--remove-orphans]                   |
| dcp workspace(ws) register(reg)      | Register a new repo to a workspace interactively         |
| dcp workspace(ws) delete(del)        | Delete a repo from a workspace interactively             |
| dcp workspace(ws) list(li)           | List all registered workspaces                           |
| dcp workspace(ws) up(u)              | docker compose up -d for each repo in a workspace        |
| dcp workspace(ws) build(b)           | docker compose build for each repo in a workspace        |
| dcp workspace(ws) exec(e)            | docker compose exec interactively for a selected repo    |
| dcp workspace(ws) logs(lo)           | docker compose logs interactively for a selected repo    |
| dcp workspace(ws) restart(re)        | docker compose restart for each repo in a workspace      |
| dcp workspace(ws) ps                 | docker compose ps for each repo in a workspace           |
| dcp workspace(ws) stop(s)            | docker compose stop for each repo in a workspace         |
| dcp workspace(ws) down               | docker compose down for each repo in a workspace         |

and more... see `dcp --help` for the full list of supported commands and options.

## License

MIT LICENSE