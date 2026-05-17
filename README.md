# Fast DCP
> 🚀 A smart CLI wrapper for `docker compose` — with interactive file, profile, and service selection.

## Overview
A CLI tool designed to streamline workflows for developers who frequently use `docker compose`.  
In addition to short aliases for common commands, it features auto-detection and interactive selection of compose files, profiles, and service names.  
Available on PyPI — install instantly with `pipx install fast-dcp` or `uv tool install fast-dcp`.

[日本語版README](README_ja.md)もあります。

## Highlights

### Basic Commands
Installing fast-dcp adds three commands to your PATH automatically.

| Command | Description |
|---|---|
| `dcpu` | Alias for `docker compose up` |
| `dcpe` | Alias for `docker compose exec` |
| `dcp` | Alias for other subcommands (`build`, `logs`, `stop`, etc.) |

Each command supports multiple options. See the [List of Commands](#list-of-commands) for details.

### Interactive Selection
Running `-f`, `-pf`, or `-s` without arguments auto-detects compose files, profiles, and services, letting you choose interactively.

```bash
$ dcpu -f
☑ Found 2 compose files!
    1. docker-compose.yml
    2. docker-compose.prod.yml
Enter your choices (e.g., 1,3,4) or 'q' to quit: 2
▷ Executing `docker compose -f docker-compose.prod.yml up`.

$ dcp re -pf   # `re`start
☑ Found 2 profiles!
    1. dev
    2. prod
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1
▷ Executing `docker compose --profile dev restart`.

$ dcp l -s   # `l`ogs
☑ Found 3 services!
    1. app
    2. db
    3. frontend
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1,2
▷ Executing `docker compose logs app db`.
```

For `exec`/`run`, interactive selection starts automatically when no service name is given.

```bash
$ dcpe   # `e`xec
☑ Found 3 services!
    1. app
    2. db
    3. frontend
Enter your choice or 'q' to quit: 1
▷ Executing `docker compose exec app bash`.
```


## 🔧 Install fast-dcp
### Quick Install
```bash
# Using pipx
pipx install fast-dcp
# OR using uv
uv tool install fast-dcp
```
### Not familiar with Python tooling?

If you don't have `pipx` or `uv` installed yet:

<details>
<summary>Windows</summary>

```bash
python -m pip install --user pipx
python -m pipx ensurepath
# Restart terminal, then:
pipx install fast-dcp
```
</details>

<details>
<summary>macOS</summary>

```bash
brew install pipx
pipx ensurepath
pipx install fast-dcp
```
</details>

<details>
<summary>Linux (Ubuntu/Debian)</summary>

```bash
pip install pipx
pipx ensurepath
pipx install fast-dcp
```
</details>

## Features

- **Interactive Selection**: auto-detect and interactively select compose files, profiles, and services
- **Short Aliases**: `dcp u`, `dcp b`, `dcp e` — fewer keystrokes for common commands
- **Dedicated Commands**: `dcpu` and `dcpe` for frequent up/exec workflows
- **Zero Config**: No configuration files needed — just install and run
- **Cross-Platform**: Works on Windows, macOS, and Linux

## FAQ
### Why use pipx or uv tool instead of pip?

Both `pipx` and `uv tool` install CLI tools in isolated environments, so fast-dcp won't conflict with other Python packages. The commands (`dcp`, `dcpu`, `dcpe`) are available globally without activating a virtual environment. `uv tool` is the faster alternative if you already use uv.

## Requirements

- Python 3.11+
- Docker with Compose V2 (`docker compose` — not `docker-compose`)
- A `docker-compose.yml` (or `*compose*.yml/yaml`) in the current directory for interactive selection features

## List of Commands

> **Common options** (available for all commands): `-s`, `-f FILE...`, `-pf PROFILE...`, `-p PROJECT`
>
> ⚠️ Note: `-f`, `-pf`, `-p` are passed before the subcommand in the actual docker compose syntax,  
> but in fast-dcp they are specified after the subcommand (e.g. `dcp up -f FILE`).

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

and more... see `dcp --help` for the full list of supported commands and options.

## License

MIT LICENSE