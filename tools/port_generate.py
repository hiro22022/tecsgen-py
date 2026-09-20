#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Port generate.rb to generate.py / generate_celltype.py (structure-preserving)."""

import argparse
import re
import sys

RUBY_PATH = "/home/hiro22022/TECS_native/tecsgen/tecsgen/tecsgen/tecslib/core/generate.rb"
OUT_PATH = "/home/hiro22022/TECS_native/tecsgen/tecsgen-py/tecsgen/tecslib/core/generate.py"
CELLTYPE_OUT_PATH = (
    "/home/hiro22022/TECS_native/tecsgen/tecsgen-py/tecsgen/tecslib/core/generate_celltype.py"
)
CELLTYPE_RUBY_SLICE = (1184, 5278)  # lines 1185–5278 inclusive (class Celltype)

HEADER = r'''# -*- coding: utf-8 -*-
#
#  TECS Generator (Python port)
#      Generator for TOPPERS Embedded Component System
#
#   Copyright (C) 2008-2021 by TOPPERS Project TECS WG
#
#   このファイルは tecsgen (Ruby 版) の tecslib/core/generate.rb を
#   Python へ移植したものである．ライセンスは tecsgen.py の冒頭を参照のこと．

import os
import sys

import tecsgen
from tecslib.core import globals as G
from tecslib.core.messages import TECSMsg
from tecslib.core.componentobj.import_ import Import
from tecslib.core.componentobj.import_c import Import_C
from tecslib.core.componentobj.namespace import Namespace
from tecslib.core.componentobj.region import Region
from tecslib.core.componentobj.signature import Signature
from tecslib.core.componentobj.celltype import Celltype
from tecslib.core.componentobj.domaintype import DomainType
from tecslib.core.componentobj.classtype import ClassType
from tecslib.core.syntaxobj.typedef import Typedef
from tecslib.core.types import StructType
from tecslib.core.ctypes import CType
from tecslib.core.syntaxobj.node import Node
from tecslib.core.toplevel import dbgPrint, print_exception
from tecslib.rubylib.reopen import reopen

TECSGEN = tecsgen.TECSGEN


class _AppFileIO(object):
    """Ruby IO#print / #printf 相当 (AppFile が返すファイルオブジェクト)"""

    def __init__(self, f):
        self.file = f

    def print(self, s="", end=""):
        self.file.write(s)

    def printf(self, fmt, *args):
        self.file.write(fmt % args)

    def puts(self, s=""):
        self.file.write(s)
        self.file.write("\n")

    def close(self):
        self.file.close()


'''

APPFILE = r'''
# Appendable File（追記可能ファイル）
class AppFile(object):
    # 開いたファイルのリスト
    file_name_list = {}

    @classmethod
    def open(cls, name):
        if G.force_overwrite:
            real_name = name
        else:
            real_name = name + ".tmp"

        mode_enc = ":" + G.Ruby19_File_Encode

        # 既に開いているか？
        if cls.file_name_list.get(name):
            mode = "a" + mode_enc
            # 追記モードで開く
            f = open(real_name, mode)
        else:
            mode = "w" + mode_enc
            # 新規モードで開く（既にあれば、サイズを０にする）
            f = open(real_name, mode)
            cls.file_name_list[name] = True
        # File クラスのオブジェクトを返す
        return _AppFileIO(f)

    @classmethod
    def update(cls):
        if G.force_overwrite:
            return

        for name, boo in list(cls.file_name_list.items()):
            b_identical = False
            if os.path.isfile(name) and os.access(name, os.R_OK):
                with open(name, "r", encoding="latin-1") as oldf:
                    old_lines = oldf.readlines()
                with open(name + ".tmp", "r", encoding="latin-1") as newf:
                    new_lines = newf.readlines()
                if len(old_lines) == len(new_lines):
                    i = 0
                    length = len(old_lines)
                    while i < length:
                        if old_lines[i] != new_lines[i]:
                            break
                        i += 1
                    if i == length:
                        b_identical = True
            if b_identical == False:
                if G.verbose:
                    print("{} changed".format(name))
                    print("renaming '{}.tmp' => '{}'".format(name, name))
                os.rename(name + ".tmp", name)
            else:
                if G.verbose:
                    print("{} not changed".format(name))
                os.remove(name + ".tmp")


class MemFile(object):
    def __init__(self):
        self.string = ""

    def print(self, str):
        self.string += str

    def get_string(self):
        return self.string


'''

