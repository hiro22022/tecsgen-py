#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""racc (bnf.y.rb) の rule 節を PLY の p_ 関数群へ変換する。

使い方:
  python3 tools/racc_to_ply.py ../tecsgen/tecsgen/tecslib/core/bnf.y.rb \\
      > tecsgen/tecslib/core/_bnf_rules_gen.py
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict


def extract_rule(src: str) -> str:
    m = re.search(r"^rule\n(.*)^end$", src, re.M | re.S)
    if not m:
        raise SystemExit("no rule section")
    return m.group(1)


def collect_action(lines: list[str], i: int, first: str) -> tuple[str, int]:
    """'{ ... }' を深さ追跡で集め、(body, next_index) を返す。first は '{' 以降。"""
    depth = 1 + first.count("{") - first.count("}")
    buf = first + "\n"
    if depth <= 0:
        body = re.sub(r"\}\s*(#.*)?$", "", first)
        return body, i
    i += 1
    while i < len(lines) and depth > 0:
        buf += lines[i] + "\n"
        depth += lines[i].count("{") - lines[i].count("}")
        i += 1
    body = re.sub(r"\}\s*\Z", "", buf, flags=re.S)
    return body, i - 1


PROD_NAME_RE = re.compile(r"^([A-Za-z_][\w]*)\s*(?:#.*)?$")


def is_production_name(line: str) -> bool:
    if not line or line.startswith((" ", "\t")):
        return False
    return bool(PROD_NAME_RE.match(line))


def production_name(line: str) -> str | None:
    if not is_production_name(line):
        return None
    return PROD_NAME_RE.match(line).group(1)


def merge_production(productions, name, alts):
    for i_p, (n, a) in enumerate(productions):
        if n == name:
            productions[i_p] = (n, a + alts)
            return
    productions.append((name, alts))


def skip_blank_comments(lines, j):
    while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
        j += 1
    return j


def parse_productions(rule: str):
    """productions: [(name, [(rhs_tokens, action), ...]), ...]
    mid-rule action は synthetic 非終端 mra_N に切り出す。
    戻り値の第3要素に mra 定義 [(mra_name, action), ...] を付す。
    """
    lines = [ln.rstrip() for ln in rule.splitlines()]
    productions = []
    mra_defs = []  # (name, action_ruby)
    mra_counter = 0
    i = 0

    def new_mra(action):
        nonlocal mra_counter
        mra_counter += 1
        name = f"mra_{mra_counter}"
        mra_defs.append((name, action))
        return name

    while i < len(lines):
        line = lines[i]
        # NAME : alt...  （同一行）
        m_inline = re.match(r"^([A-Za-z_][\w]*)\s*:(.*)$", line)
        if m_inline and not line.startswith((" ", "\t")):
            name = m_inline.group(1)
            rest = m_inline.group(2).strip()
            alts = []
            pieces = split_top_level_alts(rest) if rest else [""]
            first = True
            for piece in pieces:
                if not piece and not first:
                    continue
                rhs_tokens, action, i, _ = parse_one_alt(
                    lines, i, piece, first, new_mra
                )
                first = False
                alts.append((rhs_tokens, action))
            # 続きの | alt 行
            i += 1
            while i < len(lines):
                l = lines[i]
                if is_production_name(l) or re.match(r"^([A-Za-z_][\w]*)\s*:", l):
                    break
                if re.match(r"^#{4,}", l):
                    break
                am = re.match(r"^\s*\|\s*(.*)$", l)
                if am:
                    for piece in split_top_level_alts(am.group(1)):
                        rhs_tokens, action, i, _ = parse_one_alt(
                            lines, i, piece, True, new_mra
                        )
                        alts.append((rhs_tokens, action))
                    i += 1
                    continue
                break
            if alts:
                merge_production(productions, name, alts)
            continue

        name = production_name(line)
        if not name:
            i += 1
            continue
        i += 1
        alts = []
        while i < len(lines):
            l = lines[i]
            if is_production_name(l) or re.match(r"^([A-Za-z_][\w]*)\s*:", l):
                break
            if re.match(r"^#{4,}", l):
                break

            am = re.match(r"^\s*([|:])\s*(.*)$", l)
            if not am:
                i += 1
                continue

            rest_line = am.group(2)
            pieces = split_top_level_alts(rest_line)
            first = True
            for piece in pieces:
                rhs_tokens, action, i, _ = parse_one_alt(
                    lines, i if first else i, piece, first, new_mra
                )
                first = False
                alts.append((rhs_tokens, action))
            i += 1
            if i < len(lines) and (
                is_production_name(lines[i]) or re.match(r"^([A-Za-z_][\w]*)\s*:", lines[i])
            ):
                break
        if alts:
            merge_production(productions, name, alts)
    return productions, mra_defs


