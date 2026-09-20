#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Port tecsgen plugin .rb files to .py using port_generate converters."""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from port_generate import (  # noqa: E402
    apply_post,
    convert_expr,
    convert_line,
    emit_body,
    preprocess_heredocs,
    rb_brace_to_do,
    rb_def_parens,
    rb_indent,
    skip_ruby_comment_block,
)

PLUGIN_HEADER = '''# -*- coding: utf-8 -*-
#
#  TECS Generator (Python port)
#   Ruby 版 tecslib/plugin/{rb_name} から移植
#

'''

IMPORTS_COMMON = '''
import sys

import tecsgen
from tecslib.core import globals as G
from tecslib.core.plugin import Plugin, CFile, AppFile
from tecslib.core.syntaxobj.cdlstring import CDLString
from tecslib.core.toplevel import dbgPrint
from tecslib.rubylib.symbol import Sym
from tecslib.rubylib import rb as rb_lib

TECSGEN = tecsgen.TECSGEN
'''


def convert_module_to_class(name, lines, start_i):
    """Convert ``module Name`` to ``class Name:`` mixin."""
    parts = []
    i = start_i
    body, i = emit_body(lines, i, 2, "class")
    parts.append("class {}:\n".format(name))
    for ln in body:
        parts.append("    " + ln + "\n" if ln else "\n")
    parts.append("\n")
    return parts, i


def convert_class(name, bases, lines, start_i):
    parts = []
    i = start_i
    body, i = emit_body(lines, i, 2, "class")
    base_str = ", ".join(bases) if bases else "object"
    parts.append("class {}({}):\n".format(name, base_str))
    for ln in body:
        parts.append("    " + ln + "\n" if ln else "\n")
    parts.append("\n")
    return parts, i


def parse_bases(stripped):
    m = re.match(r"class\s+(\w+)\s*<\s*(.+)$", stripped)
    if not m:
        return None, None
    name = m.group(1)
    bases = [b.strip() for b in m.group(2).split(",")]
    return name, bases


def port_file(rb_path, py_path, extra_imports=""):
    with open(rb_path, "r", encoding="utf-8") as f:
        raw = f.readlines()

    # strip license header comments but keep coding line
    lines = []
    for line in raw:
        lines.append(line)

    lines = preprocess_heredocs(lines)
    lines = rb_brace_to_do(lines)
    lines = rb_def_parens(lines)

    rb_name = os.path.basename(rb_path)
    parts = [PLUGIN_HEADER.format(rb_name=rb_name)]
    if extra_imports:
        parts.append(extra_imports)
    else:
        parts.append(IMPORTS_COMMON)

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if stripped == "=begin":
            i = skip_ruby_comment_block(lines, i + 1)
            continue

        if stripped.startswith("module "):
            m = re.match(r"module\s+(\w+)", stripped)
            mod_name = m.group(1)
            i += 1
            block, i = convert_module_to_class(mod_name, lines, i)
            parts.extend(block)
            while i < len(lines) and lines[i].strip() == "end":
                i += 1
            continue

        if stripped.startswith("class "):
            name, bases = parse_bases(stripped)
            if name is None:
                m = re.match(r"class\s+(\w+)", stripped)
                name = m.group(1)
                bases = ["Plugin"]
            i += 1
            block, i = convert_class(name, bases, lines, i)
            parts.extend(block)
            while i < len(lines) and lines[i].strip() == "end" and rb_indent(lines[i]) == 0:
                i += 1
            continue

        # top-level statements (TECSGEN::Makefile etc.)
        if stripped and not stripped.startswith("#"):
            if "require_tecsgen_lib" in stripped or "require " in stripped:
                i += 1
                continue
            if stripped.startswith("dbgPrint"):
                cl = convert_line(lines[i], "module")
                if cl:
                    parts.append(cl + "\n")
                i += 1
                continue
            if "TECSGEN::" in stripped or stripped.startswith("include "):
                i += 1
                continue

        i += 1

    text = "".join(parts)
    text = apply_post(text)
    text = fix_plugin_post(text, rb_name)
    os.makedirs(os.path.dirname(py_path), exist_ok=True)
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Wrote {} ({} lines)".format(py_path, text.count("\n")))


