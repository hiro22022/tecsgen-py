# ドメインプラグインの実例 MyDomainPlugin

from tecslib.plugin.DomainPlugin import DomainPlugin
from tecslib.rubylib.symbol import Sym


class MyDomainPlugin(DomainPlugin):

    def __init__(self, region, domain_type_name, option):
        super().__init__(region, domain_type_name, option)
        print("MyDomainPlugin: initialize: region={}, domainTypeName={}, option={}".format(
            region.get_name(), domain_type_name, option))

    def add_through_plugin(self, join, current_region, next_region, through_type):
        print("MyDomainPlugin: add_through_plugin: {}=>{}, {}.{}=>{}.{}., {}".format(
            current_region.get_name(), next_region.get_name(),
            join.get_owner().get_name(), join.get_definition().get_name(),
            join.get_cell().get_name(), join.get_port_name(), through_type))
        return [Sym("TracePlugin"), ""]

    def joinable(self, current_region, next_region, through_type):
        print("MyDomainPlugin: joinable? from {} to {} ({})".format(
            current_region.get_name(), next_region.get_name(), through_type))
        return True

    @classmethod
    def gen_post_code(cls, file):
        pass

    def get_kind(self):
        return Sym("OutOfDomain")
