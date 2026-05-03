# fast-dcp

A CLI tool that provides shorthand aliases for common `docker compose` commands.

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
| dcp restart(r)                            | docker compose restart                            |
| dcp restart(r) container_name             | docker compose restart container_name             |
| dcp ps                                    | docker compose ps                                 |
| dcp logs(l)                               | docker compose logs                               |
| dcp logs(l) container_name                | docker compose logs container_name                |
| dcp logs(l) container_name -F             | docker compose logs container_name -f             |
| dcp stop                                  | docker compose stop                               |
| dcp stop container_name                   | docker compose stop container_name                | 
| dcp down                                  | docker compose down                               |
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