# Compose Lazy
[![image](https://img.shields.io/pypi/v/compose-lazy.svg)](https://pypi.python.org/pypi/compose-lazy)
[![image](https://img.shields.io/pypi/l/compose-lazy.svg)](https://pypi.python.org/pypi/compose-lazy)
[![image](https://img.shields.io/pypi/pyversions/compose-lazy.svg)](https://pypi.python.org/pypi/compose-lazy)
[![Test Status](https://github.com/HiroItozzz/compose-lazy/actions/workflows/test.yml/badge.svg)](https://github.com/HiroItozzz/compose-lazy/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/HiroItozzz/compose-lazy/badge.svg?branch=test/coverall)](https://coveralls.io/github/HiroItozzz/compose-lazy?branch=main)
> 🚀 `docker compose` のCLIラッパー — インタラクティブ選択 × マルチリポジトリワークスペース管理



## 概要

`docker compose` コマンドの使用頻度の高い開発者の作業を補助するためのCLIツールです。  
よく使われるコマンドの短縮エイリアスに加え、composeファイル・プロファイル・サービス名のインタラクティブ選択や、複数リポジトリをどこからでも一括操作できるワークスペース管理機能を実装しています。    
PyPIで公開しており、`pipx install compose-lazy`または`uv tool install compose-lazy`で即座に使用できます。

## おすすめの使い方

### 1. プロジェクトを登録、どのディレクトリからでも起動
通常docker composeはプロジェクトの存在するディレクトリからでなければ実行することができません。
```bash
$ docker compose up   # ユーザーHomeなど別のディレクトリで実行
no configuration file provided: not found   # いちいちcdする必要がある！
```

*Compose Lazy*では既存のプロジェクトを簡単に登録でき、一度登録されたプロジェクトは**どのディレクトリからでもコンテナをインタラクティブに起動**することを可能にします！  
また、*Compose Lazy*はあなたの代わりに**Composeファイルを自動検出し、起動オプションの選択肢を示します**。長い引数を入力する必要もなく、ユーザーは選択肢の番号を入力するだけで簡単に起動できます。
```bash
$ dcp ws reg    # または `dcp workspace register`
Please enter a new directory path: ./myproject   # プロジェクトのパスを入力
✅️ Compose file found: docker-compose.yml

Enter a new workspace name: my workspace    # 任意のワークスペース名を入力
✅️ Registered a new repo to my workspace: /path/to/projects/myproject (docker-compose.yml)
Enter 'l' to see the workspace or exit... : l   # 登録したプロジェクトを確認
───── my workspace ─────────────────────────────────────────────────────────────────────────────────
 📁 PATH[1]: /path/to/projects/myproject
      FILES: docker-compose.yml

💡 To get all workspace lists, run `dcp ws list(li)`.

$ dcp ws up   # docker compose `up` を実行
───── 📂 myproject ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
▷ Executing `docker compose -f docker-compose.yml up -d` in MYPROJECT.
```

### 2. 複数プロジェクトの一括実行
さらにこのワークスペースに複数のプロジェクトを登録すれば、`docker compose xxx`コマンドを**登録済みプロジェクトに対して一括実行**できます。
```bash
$ dcp ws reg
Please enter a new directory path: ./otherproject
✅️ Compose file found: docker-compose.yml

✅️ Found 4 registered workspaces!
    1. my workspace

 ── Or enter 0 for a new entry.
Enter your choice or 'q' to quit: 1
✅️ Registered a new repo to my workspace: /path/to/projects/otherproject (docker-compose.yml)
Enter 'l' to see the workspace or exit... : 

💡 To get all workspace lists, run `dcp ws list(li)`.

$ dcp ws up   # 複数リポジトリに対するバルクアクション

───── 📂 myproject ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
▷ Executing `docker compose -f docker-compose.yml up -d` in MYPROJECT.
...
───── 📂 otherproject ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
▷ Executing `docker compose -f docker-compose.yml up -d` in OTHERPROJECT.
...

```

workspace(ws)コマンドは `up` 以外にも`build`, `exec`, `down`, `ps`, `logs`等、多くのコマンドに対応しています。
依存はPyYAMLのみで軽量。テストコードも充実しているため、どの環境でも安心してインストールが可能です。


## 🔧 主な機能

### 基本機能
インストールすると`dcpu`, `dcpe`, `dcp`の3コマンドが自動的にパスに追加されます。

| コマンド | 説明 |
|---|---|
| `dcpu` | `docker compose up` のシンプルなエイリアス |
| `dcpe` | `docker compose exec` のシンプルなエイリアス |
| `dcp` | その他サブコマンド (`build`, `logs`, `stop` など) のエイリアスのほか、独自のワークスペース一括実行機能（`ws/workspace`） |

各コマンドには複数のオプションを指定可能です。オプションの一覧は[こちら](README.md#list-of-commands)を参照してください。  


### インタラクティブ機能
`-f`、`-pf`、`-s` 各オプションを付与すると、カレントディレクトリのcomposeファイルが読み込まれ、対話的に実行対象を選択できます。

```bash
$ dcpu -f   # ファイル選択フローを起動
✅️ Found 2 compose files!
    1. docker-compose.yml
    2. docker-compose.prod.yml
Enter your choices (e.g., 1,3,4) or 'q' to quit: 2
▷ Executing `docker compose -f docker-compose.prod.yml up`.

$ dcp re -pf   # プロフィール選択
✅️ Found 2 profiles!
    1. dev
    2. prod
Enter your choices (e.g., 1,3,4) or 'q' to quit: 1
▷ Executing `docker compose --profile dev restart`.

$ dcp l -s   # サービス選択
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


### ワークスペース機能

```bash
# リポジトリを compose ファイル指定付きで登録する（composeファイルは自動検出されます）
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


**型注釈の充実**

ty(Astral社製型チェッカー)による静的解析をパスしています。  
YAMLによる設定ファイルの構造をTypedDictで定義しているほか、@overloadやデコレータに対するParamSpecの利用など、プロダクション品質の型注釈を目指しました。

```python
# cli_utils.py
@overload
def interactive_select(
    candidates, flag=..., *, multiple=..., allow_zero: Literal[True]
) -> None | list[str]: ...
@overload
def interactive_select(
    candidates, flag=..., *, multiple=..., allow_zero: Literal[False] = False
) -> list[str]: ...
```

**テスト**

単体テストのほか、`sys.argv`と`subprocess.run`をモックした結合テストを実装することで品質を担保しています。テストケース400超、カバレッジは99%を維持しています。


## 経緯・所感

Dockerについては同様の便利なOSSアプリケーションがある一方で、docker composeを扱うアプリケーションはネット上でも見当たらなかったことが開発の動機です。  
PyPIでの配布にあたっては、業務での使用にも耐えられる品質を目指しました。  
テストの網羅性に大きな労力を払った結果、修正時の意図せぬ破壊的変更を自覚できる状態となっており、プロダクション品質のソフトウェアを安定的に運用する方法がどのようなものかを体得できたことがこのプロジェクトでの大きな収穫です。

またv1.0.0では、依存ライブラリをPyYAMLのみに留めています。これはユーザーの環境への影響を最小化する目的に加え、Pythonの基本的仕様への理解を深める意図によるものでした。  
結果、argparseやsubprocessといった重要な標準ライブラリの実装のあり方を知ることができ、サードパーティのOSSライブラリが存在する理由や、今後外部依存を利用する際の判断基準を自分の中で築くことが出来ました。
