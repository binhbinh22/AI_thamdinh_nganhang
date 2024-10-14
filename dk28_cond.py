# =========================== DK28 ===========================================
import re
from kpt import *
import json
from convert_money import *
from log import *
import config
def dk28(row):
    try:
        text1 = str(row.get('PTK1', ''))

        text2 = str(row.get('PTK2', ''))
 
        text1 = str(row['PTK1']) 

        text2 = str(row['PTK2'])

#         if 0 < len(text1.split()) < 50:

#             text1=''

#         if 0 < len(text2.split()) < 50:

#             text2 = ''

        text = text1 + '\n' +text2

        text = check_kpt(text)

        if text:
            business_instance = chain_kpt.invoke({"input": text})
            res = json.loads(business_instance)
            converted_data = convert_money(res)
            kpt_value_str = converted_data.get("khoản phải thu", "0")  
            if kpt_value_str == '':
                kpt_value_str = 0
                row['KHOẢN PHẢI THU'] = 'Không có thông tin'
            else:
                kpt_value_str = kpt_value_str.replace(' tỷ đồng', '').strip()
                if kpt_value_str != '0':
                    row['KHOẢN PHẢI THU'] = f"{kpt_value_str} tỷ đồng"
                else:
                    row['KHOẢN PHẢI THU'] = 'Không có thông tin'
            kpt_value = float(kpt_value_str)
        else:

            print('no text')

            row['KHOẢN PHẢI THU'] = 'Không có thông tin'

    except Exception as e:

        row['KHOẢN PHẢI THU'] = 'Không có thông tin'

        kpt_value= 0

        logger.error(f"Error in processing AI chain or converting money in dk28: {e}")

        row['dk28'] = None
    try:
        # Điều kiện 1: Giá trị hạn mức/Số tiền cho vay đề xuất >= 20 tỷ đồng
        gthm = float(row.get('Giá trị hạn mức/Số tiền cho vay đề xuất*', 0)) / 1e9

        if re.search(r'buôn chuyến', text, re.IGNORECASE) and (kpt_value <= 20) and (gthm >= 20) :
            row['dk28'] = False
            return '''- Chưa thỏa mãn điều kiện 28:\n 
            -> Giải pháp là: Yêu cầu ĐVKD làm rõ nguyên nhân giá trị đề xuất tài 
            trợ lớn hơn quy mô KPT của Khách hàng (do hoạt động lĩnh vực buôn chuyến: 
            Thời gian hàng đi đường ngắn, không tính hàng tồn kho để cấp HM)\n\n'''
        row['dk28'] = None   
        return None
    except Exception as e:
        row['KHOẢN PHẢI THU'] = 'Không có thông tin'
        logger.error(f"Error in processing dk28: {e}")
        row['dk28'] = None
        return None
 