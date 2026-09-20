/* #[<PREAMBLE>]#
 * Don't edit the comments between #[<...>]# and #[</...>]#
 * These comment are used by tecsmerege when merging.
 *
 * #[</PREAMBLE>]# */

/* Put prototype declaration and/or variale definition here #_PAC_# */
#include "tArithmeticOperation_tecsgen.h"

#ifndef E_OK
#define	E_OK	0		/* success */
#define	E_ID	(-18)	/* illegal ID */
#endif

/* entry port function #_TEPF_# */
/* #[<ENTRY_PORT>]# eIAO32
 * entry port: eIAO32
 * signature:  sArithmeticOperation
 * context:    task
 * #[</ENTRY_PORT>]# */

/* #[<ENTRY_FUNC>]# eIAO32_add
 * name:         eIAO32_add
 * global_name:  tArithmeticOperation_eIAO32_add
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int32_t
eIAO32_add(CELLIDX idx, int32_t x, int32_t y)
{
	CELLCB	*p_cellcb;
	p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x + y;
}

/* #[<ENTRY_FUNC>]# eIAO32_sub
 * name:         eIAO32_sub
 * global_name:  tArithmeticOperation_eIAO32_sub
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int32_t
eIAO32_sub(CELLIDX idx, int32_t x, int32_t y)
{
	CELLCB	*p_cellcb;
	p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x - y;
}

/* #[<ENTRY_FUNC>]# eIAO32_mul
 * name:         eIAO32_mul
 * global_name:  tArithmeticOperation_eIAO32_mul
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int32_t
eIAO32_mul(CELLIDX idx, int32_t x, int32_t y)
{
	CELLCB	*p_cellcb;
	p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x * y;
}

/* #[<ENTRY_FUNC>]# eIAO32_div
 * name:         eIAO32_div
 * global_name:  tArithmeticOperation_eIAO32_div
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int32_t
eIAO32_div(CELLIDX idx, int32_t x, int32_t y)
{
	CELLCB	*p_cellcb;
	p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x / y;
}

/* #[<ENTRY_FUNC>]# eIAO32_rem
 * name:         eIAO32_rem
 * global_name:  tArithmeticOperation_eIAO32_rem
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int32_t
eIAO32_rem(CELLIDX idx, int32_t x, int32_t y)
{
	CELLCB	*p_cellcb;
	p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x % y;
}

/* #[<ENTRY_PORT>]# eIAO64
 * entry port: eIAO64
 * signature:  sArithmeticOperation2
 * context:    task
 * #[</ENTRY_PORT>]# */

/* #[<ENTRY_FUNC>]# eIAO64_add
 * name:         eIAO64_add
 * global_name:  tArithmeticOperation_eIAO64_add
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int64_t
eIAO64_add(CELLIDX idx, int64_t x, int64_t y)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x + y;
}

/* #[<ENTRY_FUNC>]# eIAO64_sub
 * name:         eIAO64_sub
 * global_name:  tArithmeticOperation_eIAO64_sub
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int64_t
eIAO64_sub(CELLIDX idx, int64_t x, int64_t y)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x - y;
}

/* #[<ENTRY_FUNC>]# eIAO64_mul
 * name:         eIAO64_mul
 * global_name:  tArithmeticOperation_eIAO64_mul
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int64_t
eIAO64_mul(CELLIDX idx, int64_t x, int64_t y)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x * y;
}

/* #[<ENTRY_FUNC>]# eIAO64_div
 * name:         eIAO64_div
 * global_name:  tArithmeticOperation_eIAO64_div
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int64_t
eIAO64_div(CELLIDX idx, int64_t x, int64_t y)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x / y;
}

/* #[<ENTRY_FUNC>]# eIAO64_rem
 * name:         eIAO64_rem
 * global_name:  tArithmeticOperation_eIAO64_rem
 * oneway:       false
 * #[</ENTRY_FUNC>]# */
int64_t
eIAO64_rem(CELLIDX idx, int64_t x, int64_t y)
{
	CELLCB	*p_cellcb = GET_CELLCB(idx);

	/* Put statements here #_TEFB_# */
	return x % y;
}

/* #[<POSTAMBLE>]#
 *   Put non-entry functions below.
 * #[</POSTAMBLE>]#*/
