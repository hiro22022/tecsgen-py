# coding: utf-8
# ドメインプラグインの実例 MyClassPlugin

from tecslib.core.tool_info import TOOL_INFO
from tecslib.plugin.ClassPlugin import ClassPlugin
from tecslib.rubylib.symbol import Sym


class MyClassPlugin(ClassPlugin):

    CLASS_DEF_schema = {
        Sym("MyClass_class_def"): {
            Sym("class_def"): [Sym("class")],
        },
        Sym("class"): {
            Sym("type"): "class",
            Sym("class_name"): Sym("string"),
            Sym("processorID"): Sym("integer"),
            Sym("locality"): Sym("string"),
        },
        Sym("__class"): {
            Sym("class_name_in_kernel"): Sym("string"),
        },
    }

    class_info = None

    def __init__(self, region, class_type_name, option):
        super().__init__(region, class_type_name, option)
        if MyClassPlugin.class_info is None:
            self.validate_and_set_class_info()
        print("MyClassPlugin: initialize: region={}, classTypeName={}, option={}".format(
            region.get_name(), class_type_name, option))

    def add_through_plugin(self, join, current_region, next_region, through_type):
        print("MyClassPlugin: add_through_plugin: {}=>{}, {}.{}=>{}.{}., {}".format(
            current_region.get_name(), next_region.get_name(),
            join.get_owner().get_name(), join.get_definition().get_name(),
            join.get_cell().get_name(), join.get_port_name(), through_type))
        return [Sym("TracePlugin"), ""]

    def joinable(self, current_region, next_region, through_type):
        print("MyClassPlugin: joinable? from {} to {} ({})".format(
            current_region.get_name(), next_region.get_name(), through_type))
        return True

    @classmethod
    def gen_post_code(cls, file):
        pass

    def get_kind(self):
        return Sym("kernel")

    def validate_and_set_class_info(self):
        validator = TOOL_INFO.VALIDATOR(Sym("MyClass_class_def"), MyClassPlugin.CLASS_DEF_schema)
        if validator.validate():
            MyClassPlugin.class_info = {}
            info = TOOL_INFO.get_tool_info(Sym("MyClass_class_def"))
            if info is None:
                self.cdl_error("MyClass9999 not found __tool_info__( MyClass_class_def )")
                return
            class_info = info.get(Sym("class_def"))
            if class_info is None:
                class_info = info.get("class_def")
            for cls in class_info:
                cn = cls.get(Sym("class_name")) or cls.get("class_name")
                attr = {}
                MyClassPlugin.class_info[_sym(cn)] = attr
                attr["processorID"] = cls.get(Sym("processorID")) or cls.get("processorID")
                attr["locality"] = cls.get(Sym("locality")) or cls.get("locality")
                attr["class_name"] = cn
                kin = cls.get(Sym("class_name_in_kernel")) or cls.get("class_name_in_kernel")
                if kin:
                    attr["class_name"] = kin

    def check_class(self, class_name):
        print("MyClassPlugin#check_class {}".format(class_name))
        key = _sym(class_name)
        return key in (MyClassPlugin.class_info or {})


def _sym(x):
    if isinstance(x, Sym):
        return x
    return Sym(str(x))
