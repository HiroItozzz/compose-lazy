# Fast DCP
> A smart CLI wrapper for `docker compose` — with interactive file, profile, and service selection.

## Highlights

**Interactive file, profile & service selection**

Running `-f`, `-pf`, or `-s` without arguments auto-detects compose files, profiles, and services, letting you choose interactively.

```bash
$ dcpu -f
☑ Found 2 docker-compose files!
    1. docker-compose.yml
    2. docker-compose.prod.yml
Enter your choices (e.g., 1,3,4) or 'q' to quit:

$ dcpu -pf
☑ Found 2 profiles!
    1. dev
    2. prod
Enter your choices (e.g., 1,3,4) or 'q' to quit:

$ dcpu -s
☑ Found 3 services!
    1. db
    2. frontend
    3. app
Enter your choices (e.g., 1,3,4) or 'q' to quit:
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
| dcp exec(e) [SERVICE] [COMMANDS...]  | docker compose exec SERVICE bash [COMMANDS...]           |
| dcp run [SERVICE]                    | docker compose run SERVICE bash                          |
| dcp restart(re) [SERVICE...]         | docker compose restart [SERVICE...]                      |
| dcp ps [SERVICE...] [-a] [-st STATUS]| docker compose ps [SERVICE...] [--all] [--status ...]    |
| dcp logs(l) [SERVICE...] [-fo]       | docker compose logs [SERVICE...] [-f]                    |
| dcp stop(s) [SERVICE...]             | docker compose stop [SERVICE...]                         |
| dcp down [-ro]                       | docker compose down [--remove-orphans]                   |

and more... see `dcp --help` for the full list of supported commands and options.

## License

MIT LICENSE