REOPEN = {
    "Namespace", "Typedef", "StructType", "Signature", "Celltype",
    "Region", "DomainType", "ClassType",
}

SKIP_CLASS = {"AppFile", "MemFile"}

DOLLAR = {
    "gen", "gen_base", "generating_region", "force_overwrite", "verbose",
    "dryrun", "h_suffix", "c_suffix", "target", "import_path", "define",
    "arguments", "ram_initializer", "generate_all_template", "generate_no_template",
    "debug", "Ruby19_File_Encode", "rom", "region_list", "unopt", "show_tree",
}


def preprocess_heredocs(lines):
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.search(r'(\s*)(\S.*?)\.print\s+<<EOT\s*$', line)
        if m:
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != "EOT":
                body.append(lines[i].rstrip("\n"))
                i += 1
            text = "\\n".join(body)
            if text and not text.endswith("\\n"):
                text += "\\n"
            text_py = re.sub(r"#\{([^}]+)\}", r"{\1}", text)
            indent = m.group(1)
            if "#{" in line or re.search(r"\{[a-zA-Z_]", text_py):
                out.append('{}f.print(f"""{}""")\n'.format(indent, text_py))
            else:
                out.append('{}f.print("""{}""")\n'.format(indent, text_py))
            i += 1
            continue
        out.append(line)
        i += 1
    return out


def rb_indent(line):
    return len(line) - len(line.lstrip())


def rb_brace_to_do(lines):
    """Convert .each { |x| and Proc.new { |x| blocks to do/end for the Python converter."""
    out = []
    stack = []  # indent levels of open brace blocks
    for line in lines:
        stripped = line.strip()
        ind = rb_indent(line)

        m = re.search(r"(\.each\s*)\{(\s*\|[^}]+\|)\s*$", line)
        if m:
            line = line[: m.start(1)] + m.group(1).rstrip() + " do" + m.group(2) + "\n"
            stack.append(ind)
            out.append(line)
            continue

        m = re.search(r"Proc\.new\s*\{\s*$", line)
        if m:
            line = line.replace("Proc.new{", "Proc.new do").replace("Proc.new {", "Proc.new do")
            if not line.rstrip().endswith("|"):
                line = line.rstrip() + " |\n"
            stack.append(ind)
            out.append(line)
            continue

        m = re.search(r"Proc\.new\s*\{(\s*\|[^}]+\|)\s*$", line)
        if m:
            line = line[: m.start()] + "Proc.new do" + m.group(1) + "\n"
            stack.append(ind)
            out.append(line)
            continue

        m = re.search(r"(\w+)\s*\{\s*\|([^|]+),([^|]+)\|\s*$", line)
        if m and ".each" in line:
            pass  # handled above

        if stripped == "}" and stack:
            if ind <= stack[-1]:
                line = line.replace("}", "end", 1)
                stack.pop()
        out.append(line)
    return out


def rb_def_parens(lines):
    """Normalize ``def foo bar`` while keeping Ruby indentation (required by emit_body)."""
    out = []
    for line in lines:
        stripped = line.strip()
        indent = line[: len(line) - len(line.lstrip())]
        m = re.match(r"def (\w+)\s+(\w+)\s*$", stripped)
        if m and not stripped.startswith("def self."):
            out.append("{}def {}({}):\n".format(indent, m.group(1), m.group(2)))
            continue
        m = re.match(r"def (\w+)\s+&(\w+)", stripped)
        if m:
            out.append("{}def {}({}=None):\n".format(indent, m.group(1), m.group(2)))
            continue
        out.append(line)
    return out


