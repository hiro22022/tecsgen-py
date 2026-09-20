# coding: utf-8
# ドメインプラグインの実例 MyClassPlugin
#
# 各メソッドの役割りは、ClassPlugin.rb を参照のこと
class MyClassPlugin < ClassPlugin

  # クラス定義(.cdf) の JSON スキーマ
  CLASS_DEF_schema = {
    :MyClass_class_def => {
      :class_def    => [ :class ]               # array
    },
    :class  => {
      :type         => "class",                 # fixed string (type name)
      :class_name   => :string,                 # "CLS_PRC1", "CLS_ALL_PRC1", "GLOBAL" (TECS でのクラス名)
      :processorID  => :integer,                # 1, 2, 3...
      :locality     => :string,                 # "only", "all", "global"
    },
    :__class  => {                              # optional
      :class_name_in_kernel => :string         # "CLS_PRC1", "CLS_ALL_PRC1", "GLOBAL" 
                                                # (HRMP3, FMP3 のクラス名; TECS と変えれるように設けている)
    }
  }

  # nTECSGENConfig::tClassConfig セルタイプのセル
  # { class_name_in_TECS => {:processorID=>processor_No, :class_name=>class_name_in_HRMP3, :locality=>locality_str}}
  @@class_info = nil
  
  def initialize( region, class_type_name, option )
    super
    if @@class_info == nil then
      validate_and_set_class_info
    end
    print "MyClassPlugin: initialize: region=#{region.get_name}, classTypeName=#{class_type_name}, option=#{option}\n"
  end

  def add_through_plugin( join, current_region, next_region, through_type )
    # join.get_owner:Cell  左辺のセル
    # join.get_definition:Port 呼び口
    # join.get_subscript:Integer or nil 呼び口配列の添数 (Join::@subscript の説明参照)
    # join.get_cell:Cell 右辺のセル
    # join.get_port_name:Symbol 受け口
    # get_rhs_subscript:Integer or nil 受け口配列の添数 (Join::@rhs_subscript の説明参照)
    # return []
    print "MyClassPlugin: add_through_plugin: #{current_region.get_name}=>#{next_region.get_name}, #{join.get_owner.get_name}.#{join.get_definition.get_name}=>#{join.get_cell.get_name}.#{join.get_port_name}, #{through_type}\n"
    return [ :TracePlugin, "" ]
  end

  def joinable?(current_region, next_region, through_type )
    print "MyClassPlugin: joinable? from #{current_region.get_name} to #{next_region.get_name} (#{through_type})\n"
    return true
  end

  def self.gen_post_code file
  end

  def get_kind
    :kernel
  end

  #=== validate
  # validate JSON format data in __tool_info__( "MyClass_class_def" )
  def validate_and_set_class_info
    validator = TOOL_INFO::VALIDATOR.new( :MyClass_class_def, CLASS_DEF_schema )
    if validator.validate then
      @@class_info = {}
      info = TOOL_INFO.get_tool_info( :MyClass_class_def )
      if info == nil then
        cdl_error( "MyClass9999 not found __tool_info__( MyClass_class_def )" )
      end
      class_info = info[ :class_def ]
      class_info.each{ |cls|
        attr = {}
        @@class_info[ cls[ :class_name ].to_sym ] = attr     # TECS でのクラス名
        attr[ :processorID ] = cls[ :processorID ]
        attr[ :locality ]    = cls[ :locality ]
        attr[ :class_name ]  = cls[ :class_name ]     # kernel でのクラス名
        if cls[ :class_name_in_kernel ] then
          attr[ :class_name ] = cls[ :class_name_in_kernel ]
        end
      }
    end
  end

  def check_class class_name
    print "MyClassPlugin#check_class #{class_name}\n"
    if @@class_info[ class_name.to_sym ] then
      return true
    else
      return false
    end
  end
end
