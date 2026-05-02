## コマンド一覧

| bashコマンド                        | 実行されるdockerコマンド                                |
|---------------------------------|------------------------------------------------|
| dcp                             | -                                              |
| dcp up(u)                       | docker compose up                              |
| dcp up(u) -f path1 path2...     | docker compose -f path1 -f path2 up            |
| dcp build(b)                    | docker compose build                           |
| dcp build(b) -f path1 path2...  | docker compose -f path1 -f path2... build      |
| dcp exec(e) container_name      | docker compose exec container_name bash        |
| dcp exec(e) container_name bash | docker compose exec container_name bash        |
| dcp exec(e) container_name args | docker compose exec container_name args        |
| dcp restart(r)                  | docker compose restart                         |
| dcp restart(r) container_name   | docker compose restart container_name          |
| dcp ps                          | docker compose ps                              |
| dcp logs(l)                     | docker compose logs                            |
| dcp logs(l) container_name      | docker compose logs container_name             |
| dcp stop                        | docker compose stop                            |
| dcp stop container_name         | docker compose stop container_name             | 
| dcp down                        | docker compose down                            |
| dcpu                            | docker compose up                              |
| dcpu -f path1 path2...          | docker compose -f path1 -f path2... up         |
| dcpu build(b)                   | docker compose up --build                      |
| dcpu build(b) -f path1 path2... | docker compose -f path1 -f path2... up --build |
| dcpu detach(d)                  | docker compose up -d                           |
| dcpe container_name             | docker compose exec container_name bash        |
| dcpe bash container_name        | docker compose exec container_name bash        |
| dcpe container_name args        | docker compose exec container_name args        |

## ユーザー設定

| bashコマンド | 登録される設定 |
|----------|---------|
| -        | -       |

