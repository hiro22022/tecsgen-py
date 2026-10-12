# tecsgen (Python 版)

## 状態

現時点では、TECS ジェネレータ V1.9.1 に cmake 対応を付加したバージョンをベースに python 化した、試験的なものです。

AI を使用して開発しています。
make test, make test_exec が通ることまで確認していますが、make test_err で検出されるエラー個数には、差があります（[Ruby 版との相違](#ruby-版との相違) を参照）。

## 概要

[TECS](https://www.toppers.jp/tecs.html)（TOPPERS Embedded Component System）のインタフェースジェネレータ **tecsgen** の Python 移植です。

Ruby 版配布ルート（`../tecsgen/`）とディレクトリ構成・振る舞を揃え、生成結果の互換を目指しています。Pythonic な再設計は行わず、Ruby 版と 1:1 の対応を優先しています（詳細は [PORTING.md](PORTING.md)）。

| 項目 | 内容 |
| --- | --- |
| 対応 Ruby 版 | `../tecsgen/`（tecsgen 1.9.1 相当） |
| 言語 | Python 3（動作確認: 3.10） |
| パーサ | [PLY](https://www.dabeaz.com/ply/)（`tecsgen/vendor/ply` に同梱） |
| ライセンス | 各ソース先頭の TOPPERS ライセンス（`tecsgen/tecsgen.py` 冒頭を参照） |

## 必要なもの

- **Python 3**（3.8 以降を推奨）
- テストビルド時: **gcc** / **make**、必要に応じて **g++**（CPPBridge 等）
- mruby 関連テスト: 別途 mruby のビルド成果物（環境に依存）
- ASP / ASP3 依存の mruby テストは、該当パッケージがある場合のみ実行

Ruby インタプリタは実行に不要です。差分比較（`make compare`）を行う場合のみ、隣の Ruby 版 tecsgen が必要です。

## ディレクトリ構成

```
tecsgen-py/                 # 配布ルート（Ruby 版 ../tecsgen/ に対応）
  Makefile                  # テスト・比較の起動
  PORTING.md                # Ruby→Python 移植規約
  README.md                 # 本ファイル
  tecsgen/                  # ジェネレータ本体
    tecsgen                 # 起動スクリプト（python3 tecsgen.py）
    tecsgen.py
    tecsmerge / tecsmerge.py
    tecslib/
    vendor/ply/             # PLY 同梱
    tecs -> …               # ランタイム CDL 等（Ruby 版 tecs/ への symlink）
  test/                     # Ruby 版と同系統のテスト
  tools/                    # 移植・比較用スクリプト
```

`tecsgen/tecs` は Ruby 版 `../tecsgen/tecsgen/tecs` へのシンボリックリンクを想定しています（mruby / RPC / posix 等の import パス用）。

## 環境変数

ルートの `Makefile` は次を自動設定します。

| 変数 | 意味 |
| --- | --- |
| `PATH` | `tecsgen/` を先頭に追加（`tecsgen` / `tecsmerge` コマンド） |
| `TECSPATH` | `tecsgen/tecs`（プラグイン・Makefile テンプレート・import 用） |

手動で使う場合の例:

```bash
export PATH="$(pwd)/tecsgen:$PATH"
export TECSPATH="$(pwd)/tecsgen/tecs"
# 必要に応じて
export TECSGEN_LANG=C.UTF-8
```

文字コードまわりの詳細は Ruby 版 `README.txt` と同様です（`LANG` / `TECSGEN_LANG` / `TECSGEN_FILE_LANG` / `-k`）。

## 使い方

```bash
# ヘルプ
tecsgen --help

# CDL からコード生成（生成物は通常 gen/）
tecsgen hello.cdl
tecsgen -I path/to/include your.cdl
```

起動スクリプトは `tecsgen/tecsgen` です。直接 `python3 tecsgen/tecsgen.py …` でも同じです。

TECS 自体の仕様・マニュアルは次を参照してください。

- [TECS リファレンスマニュアル](http://tecs-docs.readthedocs.io/ja/latest/)
- Ruby 版配布の `doc/`（TECSInfo、HRP3 向け資料など）

## テスト・検証

利用者向けの必須手順ではありません。移植開発・回帰確認用です。

```bash
# 推奨: CLI + 主要 CDL の Ruby 差分比較
make compare

# CLI のみ（--help / --version 等）
make test_cli

# test/ 一式の生成・ビルド（時間がかかる）
make test

# ErrorCase
make test_err

# ビルド済み .exe の実行（opaque* 除外 + mruby 専用）
make test_exec

# 上記をまとめて
make allall
```

個別 CDL の Ruby 比較:

```bash
tools/diff_with_ruby.sh path/to/file.cdl
```

## Ruby 版との関係

| | Ruby 版 (`../tecsgen/`) | 本リポジトリ |
| --- | --- | --- |
| 実装言語 | Ruby | Python 3 |
| 文法フロントエンド | racc | PLY |
| ビルド | ジェネレータ本体はビルド不要 | 同様（ビルド不要） |
| プラグイン | `.rb` | `.py`（`.rb` 指定も `.py` を優先ロード） |
| tecsflow 用 dump | `tecsgen.rbdmp` | 未出力（tecsflow 連携は対象外） |

移植方針・命名対応・PLY 注意点は [PORTING.md](PORTING.md) を参照してください。

## Ruby 版との相違

CDL の文法、コマンドラインオプション、生成されるコード、エラー・警告メッセージの書式は Ruby 版と一致させることを目標にしています。以下は、現時点で判明している相違点です。

### 同梱しないツール

Ruby 版の `tecsgen/` に含まれる次のツールは移植していません。`tecsgen` と `tecsmerge` のみ提供します。

- `tecscde`（コンポーネント図エディタ）
- `tecsflow` / `tcflow`（フロー解析）
- `tecsgen_rcov`（カバレッジ計測用の起動スクリプト）
- exerb による実行形式化（`$IN_EXERB` は常に偽）

### 出力の相違

- **`tecsgen.rbdmp` を出力しません。** Ruby 版は生成後に `Marshal.dump` で `gen/tecsgen.rbdmp` を出力し、`tecsflow` が読み込みます。Python 版ではこのダンプと、その前処理である `unjoin_plugin`（Ruby 版 `tecslib/core/unjoin_plugin.rb`）を移植していません。
- 生成される `Makefile.tecsgen` には Ruby 版と同じ `tecsflow` / `tcflow` ターゲットが出力されますが、`tecsgen.rbdmp` が無いため Python 版の出力に対しては動作しません。
- `-v`（verbose）で表示する処理系情報は `ruby X.Y.Z ...` ではなく `python X.Y.Z [platform]` です。

### コマンドラインオプション

オプションの種類・書式・ヘルプ文字列は Ruby 版と同じです。ただし次の 2 つは受け付けるだけで、Ruby 版と同じ効果はありません。

- `-L` / `--library-path`: ライブラリ探索は Python の `import` で行うため、本体の探索には使いません（ユーザ定義プラグインの `.py` 探索パスには使います）。
- `-y` / `--yydebug`: racc のデバッグ用パーサ（`bnf-deb.tab.rb`）に相当するものは無く、PLY のトレースも出力しません。

### プラグイン

**ユーザ定義プラグインは Python で書き直す必要があります。** `generate(FooPlugin, "...")` 等で `FooPlugin.rb` を指定した場合、Python 版は同名の `FooPlugin.py` を探してロードします。Ruby で書かれた `.rb` を実行することはできません（例: `test/ErrorCase/MyDomainPlugin.py`、`test/CPPBridge` の `CPP2TECSBridgePlugin`）。

Ruby 版 `tecslib/plugin/` のうち、次のプラグインは未移植です。

| 分類 | 未移植のプラグイン |
| --- | --- |
| ATK1（OSEK） | `ATK1DelayTaskPlugin`, `ATK1EventPlugin` |
| C インタフェース生成 | `CIfGenPlugin`, `CIfGenCelltypePlugin`, `CIfGenCellPlugin` |
| FMP | `FMPPlugin`, `FMPHandlerPlugin`, `FMPObjectPlugin` |
| HRMP | `HRMPPlugin`, `HRMPClassPlugin`, `HRMPDomainPlugin`, `HRMPKernelObjectPlugin` |
| HRP2 | `HRP2Plugin` ほか `HRP2*` 一式、`HRP2Cache`, `HRP2PostHook` |
| HRP（HRP3） | `HRPPlugin` ほか `HRP*` 一式、`HRPKernelObjectManager` |
| ブリッジ | `TECS2CBridgePlugin` |
| `plugin/lib/` | `GenAttMod`, `GenHRP2Marshaler` |

このため、FMP / HRP2 / HRP3 / HRMP などの保護・マルチプロセッサ向けカーネルと組み合わせる CDL は、現時点では Python 版で処理できません。

逆に、Python 版にのみ含まれるプラグインは次のとおりです。

- `CPP2TECSBridgePlugin`: Ruby 版では `test/CPPBridge/` 側に置かれているものを本体に同梱
- `TransparentRPCSignaturePlugin`: `RPCPlugin` / `DataPumpHolderPlugin` から参照されるが、Ruby 版配布（`../tecsgen/`）には含まれていないもの

### エラー検出・エラーメッセージ

`test/ErrorCase` の大半のケースは、エラー数・警告数とも Ruby 版と一致します。一致しないのは次の 3 ケースで、Python 版の `test/ErrorCase/Makefile` では期待値を Python 版の値に変更しています（Ruby 版の期待値はコメントで残しています）。

| ケース | Ruby 版の期待値 | Python 版の期待値 | 原因 |
| --- | --- | --- | --- |
| `singleton-err` | 2 errors, 3 warnings | 8 errors, 3 warnings | 構文エラー後の回復処理の違い |
| `domainPlugin-err` | 3 errors | 4 errors | テスト用プラグインの実装の違い |
| `cell-err` | 7 errors, 1 warning | 6 errors, 1 warning | プラグインのロード失敗後の処理の違い |

- **構文エラーの回復**: racc と PLY ではエラー回復の挙動が異なります。Python 版は構文エラーの後、`;` までトークンを読み捨てて解析を再開するため、Ruby 版では 1 件で済む構文エラーが後続の行で連鎖的に報告されることがあります。また、構文エラー（G1016）の報告桁位置が Ruby 版と異なる場合があります（`singleton-err` では Ruby 版 62:11、Python 版 62:3）。
- **プラグインのロード失敗**: 存在しないプラグインを指定した場合、Ruby 版は `P2001 ... fail to load plugin` の後に Ruby 例外が発生して `S1166 ...: fail to new` も報告します。Python 版は例外が発生しないため、`P2001` のみを報告します。また、ロード失敗時のメッセージは Ruby 版の `Check $RUBYLIB environment variable or -L option` ではなく `plugin は未対応 (Check library path or -L option)` です。
- **`domainPlugin-err`**: テストで使う `MyDomainPlugin` が Ruby 版（`DomainPlugin` を継承するだけ）と Python 版（through プラグインを挿入し、結合を常に許可する）で異なるため、検出されるエラーの内容も異なります。ジェネレータ本体の相違ではありません。
- 一部のエラーで、報告位置の桁が Ruby 版と異なる場合があります（例: `domainPlugin-err` の S1027 は Ruby 版 22:14、Python 版 22:8）。
- ジェネレータ内部で想定外の例外が発生した場合、Ruby 版と同じ `*** Begin Ruby exception message ***` という見出しで Python の例外内容を表示します。

### その他

- ワイド文字列リテラル（`L"..."`）は Ruby 版と同様に未対応です。
- Ruby 版にある XML 出力（`tecslib/core/gen_xml.rb`）は、Ruby 版でも呼び出し箇所がコメントアウトされているため移植していません。

## 質問・バグレポート

TOPPERS プロジェクトの慣例に従い、会員は `com-wg@toppers.jp`、その他は `users@toppers.jp` へお願いします（ML 参加が必要な場合があります）。

- [TOPPERS コミュニティ](http://www.toppers.jp/community.html)

## 現状（メモ）

- コア生成・主要プラグイン・`test/` の多くは Python 版で動作確認済みです。
- 一部テスト（ASP 依存 mruby、環境固有のリンク失敗など）はスキップまたは環境依存があります。
- `PORTING.md` の「移植しないもの」に古い記述が残っている場合は、実装状況を優先してください。
