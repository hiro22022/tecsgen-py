# tecsgen Ruby 版から Python 版への移植規約

隣の Ruby 配布ルート (`../tecsgen/`) と同じく、本体は `tecsgen/`、テストは `test/` に置く。
ジェネレータ本体は Ruby 版 `../tecsgen/tecsgen/` と 1:1 の対応を保つことを優先する。
Pythonic な再設計はしない。ファイル構成・クラス名・メソッド名・処理順序を Ruby 版に対応させ、
日本語コメントも原則そのまま残す。

## ディレクトリ構成

```
tecsgen-py/                 # ← ../tecsgen/ に対応（配布ルート）
  Makefile                  # テスト起動（Ruby 版トップ Makefile 相当）
  PORTING.md
  tecsgen/                  # ← ../tecsgen/tecsgen/ に対応（ジェネレータ本体）
    tecsgen                 # 起動スクリプト
    tecsgen.py              # ← tecsgen.rb
    tecslib/
    vendor/                 # PLY 同梱（Python のみ）
    tecs -> ...             # Ruby 版 tecs/ へのシンボリックリンク
  test/                     # ← ../tecsgen/test/ を配置（CDL・Makefile 等）
    Makefile                # Ruby 版と同じビルド／実行テスト
    Makefile.compare        # Python↔Ruby 差分比較用
  tools/                    # 移植補助（racc_to_ply、diff_with_ruby 等）
```

## ファイル対応

| Ruby | Python |
| --- | --- |
| `tecsgen/tecsgen.rb` | `tecsgen/tecsgen.py` |
| `tecsgen/tecslib/version.rb` | `tecsgen/tecslib/version.py` |
| `tecsgen/tecslib/core/xxx.rb` | `tecsgen/tecslib/core/xxx.py` |
| `tecsgen/tecslib/core/componentobj/xxx.rb` | `tecsgen/tecslib/core/componentobj/xxx.py` |
| `tecsgen/tecslib/core/syntaxobj/xxx.rb` | `tecsgen/tecslib/core/syntaxobj/xxx.py` |
| `tecsgen/tecslib/messages/xxx.rb` | `tecsgen/tecslib/messages/xxx.py` (`tools/convert_messages.rb` が生成) |
| `test/` | `test/` |

Ruby 版のどのファイルにも対応しない移植用の補助モジュールは `tecsgen/tecslib/rubylib/` に置く。

## 命名

- インスタンス変数 `@x` → `self.x`。メソッド名と衝突する場合は `_x` とする
  （例: `@generate` → `self._generate`。Ruby では ivar と method が別名前空間だが Python では衝突する）
- クラス変数 `@@x` → クラス属性 `x`。メソッド名と衝突する場合だけ `_x` とする
- 述語メソッド `foo?` → `foo`。`is_` が付いていないものはそのまま (`need_PPAllocator?` → `need_PPAllocator`)
- 破壊的メソッド `foo!` → `foo_bang`
- Ruby のクラスメソッドとインスタンスメソッドが同名の場合 (`TECSGEN.new_cell_location`)、
  インスタンス側に `_inst` を付ける
- グローバル変数 `$x` → `tecslib/core/globals.py` の属性。`from tecslib.core import globals as G` して `G.x`

## 型と値

- `nil` → `None`
- Ruby の Symbol → `tecslib.rubylib.symbol.Sym` (`str` のサブクラス)。
  識別子など String と区別が必要なものだけ `Sym` にする。
  `:VAR` のような内部的な列挙値は素の `str` でよい (`Sym` は `str` と等しく比較される)
- `"#{obj}"` で nil が空文字列になる箇所は `tecslib.rubylib.rb.to_s` を使う
- `obj.instance_of?(X)` → `type(obj) is X`
- `obj.kind_of?(X)` / `obj.is_a?(X)` → `isinstance(obj, X)`
- `obj.class.name` → `obj.__class__.__name__`
- `obj.clone` → `copy.copy(obj)`
- `array.uniq` → `tecslib.rubylib.rb.uniq` (出現順を保つ)
- Ruby は `if` の中で代入した局所変数も外側で `nil` として参照できる。
  Python では手前で `None` に初期化しておく

## 出力

- `puts x` → `print(x)`、`print x` → `print(x, end="")`
- `indent.times { print "  " }` → `print("  " * indent, end="")`
- `STDERR <<` → `sys.stderr.write(...)`
- エラー・警告の書式は Ruby 版と完全一致させる。差分テストの精度がここに依存する

## import

- 循環 import を避けるため、相互参照するクラスはメソッドの中で import する
- Ruby のクラス再オープン (`generate.rb` が `Celltype` にメソッドを追加するなど) は
  `tecslib.rubylib.reopen.reopen` を使う

```python
@reopen(Celltype)
class _:
    def generate(self):
        ...
```

## 移植しないもの

