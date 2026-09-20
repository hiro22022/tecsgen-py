# Copyright (c) 2009-2021 by TOPPERS Project TECS WG.
#
# 隣の Ruby 版 tecsgen 配布ルートの Makefile に対応する。
# 主としてテストを実行する。TECS ジェネレータ利用者は実行不要。

# Python 版はビルド不要。Ruby 差分比較を既定の確認とする。
# set_env.sh 相当: tecsgen を PATH に載せ、TECSPATH を設定する。
export PATH := $(CURDIR)/tecsgen:$(PATH)
export TECSPATH := $(CURDIR)/tecsgen/tecs

all: compare
	@echo "Success!"
	@echo "try 'make test' to run the Ruby-compatible test/ Makefile with Python tecsgen"
	@echo "try 'make test_err' for ErrorCase"
	@echo "try 'make test_exec' if you want to test EXEs"
	@echo "try 'make test_cli' for --help/--version CLI checks"

# do 'all', do error test cases and execute all built test modules.
allall: all test test_err test_exec

# Ruby 版の generator ターゲット相当（Python では no-op）
generator:
	@echo "Python tecsgen: no build step ($(CURDIR)/tecsgen/tecsgen)"

# Ruby 版 test/Makefile を Python tecsgen で実行
# 自動生成 Makefile は TECSGEN=tecsgen を使うため、TECSGEN も渡す。
.PHONY: test
test: generator
	cd test ; $(MAKE) TECSGEN_EXE=$(CURDIR)/tecsgen/tecsgen TECSGEN=$(CURDIR)/tecsgen/tecsgen TECSMERGE_EXE=$(CURDIR)/tecsgen/tecsmerge

test_err:
	cd test/ErrorCase ; $(MAKE) TECSGEN_EXE=$(CURDIR)/tecsgen/tecsgen TECSGEN=$(CURDIR)/tecsgen/tecsgen

# ビルド済み .exe を実行（opaque* / mruby は除外し、mruby は専用ターゲットへ）
.PHONY: test_exec
test_exec:
	find test \( -name '*[Oo]paque*' -prune \) -o \( -name mruby -prune \) -o -name '*.exe' -exec echo exec: '<<<' '{}' '>>>' \; -exec '{}' \;
	cd test/mruby; $(MAKE) test_exec TECSGEN_EXE=$(CURDIR)/tecsgen/tecsgen TECSPATH=$(CURDIR)/tecsgen/tecs

# CLI オプションの Ruby 比較
.PHONY: test_cli
test_cli:
	tools/test_cli.sh

# 生成物・警告位置の Ruby 差分比較（移植進捗の主回帰）
.PHONY: compare
compare: test_cli
	cd test ; $(MAKE) -f Makefile.compare

clean:
	cd test ; $(MAKE) clean
	rm -rf gen gen_rb gen_py gen_rb.norm gen_py.norm
	find . \( -name '*~' -o -name '*.o' -o -name '__pycache__' -o -name '*.pyc' \) -exec rm -rf '{}' + 2>/dev/null || true
	find test -name '*.exe' -exec rm -f '{}' \;
