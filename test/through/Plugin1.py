# -*- coding: utf-8 -*-
# through テスト用プラグイン（Ruby 版 Plugin1.rb の移植）

from tecslib.plugin.ThroughPlugin import ThroughPlugin
from tecslib.rubylib.symbol import Sym


class Plugin1(ThroughPlugin):

    generated_celltype = {}

    def __init__(self, cell_name, plugin_arg, next_cell, next_cell_port_name,
                 next_cell_port_subscript, signature, celltype, caller_cell):
        super().__init__(cell_name, plugin_arg, next_cell, next_cell_port_name,
                         next_cell_port_subscript, signature, celltype, caller_cell)
        self.cell_name = cell_name
        self.next_cell = next_cell
        self.next_cell_port_name = next_cell_port_name
        self.next_cell_port_subscript = next_cell_port_subscript
        self.signature = signature
        self.entry_port_name = Sym("throughEntry")
        # print( "Plugin1.new( '#{cell_name}', '#{plugin_arg}', '#{next_cell.get_name}', '#{next_cell_port_name}', #{celltype.get_name} )\n" )

    def get_cell_name(self):
        return self.cell_name

    def get_through_entry_port_name(self):
        return self.entry_port_name

#  def gen_plugin_decl_code( file )
#
#    ct_name = "Plugin1_#{@signature.get_name}"
#
#    if @@generated_celltype[ ct_name ] == nil then
#      @@generated_celltype[ ct_name ] = [ self ]
#    else
#      @@generated_celltype[ ct_name ] << self
#    end
#
#    file.print <<EOT
#celltype tPlugin1 {
#  entry #{@signature.get_name} #{@entry_port_name};
#  call #{@signature.get_name} cCall;
#};
#EOT
#
#  end

    def gen_through_cell_code(self, file):

        self.gen_plugin_decl_code(file)
        if self.next_cell_port_subscript:
            subscript = '[' + str(self.next_cell_port_subscript) + ']'
        else:
            subscript = ""

        file.print(
            "cell tPlugin1_{sig} {cell} {{\n"
            "  cCall = {next}.{ep}{sub};\n"
            "}};\n".format(
                sig=self.signature.get_name(),
                cell=self.cell_name,
                next=self.next_cell.get_name(),
                ep=self.next_cell_port_name,
                sub=subscript)
        )
