/* #[<PREAMBLE>]#
 * Don't edit the comments between #[<...>]# and #[</...>]#
 * These comment are used by tecsmerege when merging.
 *
 * call port function #_TCPF_#
 * call port: cC3SubGet signature: sPersonalDataGetSignature context:task
 *   ER             cC3SubGet_waitForNewData( );
 *   ER             cC3SubGet_dataReadDone( );
 *   ER             cC3SubGet_get_count( int_t* count );
 *   ER             cC3SubGet_get_BirthDay( Date* BirthDay );
 *   ER             cC3SubGet_get_Age( uint8_t* Age );
 *   ER             cC3SubGet_get_Name( char_t* Name );
 * call port: cC2SubGet signature: sPersonalDataGetSignature context:task
 *   ER             cC2SubGet_waitForNewData( );
 *   ER             cC2SubGet_dataReadDone( );
 *   ER             cC2SubGet_get_count( int_t* count );
 *   ER             cC2SubGet_get_BirthDay( Date* BirthDay );
 *   ER             cC2SubGet_get_Age( uint8_t* Age );
 *   ER             cC2SubGet_get_Name( char_t* Name );
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
#include "tPersonalDataSub_tecsgen.h"
#include <stdio.h>

#ifndef E_OK
#define	E_OK	0		/* success */
#define	E_ID	(-18)	/* illegal ID */
#endif

/* entry port function #_TEPF_# */
/* #[<ENTRY_PORT>]# eC4SubSet
 * entry port: eC4SubSet
 * signature:  sPersonalDataSetSignature
 * context:    task
 * #[</ENTRY_PORT>]# */

/* #[<ENTRY_FUNC>]# eC4SubSet_waitForReadDone
 * name:         eC4SubSet_waitForReadDone
 * global_name:  tPersonalDataSub_eC4SubSet_waitForReadDone
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC4SubSet_waitForReadDone(CELLIDX idx)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO, "C4S PersonalDataSub waitForReadDone");

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4SubSet_newDataReady
 * name:         eC4SubSet_newDataReady
 * global_name:  tPersonalDataSub_eC4SubSet_newDataReady
 * oneway:       true
 * #[</ENTRY_FUNC>]# */
ER
eC4SubSet_newDataReady(CELLIDX idx)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO, "C4S PersonalDataSub newDataReady");

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4SubSet_set_count
 * name:         eC4SubSet_set_count
 * global_name:  tPersonalDataSub_eC4SubSet_set_count
 * oneway:       true
 * #[</ENTRY_FUNC>]# */
ER
eC4SubSet_set_count(CELLIDX idx, const int_t count)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO,  "C4S PersonalDataSub count: %d", count );

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4SubSet_set_BirthDay
 * name:         eC4SubSet_set_BirthDay
 * global_name:  tPersonalDataSub_eC4SubSet_set_BirthDay
 * oneway:       true
 * #[</ENTRY_FUNC>]# */
ER
eC4SubSet_set_BirthDay(CELLIDX idx, const Date BirthDay)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO,  "C4S PersonalDataSub BirthDay: %d.%d.%d", BirthDay.year, BirthDay.month, BirthDay.day);

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4SubSet_set_Age
 * name:         eC4SubSet_set_Age
 * global_name:  tPersonalDataSub_eC4SubSet_set_Age
 * oneway:       true
 * #[</ENTRY_FUNC>]# */
ER
eC4SubSet_set_Age(CELLIDX idx, const uint8_t Age)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO,  "C4S PersonalDataSub Age: %d", Age );

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4SubSet_set_Name
 * name:         eC4SubSet_set_Name
 * global_name:  tPersonalDataSub_eC4SubSet_set_Name
 * oneway:       true
 * #[</ENTRY_FUNC>]# */
ER
eC4SubSet_set_Name(CELLIDX idx, const char_t* Name)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO,  "C4S PersonalDataSub Name: %s", Name );

	return(ercd);
}

/* #[<ENTRY_PORT>]# eC3Main
 * entry port: eC3Main
 * signature:  sMain
 * context:    task
 * #[</ENTRY_PORT>]# */

/* #[<ENTRY_FUNC>]# eC3Main_Main
 * name:         eC3Main_Main
 * global_name:  tPersonalDataSub_eC3Main_Main
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
void
eC3Main_Main(CELLIDX idx)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	Date	BirthDay;
	uint8_t	Age;
	char_t	Name[64];
	int_t	count;

	/* Put statements here #_TEFB_# */
	cC3SubGet_waitForNewData( );
 	cC3SubGet_get_count( &count );
 	cC3SubGet_get_BirthDay( &BirthDay );
 	cC3SubGet_get_Age( &Age );
 	cC3SubGet_get_Name( Name );
 	cC3SubGet_dataReadDone( );
	syslog( LOG_INFO,  "C3S PersonalDataSub count: %d", count );
	syslog( LOG_INFO,  "C3S PersonalDataSub Birthday: %d.%d.%d, Name: %s, Age: %d",
		BirthDay.year, BirthDay.month, BirthDay.day, Name, Age );
}

/* #[<ENTRY_PORT>]# eC2Main
 * entry port: eC2Main
 * signature:  sMain
 * context:    task
 * #[</ENTRY_PORT>]# */

/* #[<ENTRY_FUNC>]# eC2Main_Main
 * name:         eC2Main_Main
 * global_name:  tPersonalDataSub_eC2Main_Main
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
void
eC2Main_Main(CELLIDX idx)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	Date	BirthDay;
	uint8_t	Age;
	char_t	Name[64];
	int_t	count;

	/* Put statements here #_TEFB_# */

	cC2SubGet_waitForNewData( );
 	cC2SubGet_get_count( &count );
	cC2SubGet_get_BirthDay( &BirthDay );
 	cC2SubGet_get_Age( &Age );
 	cC2SubGet_get_Name( Name );
 	cC2SubGet_dataReadDone( );
	syslog( LOG_INFO,  "C2S PersonalDataSub count: %d", count );
	syslog( LOG_INFO,  "C2S PersonalDataSub Birthday: %d.%d.%d, Name: %s, Age: %d",
		BirthDay.year, BirthDay.month, BirthDay.day, Name, Age );
}

/* #[<POSTAMBLE>]#
 *   Put non-entry functions below.
 * #[</POSTAMBLE>]#*/