def convert_args(args):
    args = args.strip()
    if not args:
        return ""
    parts = []
    for p in args.split(","):
        p = p.strip()
        if p.startswith("&"):
            p = p[1:] + "=None"
        if "=" in p:
            n, d = p.split("=", 1)
            parts.append("{}={}".format(n.strip(), convert_expr(d.strip())))
        else:
            parts.append(p)
    return ", ".join(parts)


def convert_expr(e):
    s = e
    for name in sorted(DOLLAR, key=len, reverse=True):
        s = re.sub(r"\$" + name + r"\b", "G." + name, s)
    s = re.sub(r"\$(\w+)", r"G.\1", s)
    s = re.sub(r"@@(\w+)", r"Namespace.\1", s)
    s = re.sub(r"@(\w+)", r"self.\1", s)
    s = re.sub(r"\bnil\b", "None", s)
    s = re.sub(r"\btrue\b", "True", s)
    s = re.sub(r"\bfalse\b", "False", s)
    s = re.sub(r"instance_of\?\s*(\w+)", r"type(self) is \1", s)
    s = re.sub(r"(\w+)\.kind_of\?\s*\(\s*(\w+)\s*\)", r"isinstance(\1, \2)", s)
    s = re.sub(r"kind_of\?\s*\(\s*(\w+)\s*\)", r"isinstance(self, \1)", s)
    s = re.sub(r"(\w+)\.length\b", r"len(\1)", s)
    s = s.replace("TECSGEN::", "TECSGEN.")
    s = re.sub(r"&&", " and ", s)
    s = re.sub(r"\|\|", " or ", s)
    s = re.sub(r"(\w+)::(\w+)", r"\1.\2", s)
    s = re.sub(r"\b([a-zA-Z_][\w]*)\?", r"\1", s)
    s = re.sub(r"\b([a-zA-Z_][\w]*)\!", r"\1_bang", s)
    return s


def convert_call_line(stripped):
    """Convert a Ruby statement line to Python."""
    s = stripped
    if s.startswith("#"):
        return s

    # next if / return if
    m = re.match(r"next if (.+)$", s)
    if m:
        return "continue  # if {}".format(convert_expr(m.group(1)))
    m = re.match(r"return if (.+)$", s)
    if m:
        return "if {}:\n            return".format(convert_expr(m.group(1)))

    # dbgPrint "..."
    m = re.match(r'dbgPrint\s+"([^"]*)"\s*$', s)
    if m:
        return 'dbgPrint("{}")'.format(m.group(1))
    m = re.match(r'dbgPrint\s+(.+)$', s)
    if m:
        inner = convert_expr(m.group(1))
        return "dbgPrint({})".format(inner)

    s = convert_expr(s)

    # bare method call without ()
    if re.match(r"^[a-z_][a-z0-9_]*$", s, re.I):
        return s + "()"

    # f.print string
    s = re.sub(
        r'(\w+)\.print\s+"([^"]*)"\s*$',
        r'\1.print("\2")',
        s,
    )
    s = re.sub(
        r'(\w+)\.print\s+\((.+)\)\s*$',
        r'\1.print(\2)',
        s,
    )
    if re.search(r"\.print\s+", s) and not s.rstrip().endswith(")"):
        s = re.sub(r"\.print\s+(.+)$", r".print(\1)", s)

    s = re.sub(r"\.printf\s+", ".printf(", s)
    if ".printf(" in s and s.count("(") > s.count(")"):
        s += ")"

    s = s.replace("cdl_error(", "self.cdl_error(")
    s = re.sub(r"\bprint_exception\s+", "print_exception(", s)
    if "print_exception(" in s and not s.endswith(")"):
        s += ")"

    # method calls foo bar -> foo(bar)  (single identifier arg)
    s = re.sub(r"^([a-z_][\w]*)\s+([a-z_][\w.]*)$", r"\1(\2)", s, flags=re.I)

    m = re.match(r"^(.+?) if (.+)$", s)
    if m and not m.group(1).strip().startswith("if "):
        return "if {}:\n            {}".format(
            convert_expr(m.group(2)), m.group(1).strip())

    m = re.match(r"^(.+?) \? (.+?) : (.+)$", s)
    if m:
        return "{} if {} else {}".format(
            convert_expr(m.group(2).strip()),
            convert_expr(m.group(1).strip()),
            convert_expr(m.group(3).strip()),
        )

    return s