def fix_plugin_post(text, rb_name):
    """Plugin-specific fixes after apply_post."""
    text = text.replace("File.open", "open")
    text = text.replace("CFile.open", "CFile.open")
    text = re.sub(r"\bImport\.new\b", "Import.new", text)
    text = text.replace("STDERR <<", "sys.stderr.write(")
    # fix stderr writes missing paren
    text = re.sub(
        r'sys\.stderr\.write\(\s*"([^"]*)"\s*$',
        r'sys.stderr.write("\1")',
        text,
        flags=re.M,
    )
    text = text.replace("Namespace.get_root", "Namespace.get_root()")
    text = text.replace("MrubyBridgePluginArgProc", "MrubyBridgePluginArgProc")
    text = re.sub(r"(\w+)\.to_sym\b", r"Sym(\1)", text)
    text = re.sub(r"(\w+)\.to_s\b", r"rb_lib.to_s(\1)", text)
    text = re.sub(r"\.gsub!\(\s*/\\s/\s*,\s*\"\"\s*\)", ".replace(' ', '')", text)
    text = re.sub(r"\.gsub!\(\s*/\\A\"(.*)/,\s*'\\1'\s*\)", r"", text)  # noqa
    text = re.sub(r"\.split\s+'", ".split('", text)
    text = re.sub(r"\.split\s+\"", '.split("', text)
    text = re.sub(r"\.index\s+(\w+)", r".index(\1)", text)
    text = re.sub(r"\.include\?\(([^)]+)\)", r"(\1 in self.\1)", text)  # rough
    text = text.replace("Proc.new", "lambda")
    text = re.sub(r"^(\s+)when\s+", r"\1elif ", text, flags=re.M)
    text = re.sub(r"^(\s+)case\s+(.+)$", r"\1# case \2", text, flags=re.M)
    text = re.sub(r"^(\s+)else\s*$", r"\1else:", text, flags=re.M)
    # class variables on wrong class - MrubyBridgeSignaturePluginModule uses class attrs
    text = re.sub(
        r"^(\w+) = (\{)",
        r"\1 = \2",
        text,
        flags=re.M,
    )
    if "MrubyBridgeSignaturePlugin" in rb_name or "Module" in rb_name:
        text = re.sub(r"^celltypes = ", "celltypes = ", text, flags=re.M)
    return text


