import sys
sys.path.append('../')
import init

from utils.export_data import ExportData
import time

def main():
    # 导出数据
    key_map = {
        'aim_key1' : 'str_source_key2',          # 目标键 = 源键对应的值         类型为str
        'aim_key2' : 'int_source_key3',          # 目标键 = 源键对应的值         类型为int
        'aim_key3' : 'date_source_key4',         # 目标键 = 源键对应的值         类型为date
        'aim_key4' : 'vint_id',                  # 目标键 = 值                   类型为int
        'aim_key5' : 'vstr_name',                # 目标键 = 值                   类型为str
        'aim_key6' : 'sint_select id from xxx'   # 目标键 = 值为sql 查询出的结果 类型为int
        'aim_key7' : 'sstr_select name from xxx' # 目标键 = 值为sql 查询出的结果 类型为str
    }

    export_data = ExportData()
    export_data.export_to_oracle(source_table = '', aim_table = '', key_map = key_map, unique_key = 'url')

if __name__ == '__main__':
    main()
