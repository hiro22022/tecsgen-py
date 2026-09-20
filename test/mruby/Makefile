TECSGEN_EXE ?= tecsgen
TECSPATH ?= $(abspath ../../tecsgen/tecs)

# ASP / ASP3 依存はパスがあるときだけ実行
HAS_ASP := $(shell test -d ../../../../../asp/asp+tecs/asp+tecs && echo yes)
HAS_ASP3 := $(shell test -d ../../../../../asp3/asp3-3.1.0 && echo yes)

total :
ifeq ($(HAS_ASP),yes)
	cd MrubyBridge-ASP ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
else
	@echo "SKIP MrubyBridge-ASP (ASP package not found)"
endif
ifeq ($(HAS_ASP3),yes)
	cd MrubyBridge-ASP3 ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
else
	@echo "SKIP MrubyBridge-ASP3 (ASP3 package not found)"
endif
	cd MrubyBridge-SimpleSample ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
	cd MrubyBridge-TECSInfo ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
	cd MrubyBridge-TECSInfoCompo ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
	cd MrubyBridge-region ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
	cd MrubyBridge-test ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
	cd mrubycellplugin ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
	cd MrubyInfoBridge-SimpleSample ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)
	cd MrubyInfoBridge-test ; make allall TECSGEN_EXE=$(TECSGEN_EXE) TECSPATH=$(TECSPATH)

clean:
	-cd MrubyBridge-ASP ; make clean
	-cd MrubyBridge-ASP3 ; make clean
	cd MrubyBridge-SimpleSample ; make clean
	cd MrubyBridge-TECSInfo ; make clean
	cd MrubyBridge-TECSInfoCompo ; make clean
	cd MrubyBridge-region ; make clean
	cd MrubyBridge-test ; make clean
	cd mrubycellplugin ; make clean
	cd MrubyInfoBridge-SimpleSample ; make clean
	cd MrubyInfoBridge-test ; make clean

test_exec :
	@echo ===== MrubyBridge-SimpleSample =====
	@cd MrubyBridge-SimpleSample && ./SimpleSample.exe ./SimpleSample.rb
	@echo ===== MrubyBridge-region =====
	@cd MrubyBridge-region && ./SimpleSample.exe ./SimpleSample.rb
	@echo ===== MrubyBridge-test =====
	@cd MrubyBridge-test && ./test.exe ./test.rb
	@echo ===== MrubyBridge-test 2 =====
	@cd MrubyBridge-test && ./test.exe ./test2.rb
	@echo ===== MrubyBridge-TECSInfo =====
	@cd MrubyBridge-TECSInfo && ./SimpleSample.exe ./SimpleSample.rb
	@echo ===== MrubyBridge-TECSInfoCompo =====
	@cd MrubyBridge-TECSInfoCompo && ./SimpleSample.exe ./SimpleSample.rb
	@echo ===== mrubycellplugin =====
	@cd mrubycellplugin && ./mrubycellplugin.exe ./script.rb
	@echo ===== MrubyInfoBridge-SimpleSample =====
	@cd MrubyInfoBridge-SimpleSample && ./SimpleSample.exe ./SimpleSample.rb
	@echo ===== MrubyInfoBridge-test =====
	@cd MrubyInfoBridge-test && ./test.exe