MRUBY_FILES = [
    ("MrubyBridgePlugin.rb", "MrubyBridgePlugin.py", """
from tecslib.plugin.MultiPlugin import MultiPlugin
from tecslib.plugin.SignaturePlugin import SignaturePlugin
from tecslib.plugin.CelltypePlugin import CelltypePlugin
from tecslib.plugin.CompositePlugin import CompositePlugin
from tecslib.plugin.CellPlugin import CellPlugin
from tecslib.core.toplevel import dbgPrint
"""),
    ("MrubyBridgeCompositePlugin.rb", "MrubyBridgeCompositePlugin.py", """
from tecslib.plugin.CompositePlugin import CompositePlugin
from tecslib.plugin.lib.MrubyBridgeCelltypePluginModule import MrubyBridgeCelltypePluginModule
from tecslib.core.toplevel import dbgPrint
"""),
    ("MrubyBridgeCelltypePlugin.rb", "MrubyBridgeCelltypePlugin.py", """
from tecslib.plugin.CompositePlugin import CompositePlugin
from tecslib.plugin.lib.MrubyBridgeCelltypePluginModule import MrubyBridgeCelltypePluginModule
from tecslib.core.toplevel import dbgPrint
"""),
    ("Mruby2CBridgePlugin.rb", "Mruby2CBridgePlugin.py", """
from tecslib.core import globals as G
from tecslib.core.plugin import CFile
from tecslib.plugin.SignaturePlugin import SignaturePlugin
"""),
    ("MrubyInfoBridgePlugin.rb", "MrubyInfoBridgePlugin.py", """
from tecslib.plugin.MultiPlugin import MultiPlugin
from tecslib.plugin.SignaturePlugin import SignaturePlugin
from tecslib.plugin.CellPlugin import CellPlugin
from tecslib.core.toplevel import dbgPrint
"""),
    ("lib/MrubyBridgeCelltypePluginModule.rb", "lib/MrubyBridgeCelltypePluginModule.py", """
import tecsgen
from tecslib.core import globals as G
from tecslib.core.componentobj.import_ import Import
from tecslib.core.componentobj.port import Port
from tecslib.core.syntaxobj.cdlstring import CDLString
from tecslib.core.toplevel import dbgPrint
from tecslib.rubylib.symbol import Sym

TECSGEN = tecsgen.TECSGEN
"""),
    ("lib/MrubyBridgeSignaturePluginModule.rb", "lib/MrubyBridgeSignaturePluginModule.py", """
from tecslib.core.types import IntType, CIntType, FloatType, CFloatType
from tecslib.rubylib.symbol import Sym
"""),
]

RB_ROOT = "/home/hiro22022/TECS_native/tecsgen/tecsgen/tecsgen/tecslib/plugin"
PY_ROOT = "/home/hiro22022/TECS_native/tecsgen/tecsgen-py/tecsgen/tecslib/plugin"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="rb basenames or paths")
    args = ap.parse_args()

    targets = MRUBY_FILES
    if args.files:
        targets = [(f, f.replace(".rb", ".py"), "") for f in args.files]

    for rb_rel, py_rel, extra in targets:
        rb_path = os.path.join(RB_ROOT, rb_rel)
        py_path = os.path.join(PY_ROOT, py_rel)
        port_file(rb_path, py_path, extra_imports=extra or None)

    # large signature plugins - hand-listed
    for rb_rel in (
        "MrubyBridgeSignaturePlugin.rb",
        "MrubyInfoBridgeSignaturePlugin.rb",
        "MrubyBridgeCellPlugin.rb",
        "MrubyInfoBridgeCellPlugin.rb",
    ):
        rb_path = os.path.join(RB_ROOT, rb_rel)
        py_path = os.path.join(PY_ROOT, rb_rel.replace(".rb", ".py"))
        extra = """
import sys

import tecsgen
from tecslib.core import globals as G
from tecslib.core.componentobj.import_ import Import
from tecslib.core.componentobj.namespace import Namespace
from tecslib.core.componentobj.port import Port
from tecslib.core.plugin import CFile, AppFile
from tecslib.core.syntaxobj.cdlstring import CDLString
from tecslib.core.toplevel import dbgPrint
from tecslib.rubylib.symbol import Sym
from tecslib.rubylib import rb as rb_lib

TECSGEN = tecsgen.TECSGEN
"""
        if "Signature" in rb_rel:
            extra += """
from tecslib.core.types import (
    BoolType, IntType, FloatType, VoidType, PtrType, StructType,
    CIntType, CFloatType,
)
from tecslib.plugin.SignaturePlugin import SignaturePlugin
from tecslib.plugin.lib.MrubyBridgeSignaturePluginModule import MrubyBridgeSignaturePluginModule
"""
        if "CellPlugin" in rb_rel and "Info" not in rb_rel:
            extra += """
from tecslib.plugin.CellPlugin import CellPlugin
"""
        if "InfoBridgeCell" in rb_rel:
            extra += """
from tecslib.plugin.CellPlugin import CellPlugin
from tecslib.core.componentobj.namespace import Namespace
"""
        port_file(rb_path, py_path, extra_imports=extra)


if __name__ == "__main__":
    main()
