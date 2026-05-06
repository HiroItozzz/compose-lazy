# Fast DCP
> 🚀 A CLI tool that provides shorthand aliases for common `docker compose` commands.

## 🐳 Tired of Typing `docker compose` Every Time?

How many times have you typed `docker compose up --build` today?
Fast DCP cuts it down to `dcpu -b` — same result, a fraction of the keystrokes.

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
dcp r app
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

| Bash Command                              | Executed Docker Command                           |
|-------------------------------------------|---------------------------------------------------|
| dcp                                       | -                                                 |
| dcp up(u)                                 | docker compose up                                 |
| dcp up(u) container_name                  | docker compose up container_name                  |
| dcp up(u) -f path1 path2...               | docker compose -f path1 -f path2 up               |
| dcp up(u) -p project_name...              | docker compose -p project_name up                 |
| dcp up(u) -d                              | docker compose up -d                              |
| dcp build(b)                              | docker compose build                              |
| dcp build(b) container_name               | docker compose build container_name               |
| dcp build(b) -f path1 path2...            | docker compose -f path1 -f path2... build         |
| dcp build(b) -p project_name...           | docker compose -p project_name build              |
| dcp exec(e) container_name                | docker compose exec container_name bash           |
| dcp exec(e) container_name bash           | docker compose exec container_name bash           |
| dcp exec(e) container_name args1 args2... | docker compose exec container_name args1 args2... |
| dcp run(R) container_name bash            | docker compose run container_name bash            |
| dcp run(R) container_name args1 args2...  | docker compose run container_name args1 args2...  |
| dcp restart(r)                            | docker compose restart                            |
| dcp restart(r) container_name             | docker compose restart container_name             |
| dcp ps                                    | docker compose ps                                 |
| dcp ps -a                                 | docker compose ps --all                           |
| dcp ps -st running                        | docker compose ps --status running                |
| dcp logs(l)                               | docker compose logs                               |
| dcp logs(l) container_name                | docker compose logs container_name                |
| dcp logs(l) container_name -F             | docker compose logs container_name -f             |
| dcp stop                                  | docker compose stop                               |
| dcp stop container_name                   | docker compose stop container_name                | 
| dcp down                                  | docker compose down                               |
| dcp down -ro                              | docker compose down --remove_orphans              |
| dcpu                                      | docker compose up                                 |
| dcpu -f path1 path2...                    | docker compose -f path1 -f path2... up            |
| dcpu -p project_name...                   | docker compose -p project_name up                 |
| dcpu --build(-b)                          | docker compose up --build                         |
| dcpu --build(-b) -f path1 path2...        | docker compose -f path1 -f path2... up --build    |
| dcpu --detach(-d)                         | docker compose up -d                              |
| dcpe container_name                       | docker compose exec container_name bash           |
| dcpe container_name bash                  | docker compose exec container_name bash           |
| dcpe container_name args1 args2 ...       | docker compose exec container_name args1 args2... |

## License

MIT LICENSE