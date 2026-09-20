/* #[<PREAMBLE>]#
 * Don't edit the comments between #[<...>]# and #[</...>]#
 * These comment are used by tecsmerege when merging.
 *
 * call port function #_TCPF_#
 * call port: cC3PubSet signature: sPersonalDataSetSignature context:task
 *   ER             cC3PubSet_waitForReadDone( );
 *   ER             cC3PubSet_newDataReady( );
 *   ER             cC3PubSet_set_count( const int_t count );
 *   ER             cC3PubSet_set_BirthDay( const Date BirthDay );
 *   ER             cC3PubSet_set_Age( const uint8_t Age );
 *   ER             cC3PubSet_set_Name( const char_t* Name );
 * require port: signature:sSysLog context:task
 *   ER             write( uint_t prio, const SYSLOG* p_syslog );
 *   ER_UINT        read( SYSLOG* p_syslog );
 *   ER             mask( uint_t logmask, uint_t lowmask );
 *   ER             refer( T_SYSLOG_RLOG* pk_rlog );
 *
 * #[</PREAMBLE>]# */

/* Put prototype declaration and/or variale definition here #_PAC_# */
#include "tPersonalDataPub_tecsgen.h"
#include <sys/time.h>
#include <time.h>

#ifndef E_OK
#define	E_OK	0		/* success */
#define	E_ID	(-18)	/* illegal ID */
#endif

uint8_t  calc_age( Date BirthDay );

struct PersonalData{
	Date     BirthDay;
	char_t*  Name;
};;

struct PersonalData PD[] =
{
	{ { 2009,  5, 10 }, "TECS Generator" },
	{ { 2016,  5,  7 }, "TECS CDE" },
	{ { 2012, 11,  6 }, "MrubyBridgePlugin" },
	{ { 2017, 11,  5 }, "TECSInfo" }
};


/* entry port function #_TEPF_# */
/* #[<ENTRY_PORT>]# eC4PubGet
 * entry port: eC4PubGet
 * signature:  sPersonalDataGetSignature
 * context:    task
 * #[</ENTRY_PORT>]# */

static int c4_count = 0;

/* #[<ENTRY_FUNC>]# eC4PubGet_waitForNewData
 * name:         eC4PubGet_waitForNewData
 * global_name:  tPersonalDataPub_eC4PubGet_waitForNewData
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC4PubGet_waitForNewData(CELLIDX idx)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
//	syslog( LOG_INFO, "C4P PersonalDataPub waitForNewData count: %d", c4_count );

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4PubGet_dataReadDone
 * name:         eC4PubGet_dataReadDone
 * global_name:  tPersonalDataPub_eC4PubGet_dataReadDone
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC4PubGet_dataReadDone(CELLIDX idx)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
//	syslog( LOG_INFO, "C4P PersonalDataPub dataReadDone:   count: %d", c4_count);
	c4_count++;

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4PubGet_get_count
 * name:         eC4PubGet_get_count
 * global_name:  tPersonalDataPub_eC4PubGet_get_count
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC4PubGet_get_count(CELLIDX idx, int_t* count)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	*count = c4_count;

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4PubGet_get_BirthDay
 * name:         eC4PubGet_get_BirthDay
 * global_name:  tPersonalDataPub_eC4PubGet_get_BirthDay
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC4PubGet_get_BirthDay(CELLIDX idx, Date* BirthDay)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int     i;
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	i = c4_count % (sizeof( PD ) / sizeof( struct PersonalData ));
	BirthDay->year  = PD[i].BirthDay.year;
	BirthDay->month = PD[i].BirthDay.month;
	BirthDay->day   = PD[i].BirthDay.day;

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4PubGet_get_Age
 * name:         eC4PubGet_get_Age
 * global_name:  tPersonalDataPub_eC4PubGet_get_Age
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC4PubGet_get_Age(CELLIDX idx, uint8_t* Age)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int     i;
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	i = c4_count % (sizeof( PD ) / sizeof( struct PersonalData ));
	*Age = calc_age( PD[i].BirthDay );
	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC4PubGet_get_Name
 * name:         eC4PubGet_get_Name
 * global_name:  tPersonalDataPub_eC4PubGet_get_Name
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC4PubGet_get_Name(CELLIDX idx, char_t* Name)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int     i;
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	i = c4_count % (sizeof( PD ) / sizeof( struct PersonalData ));
	strcpy( Name, PD[i].Name );
	syslog( LOG_INFO, "eC4PubGet_get_Name %s", Name );

	return(ercd);
}

/* #[<ENTRY_PORT>]# eC3Main
 * entry port: eC3Main
 * signature:  sMain
 * context:    task
 * #[</ENTRY_PORT>]# */

