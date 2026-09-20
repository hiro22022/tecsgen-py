#!/bin/sh
#
#  TECS Generator (Python port)
#      Generator for TOPPERS Embedded Component System
#
#   Copyright (C) 2008-2021 by TOPPERS Project TECS WG
#
#   ライセンスは tecsgen.py の冒頭を参照のこと．
#
#= コマンドラインオプションの挙動を Ruby 版と比較する
#
#  出力 (標準出力・標準エラー出力) と終了コードが一致することを確認する．
#  プログラム名だけは tecsgen.rb / tecsgen.py で異なるため読み替える．

set -u

here=$(cd "$(dirname "$0")/.." && pwd)
ruby_tecsgen=$here/../tecsgen/tecsgen/tecsgen.rb
py_tecsgen=$here/tecsgen/tecsgen.py

norm() {
    sed 's#^[^ ]*tecsgen\.\(rb\|py\): #PROG: #'
}

rc=0
run_case() {
    args=$1
    a=$(ruby    "$ruby_tecsgen" $args 2>&1 | norm)
    rca=$?
    b=$(python3 "$py_tecsgen"   $args 2>&1 | norm)
    rcb=$?
    if [ "$a" = "$b" ] && [ "$rca" = "$rcb" ]; then
        echo "OK   [$args]"
    else
        echo "DIFF [$args] rc=$rca/$rcb"
        diff -u /dev/fd/3 /dev/fd/4 3<<EOA 4<<EOB
$a
EOA
$b
EOB
        rc=1
    fi
}

run_case "--help"
run_case "--version"
run_case ""
run_case "-Z"
run_case "-n"
run_case "-h"
run_case "--def=X --version"
run_case "--no-banner --version"
run_case "-k euc --version"

exit $rc
