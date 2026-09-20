REM (UTF-8)
REM Visual Studio Community 版でビルドしてみる (C++ 文法の確認の意図)
REM 以下のパスを追加
REM "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\Llvm\x64\bin"

tecsgen.rb cppifplugin.cdl -c "clang.exe -E -D TECSGEN -D NO_TECSGEN_VA_LIST" -I ../cygwin
clang -Igen -I../../tecsgen/tecs -I../cygwin -c -o gen\cppifplugin.o src\cppifplugin.cpp
clang -Igen -I../../tecsgen/tecs -I../cygwin -c -o gen\tArithmeticOperation_tecsgen.o gen\tArithmeticOperation_tecsgen.c
clang -Igen -I../../tecsgen/tecs -I../cygwin -c -o gen\tArithmeticOperation.o src\tArithmeticOperation.c
clang -Igen -I../../tecsgen/tecs -I../cygwin -c -o gen\tArithmeticOperationSingleton_tecsgen.o gen\tArithmeticOperationSingleton_tecsgen.c
clang -Igen -I../../tecsgen/tecs -I../cygwin -c -o gen\tArithmeticOperationSingleton.o src\tArithmeticOperationSingleton.c
clang -ocppifplugin.exe gen\cppifplugin.o gen\tArithmeticOperation.o gen\tArithmeticOperation_tecsgen.o gen\tArithmeticOperationSingleton.o gen\tArithmeticOperationSingleton_tecsgen.o


