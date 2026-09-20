#include <stdio.h>
#include "tArithmeticOperation_cif.h"
#include "tArithmeticOperationSingleton_cif.h"

int main( int n, char **argv )
{
    int  z32;
#define X32  (1)
#define Y32  (2)
    z32 = IAO_eIAO32_add( X32, Y32 );
    printf( "X32(=%d) + Y32(=%d) = Z32(=%d)\n", X32, Y32, z32 );

    int  z64;
#define X64  (3)
#define Y64  (4)
    z64 = IAO_eIAO64_add( X64, Y64 );
    printf( "X64(=%d) + Y64(=%d) = Z64(=%d)\n", X64, Y64, z64 );

    /* シングルトンセル */
    int  z32b;
#define X32b  (5)
#define Y32b  (6)
    z32b = IAOSingleton_eIAO32_add( X32b, Y32b );
    printf( "X32b(=%d) + Y32b(=%d) = Z32b(=%d)\n", X32b, Y32b, z32b );

    z64 = IAO_eIAO32EA_add( 2, X32, Y32 );
    printf( "X32(=%d) + Y32(=%d) = Z32(=%d)\n", X32, Y32, z32 );
}