- plugin (`tecslib/plugin/`) — 後のフェーズで対応する
- `tecscde`, `tecsflow`, `tecsmerge`
- exerb 対応 (`$IN_EXERB`)
- `tecsgen.rbdmp` の出力 (`Marshal.dump`)。消費側の tecsflow が対象外のため

## 検証

```
make compare                   # CLI + 主要 CDL の Ruby 差分比較（推奨）
make test_cli                  # オプション解析のみ
make test                      # test/Makefile を Python tecsgen で実行
tools/diff_with_ruby.sh X.cdl  # 個別 CDL 比較（test/ または任意パス）
```

`tecsgen/tecs` は Ruby 版 `../tecsgen/tecsgen/tecs` へのシンボリックリンクを想定する
（デフォルト import パスに mruby/posix 等のサブディレクトリを載せるため）。

`tecsgen.rbdmp` は未移植のため `diff_with_ruby.sh` では比較対象外。

## PLY / 文法まわりの注意

- racc は unit 規則 `spec_L : '['` を lookahead 前に還元できるが、PLY は `[` の次トークンを先に読む。
  そのため `in` / `size_is` 等の RESERVED2 は `next_token` で「直前が `[`」のときも認識する
  （`_bnf_runtime.Generator._prev_was_lbrack`）。
- PLY は還元前に必ず lookahead を取るため、`current_locale` が次トークンになる。
  Generator / C_parser とも `next_token` で `_last_token_locale` により 1 トークン遅らせ、
  racc の default reduce（直前トークン位置のまま）に合わせる。
  これにより構文解析中の warning/error 列、および `sizeof` の I9999 列が一致する。
  `end_of_parse` 等では加えて `Generator.set_locale_from_token(p[n])` で RHS の `;` / `}` に戻す。
  `Cell` は celltype 名還元時に生成されるため、遅延 locale 下では celltype 位置になる。
  `Cell.set_name` で `current_locale`（cell 名）へ更新し W1007 等を合わせる。
- PLY は `p[0]` 未設定だと `None` になる。racc の default result（`val[0]`）相当を明示すること
  （例: `var_declaration`、`init_declarator`）。
- Ruby の `Array#[]=` は自動拡張するが Python の list はしない。`Join.add_array_member` などで伸ばす。
- `f.printf` は `%` 書式。C の `{` / `.format` 風 `{}` を混ぜない（呼び口配列の VDES 出力など）。
- Ruby の `obj.get_celltype`（括弧省略）を `get_celltype()()` にしない。
- Ruby で真となる添数 `0` を Python の `if not subscript` で落とさない（`is None` で判定）。
- `Token` を名前にするときは `.to_sym()` / `.val`（`Sym(Token)` は不可）。
- `BaseVal` は `__str__` → `to_s()`（Ruby の `"#{IntegerVal}"` 相当）。
- 空の `domain_class_roots = {}` では Ruby 同様 `keys=[]` → `has_domain?` が真
  （`if not dct` で `[generating_region]` に差し替えない）。
- C_parser の `set_no_type_name` も PLY lookahead の影響を受ける。対策:
  - `TYPE_NAME` 化直後に `set_no_type_name(True)`（`typedef Old New` で New が型に飲み込まれないように）
  - 組み込み型トークン（`INT` 等）返却時にも `set_no_type_name(True)`
    （還元前 lookahead で既登録名が `TYPE_NAME` 化され、`typedef int __pid_t` 再定義が壊れるのを防ぐ）
  - struct 本体内は直前が `{` / `;` なら `no_type_name` を下ろす
  - `direct_declarator : TYPE_NAME`（typedef 再定義）
  - Ruby の `CompositeCelltype.find`（クラス／インスタンス同名）は
    `find_in_current` / `find` に分離する
- Ruby はメソッドの最後の式が戻り値。クラスメソッドの `return` を落とさない
  （例: `CompositeCelltype.new_join`）。
- Ruby のクラス／インスタンス同名メソッドは Python でクラスメソッドがインスタンスを隠す。
  呼び出し側は `*_inst` を明示する（例: `find_one_inst`）。
  `Region.end_of_parse` クラスメソッドは `Namespace#end_of_parse` を隠すため `pop_inst` を直接呼ぶ。
- PLY は racc と違い default reduce で `p[0]=p[1]` にならない。
  `parameter_list` の連結など、`p[1].add_param` 後に `p[0]=p[1]` が必要。
- 空規則のコメント（`# 空` / `# 空行`）を RHS トークンにしない（`empty` にする）。
- `statement : error` は racc のエラー回復用。PLY では `p_error` で `;` まで破棄し
  `parser.errok()` しないと、error 還元がトークンを消費せず無限ループする。
- `re.sub` の置換 `"\\1#{x}"` は、`x` が数字始まりだとグループ参照になる。
  `lambda m: m.group(1) + str(x)` を使う。
- Ruby の `printf("%d", "100")` は数字文字列を整数化する。`AppFile.printf` も同様に揃える。
- `StringVal.val` は Ruby ではメソッドだが、他の Val の `@val` 属性と揃えて `@property` にする。