def convert_each_header(stripped):
    """If line opens a Ruby .each block, return a Python ``for ...:`` header."""
    m = re.match(r"(.+)\.each\s+do\s*\|([^|]+),([^|]+)\|\s*$", stripped)
    if m:
        return "for {}, {} in {}.items():".format(
            m.group(2).strip(), m.group(3).strip(), convert_expr(m.group(1)))
    m = re.match(r"(.+)\.each\s+do\s*\|([^|]+)\|\s*$", stripped)
    if m:
        return "for {} in {}:".format(m.group(2).strip(), convert_expr(m.group(1)))
    m = re.match(r"(.+)\.each\s*\{\s*\|([^|]+),([^|]+)\|\s*$", stripped)
    if m:
        return "for {}, {} in {}.items():".format(
            m.group(2).strip(), m.group(3).strip(), convert_expr(m.group(1)))
    m = re.match(r"(.+)\.each\s*\{\s*\|([^|]+)\|\s*$", stripped)
    if m:
        return "for {} in {}:".format(m.group(2).strip(), convert_expr(m.group(1)))
    m = re.match(
        r"(.+)\.each_param\s*\{\s*\|([^|]+),([^|]+),([^|]+)\|\s*$", stripped)
    if m:
        return "for {}, {}, {} in {}:".format(
            m.group(2).strip(),
            m.group(3).strip(),
            m.group(4).strip(),
            convert_expr(m.group(1)),
        )
    return None


