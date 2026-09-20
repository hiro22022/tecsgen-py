/* #[<PREAMBLE>]#
 * Don't edit the comments between #[<...>]# and #[</...>]#
 * These comment are used by tecsmerege when merging.
 *
 * attr access macro #_CAAM_#
 * name             char_t*          ATTR_name       
 *
 * call port function #_TCPF_#
 * call port: cC4Call signature: sPumpMain context:task
 *   ER             cC4Call_Main( );
 * call port: cC3PubMain signature: sMain context:task
 *   void           cC3PubMain_Main( );
 * call port: cC3SubMain signature: sMain context:task optional:true
 *   bool_t     is_cC3SubMain_joined()                     check if joined
 *   void           cC3SubMain_Main( );
 * call port: cC2PumpMain signature: sPumpMain context:task
 *   ER             cC2PumpMain_Main( );
 * call port: cC2SubMain signature: sMain context:task optional:true
 *   bool_t     is_cC2SubMain_joined()                     check if joined
 *   void           cC2SubMain_Main( );
 * require port: signature:sKernel context:task
 *   ER             delay( RELTIM delay_time );
 *   ER             exitTask( );
 *   ER             getTime( SYSTIM* p_system_time );
 *   ER             getMicroTime( SYSUTM* p_system_micro_time );
 *   ER             exitKernel( );
 * require port: signature:sSysLog context:task
 *   ER             write( uint_t prio, const SYSLOG* p_syslog );
 *   ER_UINT        read( SYSLOG* p_syslog );
 *   ER             mask( uint_t logmask, uint_t lowmask );
 *   ER             refer( T_SYSLOG_RLOG* pk_rlog );
 *
 * #[</PREAMBLE>]# */

/* Put prototype declaration and/or variale definition here #_PAC_# */
#include "tTaskMain_tecsgen.h"
#include <stdio.h>

#ifndef E_OK
#define	E_OK	0		/* success */
#define	E_ID	(-18)	/* illegal ID */
#endif

/* entry port function #_TEPF_# */
/* #[<ENTRY_PORT>]# eTaskBody
 * entry port: eTaskBody
 * signature:  sTaskBody
 * context:    task
 * #[</ENTRY_PORT>]# */

/* #[<ENTRY_FUNC>]# eTaskBody_main
 * name:         eTaskBody_main
 * global_name:  tTaskMain_eTaskBody_main
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
void
eTaskBody_main(CELLIDX idx)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int   i, count = 5;

	syslog( LOG_INFO,  "### tTaskMain: Start %s Task ###", ATTR_name );
	/* Put statements here #_TEFB_# */
	for( i = 0; i < count; i++ ){
		syslog( LOG_INFO,  "** TaskMain: C4 DataPump TEST %d", i );
		cC4Call_Main( );
		delay( 500 );
		syslog( LOG_INFO,  "** TaskMain: C3 DataHolder TEST %d", i );
		cC3PubMain_Main();
		if( is_cC3SubMain_joined() )
			cC3SubMain_Main();
		delay( 500 );
		syslog( LOG_INFO,  "** TaskMain: C2 DataPumpHolder TEST %d", i );
		cC2PumpMain_Main();
		if( is_cC2SubMain_joined() )
			cC2SubMain_Main();
		delay( 1000 );
	}
	syslog( LOG_INFO,  "### tTaskMain: End %d times done ###", count );
	/*------------*/
}

/* #[<POSTAMBLE>]#
 *   Put non-entry functions below.
 * #[</POSTAMBLE>]#*/
