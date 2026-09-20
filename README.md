# tecsgen (Python 版)

[TECS](https://www.toppers.jp/tecs.html)（TOPPERS Embedded Component System）のインタフェースジェネレータ **tecsgen** の Python 移植です。

隣の Ruby 版配布ルート（`../tecsgen/`）とディレクトリ構成・振る舞を揃え、生成結果の互換を目指しています。Pythonic な再設計は行わず、Ruby 版と 1:1 の対応を優先しています（詳細は [PORTING.md](PORTING.md)）。

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

## 質問・バグレポート

TOPPERS プロジェクトの慣例に従い、会員は `com-wg@toppers.jp`、その他は `users@toppers.jp` へお願いします（ML 参加が必要な場合があります）。

- [TOPPERS コミュニティ](http://www.toppers.jp/community.html)

## 現状（メモ）

- コア生成・主要プラグイン・`test/` の多くは Python 版で動作確認済みです。
- 一部テスト（ASP 依存 mruby、環境固有のリンク失敗など）はスキップまたは環境依存があります。
- `PORTING.md` の「移植しないもの」に古い記述が残っている場合は、実装状況を優先してください。