def convert_line(line, ctx):
    """ctx: 'module' | 'class'"""
    stripped = line.strip()
    if stripped == "":
        return ""
    if stripped.startswith("#"):
        return stripped

    # class var
    m = re.match(r"@@(\w+)\s*=\s*(.+)$", stripped)
    if m and ctx == "class":
        return "{} = {}".format(m.group(1), convert_expr(m.group(2)))

    m = re.match(r"def\s+(\w+)\s*\((.*)\)\s*$", stripped)
    if m and ctx == "class" and not stripped.startswith("def self."):
        name = m.group(1)
        a = convert_args(m.group(2))
        if name == "initialize":
            name = "__init__"
        if a:
            return "def {}(self, {}):".format(name, a)
        return "def {}(self):".format(name)

    m = re.match(r"def self\.(\w+)\((.*)\)\s*$", stripped)
    if m:
        a = convert_args(m.group(2))
        if a:
            return "@classmethod\ndef {}(cls, {}):".format(m.group(1), a)
        return "@classmethod\ndef {}(cls):".format(m.group(1))

    m = re.match(r"def (\w+)\s*$", stripped)
    if m and ctx == "class":
        return "def {}(self):".format(m.group(1))

    m = re.match(r"def (\w+)\s+(\w+)\s*$", stripped)
    if m and ctx == "class":
        return "def {}(self, {}):".format(m.group(1), m.group(2))

    m = re.match(r"def (\w+)\s+&(\w+)", stripped)
    if m:
        if ctx == "class":
            return "def {}(self, {}=None):".format(m.group(1), m.group(2))
        return "def {}({}=None):".format(m.group(1), m.group(2))

    m = re.match(r"def (\w+)\((.*)\)\s*$", stripped)
    if m:
        name = m.group(1)
        a = convert_args(m.group(2))
        if name == "initialize":
            name = "__init__"
        if ctx == "class":
            pre = "self"
            if a:
                return "def {}({}, {}):".format(name, pre, a)
            return "def {}({}):".format(name, pre)
        if a:
            return "def {}({}):".format(name, a)
        return "def {}():".format(name)

    if stripped == "begin":
        return "try:"
    if stripped.startswith("rescue =>"):
        return "except Exception as {}:".format(stripped.split("=>")[1].strip())

    # each one-liner
    m = re.match(r"(.+)\.each\s*\{\s*\|([^|]+)\|\s*(.+)\s*\}\s*$", stripped)
    if m:
        v = m.group(2).strip()
        return "for {} in {}:\n            {}".format(
            v, convert_expr(m.group(1)), convert_call_line(m.group(3).strip()))

    m = re.match(r"(.+)\.each\s+do\s*\|([^|]+)\|\s*$", stripped)
    if m:
        return "for {} in {}:".format(m.group(2).strip(), convert_expr(m.group(1)))

    m = re.match(r"(.+)\.each\s+do\s*\|([^|]+),([^|]+)\|\s*$", stripped)
    if m:
        return "for {}, {} in {}.items():".format(
            m.group(2).strip(), m.group(3).strip(), convert_expr(m.group(1)))

    m = re.match(r"(.+)\.each\s*\{\s*\|([^|]+),([^|]+)\|\s*$", stripped)
    if m:
        return "for {}, {} in {}.items():".format(
            m.group(2).strip(), m.group(3).strip(), convert_expr(m.group(1)))

    # while
    m = re.match(r"while\s+(.+?)\s+do\s*$", stripped)
    if m:
        return "while {}:".format(convert_expr(m.group(1)))
    m = re.match(r"while\s+(.+)$", stripped)
    if m and not stripped.endswith("{"):
        return "while {}:".format(convert_expr(m.group(1)))

    # if / elsif / unless
    if stripped.startswith("unless "):
        rest = stripped[7:]
        if rest.endswith(" then"):
            rest = rest[:-5]
        return "if not {}:".format(convert_expr(rest))
    if stripped.startswith("elsif "):
        rest = stripped[6:]
        if rest.endswith(" then"):
            rest = rest[:-5]
        return "elif {}:".format(convert_expr(rest))
    if stripped.startswith("if "):
        rest = stripped[3:]
        if rest.endswith(" then"):
            rest = rest[:-5]
        return "if {}:".format(convert_expr(rest))
    if stripped.startswith("else"):
        return "else:"
    if stripped.startswith("elsif "):
        rest = stripped[6:]
        if rest.endswith(" then"):
            rest = rest[:-5]
        return "elif {}:".format(convert_expr(rest))

    s = stripped
    s = re.sub(r"^!", "not ", s)
    if s.endswith(" then"):
        s = s[:-5] + ":"
    elif s.endswith(" then:"):
        pass

    if stripped == "end":
        return None

    if stripped == "return":
        return "return"
    m = re.match(r"return\s+(.+)$", stripped)
    if m:
        return "return {}".format(convert_expr(m.group(1)))

    s = re.sub(
        r"Proc\.new\s*do\s*\|(\w+)\|\s*$",
        r"lambda \1: ",
        s,
    )
    s = re.sub(
        r"Proc\.new\s*\{\s*\|(\w+)\|\s*(.+)\s*\}",
        r"lambda \1: \2",
        s,
    )
    s = re.sub(r"Proc\.new\s*\{\s*\|\s*\|\s*(.+)\s*\}", r"lambda: \1", s)
    s = s.replace(".call(", "(")

    return convert_call_line(s)


def skip_ruby_comment_block(lines, i):
    """Skip =begin … =end; return index after =end."""
    while i < len(lines):
        if lines[i].strip() == "=end":
            return i + 1
        i += 1
    return i


