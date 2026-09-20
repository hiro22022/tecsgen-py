#!/usr/bin/env ruby
# -*- coding: utf-8 -*-
#
#  TECS Generator (Python port)
#
#= racc (bnf.y.rb) の rule 節を PLY の p_ 関数群へ変換する
#
# 使い方:
#   ruby tools/racc_to_ply.rb ../tecsgen/tecsgen/tecslib/core/bnf.y.rb \
#        > tecsgen/tecslib/core/_bnf_rules.py
#
# 変換規約:
#   val[n]     → p[n+1]
#   result = x → p[0] = x
#   result << x → (p[0] は既定で p[1])  p[0] = list(p[1]); p[0].append(x) 等は手動調整が必要な場合あり
#                 ここでは result の初期値を p[1] とし、result << を .append に変換
#   :SYM       → "SYM"
#   true/false/nil → True/False/None
#   .new(      → (
#   @@x        → Generator._x  (クラス属性。後で手で合わせる)
#

src_path = ARGV[0] or abort("usage: racc_to_ply.rb bnf.y.rb")
src = File.read(src_path)
rule = src[/^rule\n(.*)^end$/m, 1] or abort("no rule section")

#--- tokenize the rule section into productions ---
# Each production: NAME\n  : alt\n  | alt\n

lines = rule.lines.map(&:rstrip)
i = 0
productions = []  # [name, [[rhs_tokens, action_ruby], ...]]

