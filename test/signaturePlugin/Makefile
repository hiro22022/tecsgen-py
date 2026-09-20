# 変数 #_MVAR_#
# fixed variable (unchangeable by config or plugin)
TARGET_BASE = generate
BASE_DIR = .
GEN_DIR = $(BASE_DIR)/gen
INCLUDES = -I $(BASE_DIR)/. -I $(BASE_DIR)/../cygwin3 -I $(BASE_DIR)/../../tecs -I $(TECSPATH) -I $(TECSPATH)/mruby -I $(TECSPATH)/posix -I $(TECSPATH)/rpc -I $(MRUBYPATH)/include -I $(GEN_DIR)
DEFINES =

# end of fixed variable (unchangeable by config or plugin)
#default C Compiler
CC = gcc

#default C Compiler options
CFLAGS = $(INCLUDES) $(DEFINES) -D  "Inline=static inline"

#default Liknker
LD = gcc

#default Liknker Options
LDFLAGS = -L$(MRUBYPATH)/build/host/lib -lmruby

#CHANGE this to suitable path
# MRUBYPATH = ..
MRUBYPATH=${HOME}/mruby/mruby-3.0.0

#default source directory
SRC_DIR = $(BASE_DIR)/src

#default target name
TARGET = $(TARGET_BASE).exe

#default TECS generator
TECSGEN = tecsgen

#Time Stamp
TIMESTAMP = $(GEN_DIR)/tecsgen.timestamp

#default relocatable object (.o) directory
_TECS_OBJ_DIR = $(GEN_DIR)/



# Pre-tecsgen target
PRE_TECSGEN_TARGET =

# Post-tecsgen target
POST_TECSGEN_TARGET =

# vpath for C sources and headers
vpath %.c $(SRC_DIR) $(GEN_DIR)  ../cygwin3 ../../tecs $(TECSPATH) $(TECSPATH)/mruby $(TECSPATH)/mruby-bak2 $(TECSPATH)/mruby.org $(TECSPATH)/posix $(TECSPATH)/rpc $(MRUBYPATH)/include
vpath %.h $(SRC_DIR) $(GEN_DIR)  ../cygwin3 ../../tecs $(TECSPATH) $(TECSPATH)/mruby $(TECSPATH)/mruby-bak2 $(TECSPATH)/mruby.org $(TECSPATH)/posix $(TECSPATH)/rpc $(MRUBYPATH)/include

# Other objects (out of tecsgen)
OTHER_OBJS =                      # Add objects out of tecs care.
# OTHER_OBJS = $(_TECS_OBJ_DIR)vasyslog.o
# ルール #_MRUL_#
allall: tecs
	make all     # in order to include generated Makefile.tecsgen & Makefile.depend

all : $(TARGET)


# depend を include #_MDEP_#
-include $(GEN_DIR)/Makefile.tecsgen
-include $(GEN_DIR)/Makefile.depend

$(TARGET) : $(TIMESTAMP) $(CELLTYPE_COBJS) $(TECSGEN_COBJS) $(PLUGIN_COBJS) $(OTHER_OBJS)
	$(LD) -o $(TARGET) $(TECSGEN_COBJS) $(CELLTYPE_COBJS) $(PLUGIN_COBJS) $(OTHER_OBJS) $(LDFLAGS)

clean :
	rm -f $(CELLTYPE_COBJS) $(TECSGEN_COBJS) $(PLUGIN_COBJS) $(OTHER_OBJS) $(TARGET)  $(TIMESTAMP)
	rm -rf $(GEN_DIR)

tecs : $(PRE_TECSGEN_TARGET) $(TIMESTAMP) $(POST_TECSGEN_TARGET)

$(TIMESTAMP) : $(TECS_IMPORTS)
	$(TECSGEN)  -L . -I ../cygwin3 -I ../../tecs generate.cdl
# generic target for objs
$(_TECS_OBJ_DIR)%.o : %.c
	$(CC) -c $(CFLAGS) -o $@ $<

$(_TECS_OBJ_DIR)tTask.o : tTask.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)tTECSTest.o : tTECSTest.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nMruby_tTECSInitializer.o : nMruby_tTECSInitializer.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nMruby_tCharPointer.o : nMruby_tCharPointer.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nMruby_tInt32Pointer.o : nMruby_tInt32Pointer.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nMruby_tULongPointer.o : nMruby_tULongPointer.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nMruby_tsTest.o : nMruby_tsTest.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nMruby_tsTest_Initializer.o : nMruby_tsTest_Initializer.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nMruby_tagSt.o : nMruby_tagSt.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
$(_TECS_OBJ_DIR)nC2TECS_tsTest.o : nC2TECS_tsTest.c
	$(CC) -c $(CFLAGS) -o $@ $<
 