def emit_body(lines, start, base_indent, ctx):
    """Parse from start until `end` at base_indent. Returns (py_lines, next_i)."""
    out = []
    i = start
    while i < len(lines):
        line = lines[i]
        ind = rb_indent(line)
        stripped = line.strip()
        if stripped == "end" and ind < base_indent:
            return out, i + 1

        if stripped == "=begin":
            i = skip_ruby_comment_block(lines, i + 1)
            continue

        if ind < base_indent and stripped != "":
            if stripped == "end" or stripped.startswith("class ") or stripped.startswith("def "):
                return out, i
            if stripped.startswith("#"):
                out.append(stripped)
                i += 1
                continue
            cl = convert_line(" " * base_indent + stripped, ctx)
            if cl is not None:
                out.append(cl.lstrip())
            i += 1
            continue

        if stripped == "":
            out.append("")
            i += 1
            continue

        if stripped == "end":
            i += 1
            continue

        if stripped == "}":
            i += 1
            continue

        block_open = (
            stripped == "begin"
            or stripped.startswith("if ")
            or stripped.startswith("unless ")
            or stripped.startswith("elsif ")
            or stripped.startswith("while ")
            or re.search(r"\.each\s*\{\s*\|", stripped)
            or re.search(r"\.each do \|", stripped)
            or re.search(r"\.each_param\s*\{\s*\|", stripped)
        )
        if block_open:
            hdr = convert_each_header(stripped) or convert_line(line, ctx)
            if hdr is None:
                i += 1
                continue
            out.append(hdr)
            i += 1
            if hdr.startswith("for ") and "\n" in hdr:
                continue
            if hdr.endswith(":"):
                inner, i = emit_body(lines, i, base_indent + 2, ctx)
                for ln in inner:
                    out.append("    " + ln if ln else ln)
            continue

        if stripped.startswith("def ") or stripped.startswith("def self."):
            hdr = convert_line(line, ctx)
            if hdr is None:
                i += 1
                continue
            out.append(hdr)
            i += 1
            inner, i = emit_body(lines, i, ind + 2, ctx)
            for ln in inner:
                out.append("    " + ln if ln else ln)
            continue

        cl = convert_line(line, ctx)
        if cl is not None:
            out.append(cl)
        i += 1

    return out, i


