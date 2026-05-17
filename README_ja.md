# Fast DCP
> 🚀 `docker compose` をインタラクティブに操作できるCLIラッパー

## 概要

`docker compose` コマンドの使用頻度の高い開発者の作業を補助するためのCLIツールです。  
よく使われるコマンドの短縮エイリアスに加え、composeファイル・プロファイル・サービス名を自動検出しインタラクティブに選択できる機能を実装しています。  
PyPIで公開しており、`pipx install fast-dcp`または`uv tool install fast-dcp`で即座に使用できます。

## 主な機能

### 基本機能
インストールすると`dcpu`, `dcpe`, `dcp`の3コマンドが自動的にパスに追加されます。

| コマンド | 説明 |
|---|---|
| `dcpu` | `docker compose up` のエイリアス |
| `dcpe` | `docker compose exec` のエイリアス |
| `dcp` | その他サブコマンド (`build`, `logs`, `stop` など) のエイリアス |

各コマンドには複数のオプションを指定可能です。オプションの一覧は[こちら](README.md#list-of-commands)を参照してください。  

### インタラクティブ機能
`-f`、`-pf`、`-s` 各オプションを付与すると、カレントディレクトリのcomposeファイルが読み込まれ、対話的に実行対象を選択できます。

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

`docker compose exec/run`コマンドのエイリアスでは、サービス指定のない場合自動的に対話が始まります。

```bash
$ dcpe   # `e`xec
☑ Found 3 services!
    1. app
    2. db
    3. frontend
Enter your choice or 'q' to quit: 1
▷ Executing `docker compose exec app bash`.
```


## 🔧 インストール

```bash
# pipx
pipx install fast-dcp

# uv
uv tool install fast-dcp
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

単体テストのほか、`sys.argv`と`subprocess.run`をモックした結合テストを実装することで品質を担保しています。約350テスト、カバレッジ99%を維持しています。


## 感想 (2026-05-18)

当初はbashエイリアスでdocker composeの短縮コマンドを利用していましたが、より高機能なものが欲しくなったのが構想のきっかけです。  
インタラクティブ機能を思いついた時点で、他の開発者にも一定程度価値があるのではないかと感じ、PyPIにアップロードする前提で今回のプロジェクトを立ち上げました。  
PyPIでの配布についてですが、その手続き自体はそこまで煩雑ではありませんでした。
他方で、修正時や機能追加の際の意図せぬ破壊的変更が起こらないよう、テストコードの網羅性に対しては大きな労力を割くことになりました。  
設計は簡明で拡張性は高いため、今後もアイデアが思いついた際には機能拡張を行っていく予定です。

日頃当たり前に使用しているCLIアプリケーションの裏側を知ることができ良い経験になりました。  
現在はインストールにpipxかuvが必要であり使用できる層は限られてしまっているため、将来的に別言語でのバイナリ形式での配布を行えればと考えています。