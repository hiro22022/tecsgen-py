#!/bin/sh
#
#  TECS Generator (Python port)
#      Generator for TOPPERS Embedded Component System
#
#   Copyright (C) 2008-2021 by TOPPERS Project TECS WG
#
#   ライセンスは tecsgen.py の冒頭を参照のこと．
#
#= Ruby 版 tecsgen と Python 版の出力を比較する
#
#  使い方:
#    tools/diff_with_ruby.sh [tecsgen のオプション] <CDL ファイル>
#
#  カレントディレクトリに gen_rb と gen_py を作り，生成物と標準出力・標準エラー出力を
#  比較する．差分がなければ終了コード 0．

set -u

here=$(cd "$(dirname "$0")/.." && pwd)
ruby_tecsgen=$here/../tecsgen/tecsgen/tecsgen.rb
py_tecsgen=$here/tecsgen/tecsgen.py

if [ ! -f "$ruby_tecsgen" ]; then
    echo "Ruby 版が見つからない: $ruby_tecsgen" >&2
    exit 2
fi

rm -rf gen_rb gen_py
mkdir -p gen_rb gen_py

ruby   "$ruby_tecsgen" -g gen_rb "$@" > gen_rb.out 2> gen_rb.err
rb_rc=$?
python3 "$py_tecsgen"  -g gen_py "$@" > gen_py.out 2> gen_py.err
py_rc=$?

rc=0

if [ "$rb_rc" != "$py_rc" ]; then
    echo "終了コードが異なる: ruby=$rb_rc python=$py_rc"
    rc=1
fi

# 標準出力・標準エラー出力の比較 (ファイル名に含まれる gen ディレクトリ名は読み替える)
sed 's/gen_rb/GEN/g' gen_rb.out > gen_rb.out.norm
sed 's/gen_py/GEN/g' gen_py.out > gen_py.out.norm
if ! diff -u gen_rb.out.norm gen_py.out.norm; then
    echo "標準出力に差分あり"
    rc=1
fi

sed 's/gen_rb/GEN/g; s/tecsgen\.rb/TECSGEN/g' gen_rb.err > gen_rb.err.norm
sed 's/gen_py/GEN/g; s/tecsgen\.py/TECSGEN/g' gen_py.err > gen_py.err.norm
if ! diff -u gen_rb.err.norm gen_py.err.norm; then
    echo "標準エラー出力に差分あり"
    rc=1
fi

# 生成物の比較
# - tecsgen.rbdmp は Python 版では未移植（PORTING.md）
# - gen_rb / gen_py パス差は正規化して比較
rm -rf gen_rb.norm gen_py.norm
mkdir -p gen_rb.norm gen_py.norm
for d in gen_rb gen_py; do
    for f in "$d"/*; do
        [ -e "$f" ] || continue
        base=$(basename "$f")
        case "$base" in
            tecsgen.rbdmp) continue ;;
        esac
        sed 's/gen_rb/GEN/g; s/gen_py/GEN/g' "$f" > "${d}.norm/$base"
    done
done
if ! diff -ru gen_rb.norm gen_py.norm; then
    echo "生成物に差分あり"
    rc=1
fi

if [ "$rc" = 0 ]; then
    echo "差分なし"
fi
exit $rc