def split_top_level_alts(s: str) -> list[str]:
    """'A { x } | B { y }' → ['A { x }', 'B { y }']。先頭の空は除く。"""
    parts = []
    buf = []
    depth = 0
    in_q = None
    i = 0
    while i < len(s):
        c = s[i]
        if in_q:
            buf.append(c)
            if c == "\\" and i + 1 < len(s):
                buf.append(s[i + 1])
                i += 2
                continue
            if c == in_q:
                in_q = None
            i += 1
            continue
        if c in "'\"":
            in_q = c
            buf.append(c)
            i += 1
            continue
        if c == "{":
            depth += 1
            buf.append(c)
            i += 1
            continue
        if c == "}":
            depth -= 1
            buf.append(c)
            i += 1
            continue
        if c == "|" and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts or [""]


def find_action_brace(text: str):
    """クォート外の最初の '{' を探し (before, after_or_None) を返す。"""
    in_q = None
    i = 0
    while i < len(text):
        c = text[i]
        if in_q:
            if c == "\\" and i + 1 < len(text):
                i += 2
                continue
            if c == in_q:
                in_q = None
            i += 1
            continue
        if c in "'\"":
            in_q = c
            i += 1
            continue
        if c == "{":
            before = text[:i].rstrip()
            after = text[i + 1 :]
            if after.startswith(" "):
                after = after.lstrip()
            return before, after
        i += 1
    return text, None


def parse_one_alt(lines, i, piece, is_first_piece, new_mra):
    """1つの alt をパース。(rhs_tokens, final_action, i, _)"""
    rhs_tokens: list[str] = []
    final_action = None
    text = piece.strip()
    text = re.sub(r"\s+#.*$", "", text).strip()
    allow_line_continue = is_first_piece

    def is_boundary(nxt: str) -> bool:
        if re.match(r"^\s*[:|]", nxt):
            return True
        if is_production_name(nxt):
            return True
        if re.match(r"^([A-Za-z_][\w]*)\s*:", nxt) and not nxt.startswith((" ", "\t")):
            return True
        return False

    while True:
        if not text:
            if not allow_line_continue:
                break
            j = skip_blank_comments(lines, i + 1)
            if j >= len(lines):
                break
            nxt = lines[j]
            if is_boundary(nxt):
                break
            if re.match(r"^\s*\{", nxt):
                rest = re.sub(r"^\s*\{\s*", "", nxt)
                action, i = collect_action(lines, j, rest)
                k = skip_blank_comments(lines, i + 1)
                more_on_next = k < len(lines) and not is_boundary(lines[k]) and not re.match(
                    r"^\s*\{", lines[k]
                )
                if more_on_next:
                    mra = new_mra(action)
                    rhs_tokens.append(mra)
                    text = re.sub(r"\s+#.*$", "", lines[k].strip()).strip()
                    i = k
                    continue
                final_action = action
                break
            text = re.sub(r"\s+#.*$", "", nxt.strip()).strip()
            i = j
            continue

        before, after = find_action_brace(text)
        if after is not None:
            if before:
                rhs_tokens.extend(tokenize_rhs(before))
            action, i2 = collect_action(lines, i, after)
            i = i2
            if not allow_line_continue:
                final_action = action
                break
            k = skip_blank_comments(lines, i + 1)
            more_on_next = k < len(lines) and not is_boundary(lines[k]) and not re.match(
                r"^\s*\{", lines[k]
            )
            if more_on_next:
                mra = new_mra(action)
                rhs_tokens.append(mra)
                text = re.sub(r"\s+#.*$", "", lines[k].strip()).strip()
                i = k
                continue
            final_action = action
            break
        else:
            rhs_tokens.extend(tokenize_rhs(text))
            text = ""
            continue

    return rhs_tokens, final_action, i, False


