/*
 * クラス定義
 *   
 */
__tool_info__ ("MyClass_class_def") {
    "class_def" : [
        {
            "type"        : "class",
            "class_name"  : "CLS_PRC1",
            "processorID" : 1,
            "locality"    : "only",
            "class_name_in_kernel" : "CLS_PRC1"     // 省略可
        },
        {
            "type"        : "class",
            "class_name"  : "CLS_ALL_PRC1",
            "processorID" : 1,
            "locality"    : "all"
        },
        {
            "type"        : "class",
            "class_name"  : "CLS_PRC2",
            "processorID" : 2,
            "locality"    : "only"
        },
        {
            "type"        : "class",
            "class_name"  : "CLS_ALL_PRC2",
            "processorID" : 2,
            "locality"    : "all"
        },
        {
            "type"        : "class",
            "class_name"  : "global",
            "processorID" : 0,
            "locality"    : "global"
        }
    ]
}