while i < lines.size
  line = lines[i]
  if line =~ /^([A-Za-z_][\w]*)\s*$/
    name = $1
    i += 1
    alts = []
    while i < lines.size
      l = lines[i]
      break if l =~ /^[A-Za-z_][\w]*\s*$/ && l !~ /^\s/
      break if l =~ /^\#\#\#\#/  # section comment at column 0 rare

      if l =~ /^\s*([|:])\s*(.*)$/
        rhs_str = $2.strip
        # action may follow on same line { ... } or next lines
        action = nil
        if rhs_str =~ /^(.*?)\s*\{\s*(.*)$/
          rhs_part = $1.strip
          rest = $2
          # collect until matching }
          depth = 1
          buf = rest + "\n"
          if rest.count('{') - rest.count('}') >= 0 && rest.include?('}') && (rest.count('{') < rest.count('}'))
            # closed on same line - already in rest
          end
          # recount
          depth = 1 + rest.count('{') - rest.count('}')
          if depth <= 0
            # extract action body before final }
            action = rest.sub(/\}\s*$/, '')
            rhs_str = rhs_part
          else
            i += 1
            while i < lines.size && depth > 0
              buf << lines[i] << "\n"
              depth += lines[i].count('{') - lines[i].count('}')
              i += 1
            end
            i -= 1
            action = buf.sub(/\}\s*\z/m, '')
            rhs_str = rhs_part
          end
        end
        rhs_tokens = rhs_str.empty? ? [] : rhs_str.split(/\s+/)
        alts << [rhs_tokens, action]
      elsif l =~ /^\s*\{/ || (l =~ /^\s/ && !alts.empty? && alts[-1][1].nil? == false)
        # continuation of previous action already handled
      elsif l =~ /^\s*#/ || l.empty?
        # comment / blank
      end
      i += 1
      # stop if next production name at column 0
      if i < lines.size && lines[i] =~ /^[A-Za-z_][\w]*\s*$/
        break
      end
    end
    productions << [name, alts] unless alts.empty?
  else
    i += 1
  end
end

STDERR.puts "productions: #{productions.size}, alts: #{productions.map{|n,a| a.size}.inject(:+)}"

def ruby_action_to_py(action, rhs_len)
  return "p[0] = p[1] if len(p) > 1 else None" if action.nil? || action.strip.empty?

  a = action.dup
  # strip leading/trailing whitespace
  a.strip!

  # comments # ... keep
  # val[n] → p[n+1]
  a.gsub!(/val\[(\d+)\]/) { "p[#{$1.to_i + 1}]" }

  # result defaults to val[0] in racc (= p[1])
  # Replace result = with p[0] =
  # Replace result << with append on p[0]
  # First, if action uses result without assignment first, prepend p[0] = p[1]
  uses_result = a =~ /\bresult\b/
  if uses_result
    unless a =~ /\bresult\s*=/
      # might only use result << 
      a = "p[0] = p[1]\n" + a if rhs_len >= 1
    end
  end
  a.gsub!(/\bresult\s*<</, 'p[0].append')  # result << x → p[0].append x  need parens later
  a.gsub!(/\bresult\s*=/, 'p[0] =')
  a.gsub!(/\bresult\b/, 'p[0]')

  # Fix .append x → .append(x) for simple cases: append val already became append p[N]
  a.gsub!(/\.append\s+(p\[\d+\])/, '.append(\1)')
  a.gsub!(/\.append\s+(\[[^\]]+\])/, '.append(\1)')

  # symbols :FOO → "FOO"  (but :"#{}" rare in actions)
  a.gsub!(/:([A-Za-z_][A-Za-z0-9_]*)/, '"\1"')

  a.gsub!(/\bnil\b/, 'None')
  a.gsub!(/\btrue\b/, 'True')
  a.gsub!(/\bfalse\b/, 'False')
  a.gsub!(/\.new\(/, '(')
  a.gsub!(/@@([A-Za-z_][\w]*)/, 'Generator.\1')

  # each { |i| ... }  — keep as comment for complex; simple one-liners
  # .each { |i|    →  for i in (...):
  # This is hard; leave Ruby-like and mark FIXME for blocks with {
  if a =~ /\.each\s*\{/ || a =~ /\{\s*\|/
    # convert simple .each { |x| stmt } 
    a.gsub!(/(\S+)\.each\s*\{\s*\|(\w+)\|\s*/) { "for #{$2} in #{$1}:\n                " }
    a.gsub!(/\}\s*\z/, '')
  end

  # && || 
  a.gsub!('&&', ' and ')
  a.gsub!('||', ' or ')
  a.gsub!(/(?<![\w=])!\s*(?=[\w(])/, 'not ')

  # instance_of? / kind_of?
  a.gsub!(/(\w+(?:\.\w+)*)\.instance_of\?\(\s*(\w+)\s*\)/, '(type(\1) is \2)')
  a.gsub!(/(\w+(?:\.\w+)*)\.kind_of\?\(\s*(\w+)\s*\)/, 'isinstance(\1, \2)')
  a.gsub!(/\.(\w+)\?/, '.\1')

  # put parentheses on method calls without them - skip

  # Indent each line of action
  lines = a.split("\n").map(&:rstrip)
  lines.map { |l| l.empty? ? "" : "        " + l }.join("\n")
end

def rhs_to_ply(tokens)
  return "empty" if tokens.empty?  # PLY needs a name for epsilon - use empty and define empty rule
  tokens.map { |t|
    if t =~ /^[A-Z][A-Z0-9_]*$/
      t  # token name
    elsif t =~ /^[a-z_][\w]*$/
      t  # nonterminal
    elsif t =~ /^'.'$/ || t =~ /^'.*'$/ || t =~ /^".*"$/
      t.tr("'", '"')  # PLY prefers "
    else
      # operator like :: => etc written bare in racc? usually quoted
      "\"#{t}\""
    end
  }.join(" ")
end

puts "# -*- coding: utf-8 -*-"
puts "# AUTO-GENERATED by tools/racc_to_ply.rb — review and fix FIXME"
puts "# from bnf.y.rb rule section"
puts
puts "def p_empty(p):"
puts "    'empty :'"
puts "    pass"
puts

prod_index = Hash.new(0)
productions.each do |name, alts|
  alts.each do |rhs, action|
    prod_index[name] += 1
    idx = prod_index[name]
    fname = alts.size == 1 ? "p_#{name}" : "p_#{name}_#{idx}"
    rhs_ply = rhs_to_ply(rhs)
    rhs_ply = "empty" if rhs.empty?

    puts "def #{fname}(p):"
    puts "    '''#{name} : #{rhs_ply}'''"
    py = ruby_action_to_py(action, rhs.size)
    # default: if no action and single symbol, p[0]=p[1]
    if action.nil? || action.strip.empty?
      if rhs.size == 1
        puts "        p[0] = p[1]"
      elsif rhs.empty?
        puts "        p[0] = None"
      else
        puts "        p[0] = p[1]  # default racc result"
      end
    else
      puts py
    end
    puts
  end
end

puts "def p_error(p):"
puts "    # overridden by Generator.on_error via parser"
puts "    pass"
