
#include "iostream"
#include "tArithmeticOperation_cppif.hpp"
#include "tArithmeticOperationSingleton_cppif.hpp"
#include "tArithmeticOperationEA_cppif.hpp"
#include "tArithmeticOperationSingletonEA_cppif.hpp"

int main( int n, char **argv )
{
    tArithmeticOperation  iao( IAO_IDX );

    int  z32;
#define X32  (1)
#define Y32  (2)
    z32 = iao.eIAO32.add( X32, Y32 );
    std::cout << "X32(=" << X32 << ") + Y32(=" << Y32 << ") = Z32(=" << z32 << ")\n";

    int64_t  z64;
#define X64  (3)
#define Y64  (4)
    z64 = iao.eIAO64.add( X64, Y64 );
    std::cout << "X64(=" << X64 << ") + Y64(=" << Y64 << ") = Z64(=" << z64 << ")\n";

    /* sArithmeticOperation32 型として扱う */
    sArithmeticOperation32 *sAO32;
    sAO32 = &iao.eIAO32;
    int  z32b;
#define X32b  (5)
#define Y32b  (6)
    z32b = sAO32->add( X32b, Y32b );
    std::cout << "X32b(=" << X32b << ") + Y32b(=" << Y32b << ") = Z32b(=" << z32b << ")\n";

    /* シングルトンの例 */
    tArithmeticOperationSingleton iaoSingleton;     /* singleton の場合、'()' を付けてはいけない．関数宣言に扱われてしまう */
    sArithmeticOperation32 *sAO32S;
    int  z32c;
#define X32c  (7)
#define Y32c  (8)
    sAO32S = &iaoSingleton.eIAO32;
    z32c = sAO32S->add( X32c, Y32c );
    std::cout << "X32c(=" << X32c << ") + Y32c(=" << Y32c << ") = Z32c(=" << z32c << ")\n";

/////////  受け口配列の例  /////////
    tArithmeticOperationEA  iaoea( IAOEA_IDX );
    z32 = iaoea.eIAO32[0].add( X32, Y32 );

    tArithmeticOperationEA  iaoe( IAOEA_IDX );

    // 普通の呼出し方の例 1
    z32b = iaoe.eIAO32[2].add( X32b, Y32b );
    std::cout << "EA: X32b(=" << X32b << ") + Y32b(=" << Y32b << ") = Z32b(=" << z32b << ")\n";

    // 普通の呼出し方の例 2
    z64 = iaoe.eIAO64[2].add( X64, Y64 );
    std::cout << "EA: X64(=" << X64 << ") + Y64(=" << Y64 << ") = Z64(=" << z64 << ")\n";

    /* シングルトンの例 */
    tArithmeticOperationSingletonEA iasea;
    z64 = iasea.eIAO64[2].mul( X64, Y64 );
    std::cout << "EA: X64(=" << X64 << ") * Y64(=" << Y64 << ") = Z64(=" << z64 << ")\n";

    /* sArithmeticOperation32 型として扱う */
    // 以下は、[] がオーバーライドされた演算子であるため、エラーとなる。
    //    sArithmeticOperation32 *sAO32v = &iaoe.eIAO32[4];
    //
    // 以下は、sArithmeticOperation32 が仮想クラスのため不可。
    // できたとしても、メンバー変数を失うため、不適切。
    //    sArithmeticOperation32 sAO32v;

    // 以下はクラス eIAO32_ は private な inner class なので扱えない。
    // tArithmeticOperationEA::eIAO32_ sAO32v2 = iaoe.eIAO32[4];
    //    auto だと扱えるのは gcc 10.2.0, 7.4.0、 VC++2019 で確認。
    //    auto は C++11 以降なので、それ以前では使えない。
    auto sAO32v = iaoe.eIAO32[4];
    sAO32 = &sAO32v;
    z32c = sAO32v.add( X32c, Y32c );
    std::cout << "X32b(=" << X32c << ") + Y32c(=" << Y32c << ") = Z32c(=" << z32c << ")\n";
}