static int c3_count;


/* #[<ENTRY_FUNC>]# eC3Main_Main
 * name:         eC3Main_Main
 * global_name:  tPersonalDataPub_eC3Main_Main
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
void
eC3Main_Main(CELLIDX idx)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int		i;

	/* Put statements here #_TEFB_# */
	i = c3_count % (sizeof( PD ) / sizeof( struct PersonalData ));
	syslog( LOG_INFO, "C3P PersonalDataPub Main: count: %d", c3_count);
 	cC3PubSet_waitForReadDone( );
	cC3PubSet_set_count( c3_count );
	cC3PubSet_set_BirthDay( PD[i].BirthDay );
	cC3PubSet_set_Age( calc_age( PD[i].BirthDay ) );
	cC3PubSet_set_Name( PD[i].Name );
 	cC3PubSet_newDataReady( );
	c3_count++;
}

/* #[<ENTRY_PORT>]# eC2PubGet
 * entry port: eC2PubGet
 * signature:  sPersonalDataGetSignature
 * context:    task
 * #[</ENTRY_PORT>]# */

static int c2_count = 0;

/* #[<ENTRY_FUNC>]# eC2PubGet_waitForNewData
 * name:         eC2PubGet_waitForNewData
 * global_name:  tPersonalDataPub_eC2PubGet_waitForNewData
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC2PubGet_waitForNewData(CELLIDX idx)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO, "C2P PersonalDataPub waitForNewData: count: %d", c2_count);

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC2PubGet_dataReadDone
 * name:         eC2PubGet_dataReadDone
 * global_name:  tPersonalDataPub_eC2PubGet_dataReadDone
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC2PubGet_dataReadDone(CELLIDX idx)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	syslog( LOG_INFO, "C2P PersonalDataPub dataReadDone count: %d", c2_count);
	c2_count++;

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC2PubGet_get_count
 * name:         eC2PubGet_get_count
 * global_name:  tPersonalDataPub_eC2PubGet_get_count
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC2PubGet_get_count(CELLIDX idx, int_t* count)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	*count = c2_count;

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC2PubGet_get_BirthDay
 * name:         eC2PubGet_get_BirthDay
 * global_name:  tPersonalDataPub_eC2PubGet_get_BirthDay
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC2PubGet_get_BirthDay(CELLIDX idx, Date* BirthDay)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int     i;
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	i = c2_count % (sizeof( PD ) / sizeof( struct PersonalData ));
	BirthDay->year  = PD[i].BirthDay.year;
	BirthDay->month = PD[i].BirthDay.month;
	BirthDay->day   = PD[i].BirthDay.day;

	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC2PubGet_get_Age
 * name:         eC2PubGet_get_Age
 * global_name:  tPersonalDataPub_eC2PubGet_get_Age
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC2PubGet_get_Age(CELLIDX idx, uint8_t* Age)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int     i;
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	i = c2_count % (sizeof( PD ) / sizeof( struct PersonalData ));
	*Age = calc_age( PD[i].BirthDay );
	return(ercd);
}

/* #[<ENTRY_FUNC>]# eC2PubGet_get_Name
 * name:         eC2PubGet_get_Name
 * global_name:  tPersonalDataPub_eC2PubGet_get_Name
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
ER
eC2PubGet_get_Name(CELLIDX idx, char_t* Name)
{
	ER		ercd = E_OK;
	CELLCB	*p_cellcb = GET_CELLCB(idx);
	int     i;
	(void)p_cellcb;

	/* Put statements here #_TEFB_# */
	i = c2_count % (sizeof( PD ) / sizeof( struct PersonalData ));
	strcpy( Name, PD[i].Name );

	return(ercd);
}

/* #[<POSTAMBLE>]#
 *   Put non-entry functions below.
 * #[</POSTAMBLE>]#*/

uint8_t  calc_age( Date BirthDay )
{
	struct timespec tp;
	struct tm       result, *res;
	int    sub;

	clock_gettime(CLOCK_REALTIME, &tp);
	res = localtime_r( &tp.tv_sec, &result );
	(void)res;

	if( BirthDay.month > result.tm_mon ){
		sub = 1;
	} else if ( BirthDay.month == result.tm_mon ){
		if( BirthDay.day >= result.tm_mday )
			sub = 1;
		else 
			sub = 0;
	} else{
		sub = 0;
	}

	// printf( "now year = %d birth year = %d sub = %d\n", result.tm_year + 1900, BirthDay.year, sub);
	return result.tm_year + 1900 - BirthDay.year - sub;
}