def port():
    with open(RUBY_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start = 0
    for i, line in enumerate(lines):
        if line.startswith("def ifdef_macro_only"):
            start = i
            break
    lines = preprocess_heredocs(lines[start:])
    lines = rb_brace_to_do(lines)
    lines = rb_def_parens(lines)

    parts = [HEADER, APPFILE]
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("class "):
            m = re.match(r"class\s+(\w+)", stripped)
            cname = m.group(1)
            if cname == "Celltype":
                i += 1
                while i < len(lines) and not (lines[i].strip() == "end" and rb_indent(lines[i]) == 0):
                    i += 1
                i += 1
                continue
            if cname in SKIP_CLASS:
                i += 1
                while i < len(lines) and not (lines[i].strip() == "end" and rb_indent(lines[i]) == 0):
                    i += 1
                i += 1
                continue
            if cname in REOPEN:
                parts.append("\n@reopen({})\nclass _:\n".format(cname))
                ctx = "class"
            else:
                i += 1
                continue
            i += 1
            body, i = emit_body(lines, i, 2, ctx)
            for ln in body:
                parts.append("    " + ln + "\n" if ln else "\n")
            parts.append("\n")
            continue

        if stripped.startswith("def "):
            hdr = convert_line(lines[i], "module")
            parts.append(hdr + "\n")
            i += 1
            body, i = emit_body(lines, i, 2, "module")
            for ln in body:
                parts.append("    " + ln + "\n" if ln else "\n")
            parts.append("\n")
            continue
        i += 1

    text = "".join(parts)
    text = apply_post(text)
    text += "\nimport tecslib.core.generate_celltype  # noqa: F401\n"
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print("lines", text.count("\n"), file=sys.stderr)


CELLTYPE_HEADER = '''# -*- coding: utf-8 -*-
# Celltype generate methods (from generate.rb)

import tecsgen
from tecslib.core import globals as G
from tecslib.core.messages import TECSMsg
from tecslib.core.componentobj.celltype import Celltype
from tecslib.core.componentobj.region import Region
from tecslib.core.componentobj.signature import Signature
from tecslib.core.syntaxobj.node import Node
from tecslib.core.toplevel import dbgPrint, print_exception
from tecslib.core.generate import (
    AppFile, MemFile, print_note, print_indent,
    ifdef_macro_only, ifndef_macro_only, endif_macro_only,
    ifndef_cb_type_only, ifdef_cb_type_only, endif_cb_type_only,
    begin_extern_C, end_extern_C,
)
from tecslib.rubylib.reopen import reopen
from tecslib.rubylib.symbol import Sym

TECSGEN = tecsgen.TECSGEN

'''


def load_celltype_ruby_lines():
    with open(RUBY_PATH, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    lo, hi = CELLTYPE_RUBY_SLICE
    lines = all_lines[lo:hi]
    lines = preprocess_heredocs(lines)
    lines = rb_brace_to_do(lines)
    lines = rb_def_parens(lines)
    return lines


def port_celltype(out_path):
    lines = load_celltype_ruby_lines()
    parts = [CELLTYPE_HEADER, "\n@reopen(Celltype)\nclass _:\n"]
    body, _i = emit_body(lines, 1, 2, "class")
    for ln in body:
        parts.append("    " + ln + "\n" if ln else "\n")
    ct_text = apply_post("".join(parts))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(ct_text)
    print(ct_text.count("\n"), file=sys.stderr)
    return ct_text


def apply_post(text):
    # post fixes
    fixes = [
        (".get_n_cells ==", ".get_n_cells() =="),
        (".get_n_cells !=", ".get_n_cells() !="),
        (".get_n_cells >", ".get_n_cells() >"),
        (".get_name ", ".get_name() "),
        (".get_name\n", ".get_name()\n"),
        ("Import_C.get_header_list2", "Import_C.get_header_list2()"),
        ("Import.get_list", "Import.get_list()"),
        ("Import_C.get_header_list", "Import_C.get_header_list()"),
        ("Region.get_link_roots", "Region.get_link_roots()"),
        ("Celltype.get_domain_class_roots_total", "Celltype.get_domain_class_roots_total()"),
        ("TECSGEN.is_absolute_path?", "TECSGEN.is_absolute_path"),
        ("TECSGEN.subst_tecspath", "TECSGEN.subst_tecspath"),
        ("Generator.", "Generator."),  # noop
    ]
    for a, b in fixes:
        text = text.replace(a, b)

    text = re.sub(r'^(\s+)\}\s*$', '', text, flags=re.M)
    # dbgPrint / strings: leave #{...} in Ruby strings to manual f-strings; only fix dbgPrint patterns
    text = re.sub(
        r'dbgPrint\("([^"]*)#\{([^}]+)\}([^"]*)"\)',
        lambda m: 'dbgPrint("{}".format({}))'.format(
            m.group(1) + "{}" + m.group(3), convert_expr(m.group(2))),
        text,
    )
    # Do not turn ``tecslib.core.generate`` into ``tecslib.core.generate()``.
    text = re.sub(r'(?<!core)\.generate\b(?!\()', '.generate()', text)
    text = re.sub(r'(?<!core)\.generate_post\b(?!\()', '.generate_post()', text)
    text = re.sub(r'(?<![.\w])gen_([a-z_][\w]*)\(\)', r'self.gen_\1()', text)
    text = re.sub(r'(?<![.\w])gen_([a-z_][\w]*)\b(?!\()', r'self.gen_\1()', text)
    text = re.sub(r'(?<![.\w])get_domain_type\b(?!\()', r'self.get_domain_type()', text)
    text = re.sub(r'(?<![.\w])get_class_type\b(?!\()', r'self.get_class_type()', text)
    text = text.replace(".keys", ".keys()")
    text = text.replace(".keys()()", ".keys()")
    text = re.sub(r'\.eachdo \|([^|]+)\|', r'.each do |\1|', text)
    text = re.sub(r'print ([a-z_.]+), " "', r'print(\1, end=" ")', text)
    text = re.sub(r'print "\n"', r'print("\\n")', text)
    text = re.sub(r'print "\n"', r'print("\\n")', text)
    text = re.sub(r'(\w+)\.get_type_str\b(?!\()', r'\1.get_type_str()', text)
    text = re.sub(r'(\w+)\.get_type_str_post\b(?!\()', r'\1.get_type_str_post()', text)
    text = re.sub(r'(\w+)\.get_global_name\b(?!\()', r'\1.get_global_name()', text)
    text = re.sub(r'(\w+)\.get_name\b(?!\()', r'\1.get_name()', text)
    text = re.sub(r'(\w+)\.eval_const2\b(?!\()', r'\1.eval_const2', text)
    text = re.sub(r'\bend\(\)\s*$', '', text, flags=re.M)
    text = re.sub(r'\.need_CB_initializer\b(?!\()', '.need_CB_initializer()', text)
    text = re.sub(r'\.need_generate\b(?!\()', '.need_generate()', text)
    text = re.sub(r'\.is_all_entry_inline\b(?!\()', '.is_all_entry_inline()', text)
    text = re.sub(r'\.is_active\b(?!\()', '.is_active()', text)
    text = re.sub(r'\.is_root\b(?!\()', '.is_root()', text)
    text = re.sub(r'\.is_link_root\b(?!\()', '.is_link_root()', text)
    text = re.sub(r'TECSMsg\.get\(\s*:(\w+)\s*\)', r'TECSMsg.get("\1")', text)
    text = re.sub(r'f\.print\s+TECSMsg', 'f.print(TECSMsg', text)
    text = re.sub(r'(\w+)\.gen_gh\s+(\w+)\s*$', r'\1.gen_gh(\2)', text, flags=re.M)
    text = re.sub(r'(\w+)\.close\s*$', r'\1.close()', text, flags=re.M)
    text = re.sub(r'f\.printf\(\s*"([^"]+)"\s*,\s*([^)]+)\)', r'f.printf("\1", \2)', text)

    # indent bare defs inside @reopen class _ blocks
    lines = text.splitlines(keepends=True)
    out = []
    in_reopen = False
    for line in lines:
        if line.startswith("@reopen("):
            in_reopen = True
            out.append(line)
            continue
        if in_reopen and line.startswith("class _:"):
            out.append(line)
            continue
        if in_reopen and line.startswith("@reopen("):
            in_reopen = True
            out.append(line)
            continue
        if in_reopen and line.startswith("class ") and not line.startswith("class _:"):
            in_reopen = False
        if in_reopen and (line.startswith("def ") or line.startswith("@classmethod")):
            out.append("    " + line)
            continue
        if in_reopen and line.strip() and not line.startswith(" ") and not line.startswith("#"):
            if line.startswith("@reopen("):
                in_reopen = True
                out.append(line)
                continue
            out.append("    " + line)
            continue
        out.append(line)
    text = "".join(out)
    return text


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Convert generate.rb sections to Python.")
    ap.add_argument(
        "-o",
        "--output",
        default=CELLTYPE_OUT_PATH,
        help="Output path for generate_celltype.py (default: %(default)s)",
    )
    ap.add_argument(
        "--full-generate",
        action="store_true",
        help="Also emit tecslib/core/generate.py (overwrites existing file)",
    )
    args = ap.parse_args()
    port_celltype(args.output)
    if args.full_generate:
        port()
