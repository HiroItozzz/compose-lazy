# Compose Lazy
> 🚀 `docker compose` のCLIラッパー — インタラクティブ選択 × マルチリポジトリワークスペース管理



## 概要

`docker compose` コマンドの使用頻度の高い開発者の作業を補助するためのCLIツールです。  
よく使われるコマンドの短縮エイリアスに加え、composeファイル・プロファイル・サービス名のインタラクティブ選択や、複数リポジトリをどこからでも一括操作できるワークスペース管理機能を実装しています。    
PyPIで公開しており、`pipx install compose-lazy`または`uv tool install compose-lazy`で即座に使用できます。

## 主な機能

### 基本機能
インストールすると`dcpu`, `dcpe`, `dcp`の3コマンドが自動的にパスに追加されます。

| コマンド | 説明 |
|---|---|
| `dcpu` | `docker compose up` のエイリアス |
| `dcpe` | `docker compose exec` のエイリアス |
| `dcp` | その他サブコマンド (`build`, `logs`, `stop` など) のエイリアス |

各コマンドには複数のオプションを指定可能です。オプションの一覧は[こちら](README.md#list-of-commands)を参照してください。  


### ワークスペース機能
 
複数のリポジトリを「ワークスペース」としてまとめて登録し、一括で操作できます。
**カレントディレクトリを問わず、`cd` なしでどこからでも操作できる**のが特徴です。

登録しておけば、各リポジトリのパスと compose ファイルを compose-lazy が記憶します。
ファイルシステム上のどこにいても、任意のコンテナの起動・exec・状態確認が行えます。
 

```bash

# リポジトリを compose ファイル指定付きで登録する
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

# ワークスペース内の全リポジトリを登録済み compose ファイルで起動する
$ dcp ws up
✅️ Found 1 registered workspace!
    1. myproject
Enter your choice or 'q' to quit: 1

───── 📂 myproject ────────────────────────────────────────────────────────────────────────────────────
▷ Executing `docker compose -f docker-compose.yml up -d` in MYPROJECT.

# ワークスペース内のリポジトリ・サービスを対話的に選択して exec する
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
 
設定は `~/.config/compose-lazy` に保存されます。


### インタラクティブ機能
`-f`、`-pf`、`-s` 各オプションを付与すると、カレントディレクトリのcomposeファイルが読み込まれ、対話的に実行対象を選択できます。

```bash
$ dcpu -f
✅️ Found 2 compose files!
    1. docker-compose.yml
    2. docker-compose.prod.yml
Enter your choices (e.g., 1,3,4) or 'q' to quit: 2
▷ Executing `docker compose -f docker-compose.prod.yml up`.

$ dcp re -pf   # `re`start
✅️ Found 2 profiles!
    1. dev
    2. prod
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1
▷ Executing `docker compose --profile dev restart`.

$ dcp l -s   # `l`ogs
✅️ Found 3 services!
    1. app
    2. db
    3. frontend
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1,2
▷ Executing `docker compose logs app db`.
```

`docker compose exec/run`コマンドのエイリアスでは、サービス指定のない場合自動的に対話が始まります。

```bash
$ dcpe   # `e`xec
✅️ Found 3 services!
    1. app
    2. db
    3. frontend
Enter your choice or 'q' to quit: 1
▷ Executing `docker compose exec app bash`.
```

## 🔧 インストール

```bash
# pipx
pipx install compose-lazy

# uv
uv tool install compose-lazy
```


## コマンド一覧

（省略 — [英語版README](README.md#list-of-commands)を参照）


## 技術スタック

- **言語**: Python 3.11+
- **パッケージ管理**: uv
- **配布**: PyPI (pipx / uv tool でインストール可能)

## 工夫した点

**エントリーポイントのコマンド定義部分の可読性**

`ArgumentParser` のデフォルトの構成を利用すると、トリガーとなる引数の指定/helpメッセージ定義/ビジネスロジックの3機能が密結合かつ可読性が低くなる状態でした。  
そこで、そのラッパークラス（`ArgBuilder`）を設計しサブコマンドの定義をメソッドチェーンで実装する方式としました。これにより新しいオプションの追加を1行で見通し良く行うことができます。

```python
ArgBuilder(parser)
    .add_service_name_subcmd(multiple=True)
    .add_detach_args()
    .add_build_args()
    .add_common_compose_options()
    .set_defaults(func=Processor())
```

ビジネスロジック（インタラクティブ機能/コマンド組み立て）も別クラスに分離し、エントリーポイントのコードは引数の定義と処理の呼び出しに専念しています。

**テスト**

単体テストのほか、`sys.argv`と`subprocess.run`をモックした結合テストを実装することで品質を担保しています。約470テスト、カバレッジ99%を維持しています。


## 経緯・所感 (2026-05-18)

当初はbashエイリアスでdocker composeの短縮コマンドを利用していましたが、より高機能なものが欲しくなったのが構想のきっかけです。  
インタラクティブ機能を思いついた時点で、他の開発者にも一定程度価値があるのではないかと感じ、PyPIにアップロードする前提で今回のプロジェクトを立ち上げました。  
PyPIでの配布についてですが、その手続き自体はそこまで煩雑ではありませんでした。
他方で、修正時や機能追加の際の意図せぬ破壊的変更が起こらないよう、テストコードの網羅性に対しては大きな労力を割くことになりました。  
設計は簡明で拡張性は高いため、今後もアイデアを思いついた際には機能拡張を行っていく予定です。