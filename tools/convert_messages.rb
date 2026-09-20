#
#  TECS Generator (Python port)
#      Generator for TOPPERS Embedded Component System
#
#   Copyright (C) 2008-2021 by TOPPERS Project TECS WG
#
#   ライセンスは tecsgen.py の冒頭を参照のこと．
#
#= Ruby 版のメッセージ定義を Python モジュールへ変換する
#
# tecslib/messages/*.rb は文字列のテーブルだけを持つデータファイルなので，
# Ruby で読み込んでから Python のソースとして書き出す．
# Ruby 版を更新したときはこのスクリプトを再実行する．
#
#   ruby tools/convert_messages.rb ../tecsgen/tecsgen/tecslib/messages tecsgen/tecslib/messages
#

require 'json'

src_dir = ARGV[0]
dst_dir = ARGV[1]

TABLES = {
  :@@error_message   => "error_message",
  :@@warning_message => "warning_message",
  :@@info_message    => "info_message",
  :@@comment         => "comment",
}

#=== Python の文字列リテラルへ変換する
def py_str(s)
  JSON.generate([s])[1..-2]
end

Dir.glob("#{src_dir}/messages_*.rb").sort.each { |path|
  base = File.basename(path, ".rb")

  # ファイルごとに独立したテーブルを得るため，毎回 class を作り直す
  klass = Class.new
  Object.send(:remove_const, :TECSMsg) if Object.const_defined?(:TECSMsg)
  Object.const_set(:TECSMsg, klass)
  load path

  lines = []
  lines << "# -*- coding: utf-8 -*-"
  lines << "#"
  lines << "#  TECS Generator (Python port)"
  lines << "#      Generator for TOPPERS Embedded Component System"
  lines << "#"
  lines << "#   Copyright (C) 2008-2021 by TOPPERS Project TECS WG"
  lines << "#"
  lines << "#   このファイルは tecslib/messages/#{base}.rb から"
  lines << "#   tools/convert_messages.rb により生成された．直接編集しないこと．"
  lines << "#   ライセンスは tecsgen.py の冒頭を参照のこと．"
  lines << ""
  lines << "from tecslib.core.messages import TECSMsg"
  lines << ""

  TABLES.each { |var, name|
    next unless klass.class_variable_defined?(var)
    table = klass.class_variable_get(var)
    next if table.empty?
    lines << ""
    lines << "TECSMsg.#{name}.update({"
    table.each { |k, v|
      lines << "    #{py_str(k.to_s)}: #{py_str(v)},"
    }
    lines << "})"
  }
  lines << ""

  dst = "#{dst_dir}/#{base}.py"
  File.write(dst, lines.join("\n"))
  STDERR.puts "generated #{dst}"
}
