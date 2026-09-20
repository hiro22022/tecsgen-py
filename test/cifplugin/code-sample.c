C 言語 IF のサンプルコード

#ifndef tRawSpinLock_FACTORY_H
#define tRawSpinLock_FACTORY_H

/* include celltype definition header */
#define TOPPERS_CB_TYPE_ONLY
#include "tRawSpinLock_tecsgen.h"
#undef TOPPERS_CB_TYPE_ONLY
/**/

/* cell: RawSpinLock */
#define RawSpinLock_lock()      tRawSpinLock_eRawSpinLock_lock( &tRawSpinLock_INIB_tab[0] )
#define RawSpinLock_trylock()   tRawSpinLock_eRawSpinLock_tryLock( &tRawSpinLock_INIB_tab[0] )
#define RawSpinLock_unlock()    tRawSpinLock_eRawSpinLock_unlock( &tRawSpinLock_INIB_tab[0] )
/**/

#endif /* tRawSpinLock_FACTORY_H */