def tokenize_rhs(rhs_str: str) -> list[str]:
    """RHS をトークン列に分割。'('name のようにクォート直後に識別子が続く場合も分離する。"""
    tokens: list[str] = []
    i = 0
    n = len(rhs_str)
    while i < n:
        if rhs_str[i].isspace():
            i += 1
            continue
        if rhs_str[i] in "'\"":
            q = rhs_str[i]
            j = i + 1
            while j < n and rhs_str[j] != q:
                if rhs_str[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            if j < n:
                j += 1
            tokens.append(rhs_str[i:j])
            i = j
            continue
        if rhs_str[i] == ":" and i + 1 < n and rhs_str[i + 1].isalpha():
            j = i + 1
            while j < n and (rhs_str[j].isalnum() or rhs_str[j] == "_"):
                j += 1
            tokens.append(rhs_str[i:j])
            i = j
            continue
        j = i
        while j < n and not rhs_str[j].isspace() and rhs_str[j] not in "'\"":
            j += 1
        tokens.append(rhs_str[i:j])
        i = j
    return tokens


def convert_ruby_control(a: str) -> str:
    """簡易: unless/if ... then ... else ... end → Python。完全ではない。"""
    # unless X then → if not (X):
    a = re.sub(
        r"\bunless\s+(.*?)\s+then\b",
        lambda m: f"if not ({m.group(1).strip()}):",
        a,
        flags=re.S,
    )
    # if X then → if X:   (then が残る複合条件にも対応)
    a = re.sub(
        r"\bif\s+(.*?)\s+then\b",
        lambda m: f"if {m.group(1).strip()}:",
        a,
        flags=re.S,
    )
    # 行末の then（複合条件で then だけ残るケース）— 空白なしでも
    a = re.sub(r"[ \t]*\bthen\b", ":", a)
    # elsif → elif
    a = re.sub(r"\belsif\b", "elif", a)
    # else (alone on line-ish)
    a = re.sub(r"\belse\b(?!\s*:)", "else:", a)
    # end → インデント終端マーカー（後で削除）
    a = re.sub(r"^\s*end\s*$", "__TECS_END__", a, flags=re.M)
    a = re.sub(r"\bend\b", "", a)
    return a


def ruby_action_to_py(action: str | None, rhs_len: int, class_prefix: str = "Generator") -> str:
    if action is None or not action.strip():
        return ""

    a = action.strip()
    # strip trailing comments that are only `#1ok` style after }
    a = re.sub(r"[ \t]+#.*$", "", a, flags=re.M)

    a = convert_ruby_control(a)

    a = re.sub(r"val\[(\d+)\]", lambda m: f"p[{int(m.group(1)) + 1}]", a)

    uses_result = re.search(r"\bresult\b", a)
    if uses_result and not re.search(r"\bresult\s*=", a):
        if rhs_len >= 1:
            a = "p[0] = p[1]\n" + a

    a = re.sub(r"\bresult\s*<<", "p[0].append", a)
    a = re.sub(r"\bresult\s*=", "p[0] =", a)
    a = re.sub(r"\bresult\b", "p[0]", a)

    a = re.sub(r"\.append\s+(p\[\d+\])", r".append(\1)", a)

    def wrap_append_arg(m):
        # .append <expr> で括弧がないもの。行末またはコメントまで
        return f".append({m.group(1).strip()})"

    a = re.sub(r"\.append\s+(\[[\s\S]*?\])(?=\s*(?:#|$))", wrap_append_arg, a)
    a = re.sub(r"\.append\s+([^\n#]+?)(?=\s*(?:#|$))", wrap_append_arg, a)
    # result = a << b  → a.append(b); result = a
    a = re.sub(
        r"p\[0\] = (p\[\d+\])\.append\((\S+)\)",
        r"\1.append(\2)\n    p[0] = \1",
        a,
    )
    a = re.sub(
        r"p\[0\] = (\S+)\s*<<\s*(\S+)",
        r"\1.append(\2)\n    p[0] = \1",
        a,
    )
    a = re.sub(r"(\S+)\s*<<\s*(\S+)", r"\1.append(\2)", a)

    # result 未代入で val[0] を破壊的に更新するだけ → racc default result = val[0]
    if not re.search(r"\bp\[0\]\s*=", a) and re.search(
        r"\bp\[1\]\.(add_|append|change_|set_)", a
    ):
        a = a.rstrip() + "\n    p[0] = p[1]"

    # :FOO → "FOO" (racc Symbol)
    a = re.sub(r":([A-Za-z_][A-Za-z0-9_]*)", r'"\1"', a)

    a = re.sub(r"\bnil\b", "None", a)
    a = re.sub(r"\btrue\b", "True", a)
    a = re.sub(r"\bfalse\b", "False", a)
    # :"foo#{expr}bar" / "foo#{expr}bar" → f-string 相当
    def interp(m):
        s = m.group(0)
        # strip leading : for symbol
        if s.startswith(":"):
            s = s[1:]
        inner = s[1:-1]  # without quotes
        # #{expr} → {expr}
        inner = re.sub(r"#\{([^}]*)\}", r"{\1}", inner)
        return 'f"' + inner.replace('"', '\\"') + '"'

    a = re.sub(r':?"[^"\n]*#\{[^}]+\}[^"\n]*"', interp, a)
    # Class.new( → Class(  だが Class.new_foo( はそのまま
    a = re.sub(r"\.new\(", "(", a)
    # Class.new → Class() （引数なし）
    a = re.sub(r"\b([A-Z][A-Za-z0-9_]*)\.new\b(?!\s*[\(=])", r"\1()", a)
    a = re.sub(r"@@([A-Za-z_][\w]*)", rf"{class_prefix}.\1", a)
    a = re.sub(r"\.append!", ".append_bang", a)
    a = re.sub(r"\.merge\s+(p\[\d+\])", r".merge(\1)", a)
    if class_prefix == "C_parser":
        a = re.sub(
            r"\bset_no_type_name\s+(True|False|true|false)\b",
            rf"{class_prefix}.current().set_no_type_name(\1)",
            a,
        )
        a = re.sub(r"\bnext_token\b(?!\s*\()", rf"{class_prefix}.current().next_token()", a)
        a = re.sub(r"\bwhile\s+true\b", "while True", a, flags=re.I)

    # .gsub( /re/, "repl" ) → re.sub — val[] 置換の後に適用。受信側は識別子/添字/属性のみ
    def gsub_to_re(m):
        recv, pat, repl = m.group(1), m.group(2), m.group(3)
        return f"re.sub(r'{pat}', {repl}, {recv})"

    a = re.sub(
        r"([\w.\[\]]+)\.gsub!\(\s*/((?:\\.|[^/])*)/\s*,\s*(\"(?:\\.|[^\"])*\")\s*\)",
        gsub_to_re,
        a,
    )
    a = re.sub(
        r"([\w.\[\]]+)\.gsub\(\s*/((?:\\.|[^/])*)/\s*,\s*(\"(?:\\.|[^\"])*\")\s*\)",
        gsub_to_re,
        a,
    )
    a = re.sub(
        r"([\w.\[\]]+)\.sub!\(\s*/((?:\\.|[^/])*)/\s*,\s*(\"(?:\\.|[^\"])*\")\s*\)",
        gsub_to_re,
        a,
    )
    a = re.sub(
        r"([\w.\[\]]+)\.sub\(\s*/((?:\\.|[^/])*)/\s*,\s*(\"(?:\\.|[^\"])*\")\s*\)",
        gsub_to_re,
        a,
    )

    # .each { |x| ... }  — 複数行ブロック対応
    def each_repl(m):
        expr, var, body = m.group(1), m.group(2), m.group(3)
        body_lines = [ln.strip() for ln in body.strip().splitlines() if ln.strip() and not ln.strip().startswith("#")]
        # 先頭コメント行は残す
        comments = [ln.strip() for ln in body.splitlines() if ln.strip().startswith("#")]
        out = [f"for {var} in {expr}:"]
        for c in comments:
            out.append(f"    {c}")
        for bl in body_lines:
            if bl.startswith("#"):
                continue
            out.append(f"    {bl}")
        return "\n".join(out)

    a = re.sub(
        r"(\S+)\.each\s*\{\s*\|(\w+)\|\s*((?:[^{}]|\{[^{}]*\})*)\}",
        each_repl,
        a,
        flags=re.S,
    )
    # 取り残した単独 }
    a = re.sub(r"^\s*\}\s*$", "", a, flags=re.M)

    a = a.replace("&&", " and ")
    a = a.replace("||", " or ")
    a = re.sub(r"(?<![\w=])!\s*(?=[\w(])", "not ", a)
    # Ruby ハッシュ { a => b } → { a: b } は不可なので dict 形式へ
    a = re.sub(
        r"\{\s*([^|{}]+?)\s*=>\s*([^|{}]+?)\s*\}",
        r"{(\1): (\2)}",
        a,
    )

    _recv = r"((?:\w+|p\[\d+\])(?:\.\w+|\[\d+\])*)"
    a = re.sub(
        _recv + r"\.instance_of\?\(\s*(\w+)\s*\)",
        r"(type(\1) is \2)",
        a,
    )
    a = re.sub(
        _recv + r"\.kind_of\?\(\s*(\w+)\s*\)",
        r"isinstance(\1, \2)",
        a,
    )
    a = re.sub(
        _recv + r"\.kind_of\?\s+(\w+)",
        r"isinstance(\1, \2)",
        a,
    )
    a = re.sub(r"\.(\w+)\?", r".\1", a)
    a = re.sub(r"\.(\w+)!", r".\1", a)  # append! 等。Python 側は非破壊/同名を用意
    # 属性参照ではなく呼び出しが必要な 0 引数メソッド（式中）
    for meth in ("get_elements", "to_sym", "to_i", "to_f", "to_s"):
        a = re.sub(rf"\.{meth}\b(?!\s*\()", rf".{meth}()", a)
    # ? 除去後に残る .kind_of( / .kind_of X / .instance_of(
    a = re.sub(
        _recv + r"\.kind_of\(\s*(\w+)\s*\)",
        r"isinstance(\1, \2)",
        a,
    )
    a = re.sub(
        _recv + r"\.kind_of\s+(\w+)",
        r"isinstance(\1, \2)",
        a,
    )
    a = re.sub(
        _recv + r"\.instance_of\(\s*(\w+)\s*\)",
        r"(type(\1) is \2)",
        a,
    )

    # bare instance methods used in grammar actions
    for meth in ("set_in_specifier", "unset_in_specifier"):
        a = re.sub(rf"\b{meth}\b(?!\s*\()", rf"Generator.current().{meth}()", a)

    # 0 引数クラスメソッド呼び出し: Foo.bar → Foo.bar()
    a = re.sub(
        r"\b([A-Z][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)\b(?!\s*[\(=])(?=\s*$)",
        r"\1()",
        a,
        flags=re.M,
    )
    # Foo.bar True/False/None/p[n] → Foo.bar(...)
    a = re.sub(
        r"\b([A-Z][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)\s+(True|False|None|p\[\d+\])\b",
        r"\1(\2)",
        a,
    )
    # 代入のない行のみ: obj.method arg / obj.method
    def fix_bare_calls(line: str) -> str:
        if not line.strip() or "=" in line:
            return line
        line = re.sub(
            r"(\b[A-Za-z_][\w]*(?:\[[^\]]+\])?(?:\.[A-Za-z_][\w]*)+)\s+(p\[\d+\](?:\.\w+)*|True|False|None|\"[^\"]*\"|\d+)\s*$",
            r"\1(\2)",
            line,
        )
        line = re.sub(
            r"(\b[A-Za-z_][\w]*(?:\[[^\]]+\])?(?:\.[A-Za-z_][\w]+)+)\s*$",
            r"\1()",
            line,
        )
        return line

    a = "\n".join(fix_bare_calls(ln) for ln in a.split("\n"))

    # if/elif/for/else のインデント
    # 先行空白を落としてからブロックインデント
    a = "\n".join(ln.lstrip() if ln.strip() else "" for ln in a.split("\n"))
    a = indent_blocks(a)

    out_lines = []
    for ln in a.split("\n"):
        if not ln.strip():
            out_lines.append("")
        else:
            out_lines.append("    " + ln)
    return "\n".join(out_lines)


def indent_blocks(a: str) -> str:
    """if/elif/for/else: と __TECS_END__ でインデントを付与。空ブロックには pass。"""
    lines = a.split("\n")
    out = []
    indent = 0
    for ln in lines:
        st = ln.strip()
        if not st:
            out.append("")
            continue
        if st == "__TECS_END__":
            # 直前がヘッダだけなら pass
            if out and out[-1].rstrip().endswith(":"):
                out.append("    " * indent + "pass")
            indent = max(0, indent - 1)
            continue
        if re.match(r"^(else:|elif\b)", st):
            indent = max(0, indent - 1)
            # else の前が空 if なら pass（空行を飛ばして判定）
            k = len(out) - 1
            while k >= 0 and not out[k].strip():
                k -= 1
            if k >= 0 and out[k].rstrip().endswith(":"):
                out.append("    " * (indent + 1) + "pass")
            out.append("    " * indent + st)
            if st.endswith(":"):
                indent += 1
            continue
        out.append("    " * indent + st)
        if re.match(r"^(if\b|for\b)", st) and st.endswith(":"):
            indent += 1
    if out and out[-1].rstrip().endswith(":"):
        out.append("    " * indent + "pass")
    return "\n".join(out)


def rhs_to_ply(tokens: list[str]) -> str:
    if not tokens:
        return "empty"
    out = []
    for t in tokens:
        if re.match(r"^:[A-Z][A-Z0-9_]*$", t):
            # racc :IDENTIFIER means terminal IDENTIFIER
            out.append(t[1:])
        elif re.match(r"^[A-Z][A-Z0-9_]*$", t):
            out.append(t)
        elif re.match(r"^[A-Za-z_][\w]*$", t):
            # C_parser など CamelCase / snake_case の非終端（C_parser, namespace_identifier）
            out.append(t)
        elif re.match(r"^[a-z_][\w]*$", t):
            out.append(t)
        elif (t.startswith("'") and t.endswith("'")) or (t.startswith('"') and t.endswith('"')):
            out.append('"' + t[1:-1].replace('"', '\\"') + '"')
        else:
            out.append(f'"{t}"')
    return " ".join(out)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: racc_to_ply.py bnf.y.rb [--class-prefix=C_parser]")
    class_prefix = "Generator"
    src_path = sys.argv[1]
    for arg in sys.argv[2:]:
        if arg.startswith("--class-prefix="):
            class_prefix = arg.split("=", 1)[1]
    src = open(src_path, encoding="utf-8").read()
    productions, mra_defs = parse_productions(extract_rule(src))
    n_alts = sum(len(a) for _, a in productions)
    print(
        f"productions: {len(productions)}, alts: {n_alts}, mra: {len(mra_defs)}",
        file=sys.stderr,
    )

    print("# -*- coding: utf-8 -*-")
    print("# AUTO-GENERATED by tools/racc_to_ply.py — review FIXME")
    print(f"# from {src_path} rule section")
    print()
    print("import re")
    print()
    print("def p_empty(p):")
    print("    'empty :'")
    print("    pass")
    print()

    for mra_name, action in mra_defs:
        print(f"def p_{mra_name}(p):")
        print(f"    '''{mra_name} :'''")
        py = ruby_action_to_py(action, 0, class_prefix)
        if py.strip():
            print(py)
        else:
            print("    pass")
        print()

    prod_index: dict[str, int] = defaultdict(int)
    for name, alts in productions:
        for rhs, action in alts:
            prod_index[name] += 1
            idx = prod_index[name]
            fname = f"p_{name}" if len(alts) == 1 else f"p_{name}_{idx}"
            rhs_ply = rhs_to_ply(rhs)
            print(f"def {fname}(p):")
            print(f"    '''{name} : {rhs_ply}'''")
            if action is None or not action.strip():
                if len(rhs) == 1:
                    print("    p[0] = p[1]")
                elif not rhs:
                    print("    p[0] = None")
                else:
                    print("    p[0] = p[1]  # default racc result")
            else:
                py = ruby_action_to_py(action, len(rhs), class_prefix)
                print(py)
            print()

    print("def p_error(p):")
    print("    pass")


if __name__ == "__main__":
    main()
