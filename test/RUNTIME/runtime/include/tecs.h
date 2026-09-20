/* tecs.h */
#ifndef TECS_H_
#define TECS_H_

/* va_list の正しい扱い方がわかっていない
 * とりあえず、ここでは typedef しておく．
 */
#ifdef TECSGEN
/* va_list is not supported in C_parser.y.rb */
typedef struct { int dummy; } va_list;
#endif

/* gcc-4 で多数の built-in ライブラリとの不整合の警告を消すため */
/* tecsgen の C_parser が読めない構文が多いため tecsgen 実行時は include しない */
// #ifndef TECSGEN
#if 1
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <memory.h>
#endif /* TECSGEN */

#include "tecs_config.h"
#include <tecs/machine.h>
#include <tecs/marshal.h>

typedef int  ID;

#endif  /* ! TECS_H_ */
