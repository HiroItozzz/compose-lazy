# Fast DCP
> 🚀 A CLI tool that provides shorthand aliases for common `docker compose` commands.

## 🐳 Tired of Typing `docker compose` Every Time?

How many times have you typed `docker compose up --build` today?
Fast DCP cuts it down to `dcpu -b` — same result, a fraction of the keystrokes.

## 🆕 Highlights

**Interactive file & profile selection**

Running `-f` or `-pf` without arguments auto-detects compose files and profiles, letting you choose interactively.

```bash
$ dcpu -f
☑ Found 2 docker-compose files!
    1. docker-compose.yml
    2. docker-compose.prod.yml
Enter your choices (e.g., 1,3,4) or 'Q' to quit:

$ dcpu -pf
☑ Found 2 profiles!
    1. dev
    2. prod
Enter your choices (e.g., 1,3,4) or 'Q' to quit:
```

**`--wait` option**

```bash
# Block until all services are healthy
dcpu -w
```

## Sample Usage
```bash
# docker compose up --build
dcpu -b
# docker compose -f docker-compose.prod.yml up -d
dcpu -df docker-compose.prod.yml
# docker compose exec app bash
dcpe app
# docker compose exec db psql -U user -d mydb
dcpe db -- psql -U user -d mydb
# docker compose restart app
dcp re app
```

## Install fast-dcp
### Quick Install (Recommended)
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

## ✨ Features

- **Short Aliases**: `dcp u`, `dcp b`, `dcp e` — fewer keystrokes for common commands
- **Dedicated Commands**: `dcpu` and `dcpe` for frequent up/exec workflows
- **Zero Config**: No configuration files needed — just install and run
- **Cross-Platform**: Works on Windows, macOS, and Linux

## ❓ FAQ
### Why use pipx or uv tool instead of pip?

Both `pipx` and `uv tool` install CLI tools in isolated environments, so fast-dcp won't conflict with other Python packages. The commands (`dcp`, `dcpu`, `dcpe`) are available globally without activating a virtual environment. `uv tool` is the faster alternative if you already use uv.

## 🔧 Requirements

- Python 3.11+
- Docker with Compose V2 (`docker compose` — not `docker-compose`)


## List of Commands

> **Common options** (available for all commands): `-f FILE...`, `-pf PROFILE...`, `-p PROJECT`
>
> ⚠️ Note: `-f`, `-pf`, `-p` are passed before the subcommand in the actual docker compose syntax,  
> but in fast-dcp they are specified after the subcommand (e.g. `dcp up -f FILE`).

| Bash Command                              | Executed Docker Command                                  |
|-------------------------------------------|----------------------------------------------------------|
| dcp                                       | - (Show help)                                            |
| dcp up(u) [CONTAINER...]                  | docker compose up [CONTAINER...]                         |
| dcp up(u) -d                              | docker compose up -d                                     |
| dcp up(u) -b                              | docker compose up --build                                |
| dcp up(u) -w                              | docker compose up --wait                                 |
| dcp build(b) [CONTAINER...]               | docker compose build [CONTAINER...]                      |
| dcp exec(e) CONTAINER [CMD...]            | docker compose exec CONTAINER [CMD...]                   |
| dcp run CONTAINER [CMD...]                | docker compose run CONTAINER [CMD...]                    |
| dcp restart(re) [CONTAINER...]            | docker compose restart [CONTAINER...]                    |
| dcp ps [CONTAINER...] [-a] [-st STATUS]   | docker compose ps [CONTAINER...] [--all] [--status ...]  |
| dcp logs(l) [CONTAINER...] [-fo]           | docker compose logs [CONTAINER...] [-f]                  |
| dcp stop(s) [CONTAINER...]                | docker compose stop [CONTAINER...]                       |
| dcp down [-ro]                            | docker compose down [--remove-orphans]                   |
| dcpu [CONTAINER...] [-d] [-b] [-w]        | docker compose up [CONTAINER...]                         |
| dcpe CONTAINER [CMD...]                   | docker compose exec CONTAINER [CMD...]                   |

## License

MIT LICENSE