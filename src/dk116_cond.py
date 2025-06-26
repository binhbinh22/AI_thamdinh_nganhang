# =========================== DK28 ===========================================
import re
from kpt import *
import json
import os
import sys

sys.path.append(os.getcwd())
from src.convert_money import *
from src.log import api_logger as logger
import config
def DK116(row):
    try:
        # Điều kiện 2: Kiểm tra PTK1 và PTK2 có chứa cụm 'buôn chuyến'
        text1 = str(row.get('PTK1', ''))
        text2 = str(row.get('PTK2', ''))

        text1 = str(row['PTK1']) 
        text2 = str(row['PTK2'])
        
#         if 0 < len(text1.split()) < 50:
#             text1=''
#         if 0 < len(text2.split()) < 50:
#             text2 = ''
            
        text = text1 + '\n' +text2
        text_ptk = re.sub(r'\s+', ' ', text).strip() # loại bỏ khoảng trắng thừa
        text = check_kpt(text_ptk)
        text = text.replace("khoảng"," ")

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
            print(kpt_value)
                
                
        else:
            print('no text')
            row['KHOẢN PHẢI THU'] = 'Không có thông tin'
            
    except Exception as e:
        row['KHOẢN PHẢI THU'] = 'Không có thông tin'
        kpt_value= 0
        logger.error(f"Error in processing AI chain or converting money in DK116: {e}")
        row['DK116'] = None
        
    gc.collect()
    try:
        # Điều kiện 1: Giá trị hạn mức/Số tiền cho vay đề xuất >= 20 tỷ đồng
        gthm = float(row.get('Giá trị hạn mức/Số tiền cho vay đề xuất*', 0)) / 1e9
        if re.search(r'buôn chuyến', text_ptk, re.IGNORECASE) and (kpt_value <= 20) and (gthm >= 20) :
            row['DK116'] = False
            return '''- Yêu cầu ĐVKD làm rõ nguyên nhân giá trị đề xuất tài 
            trợ lớn hơn quy mô KPT của Khách hàng (do hoạt động lĩnh vực buôn chuyến: 
            Thời gian hàng đi đường ngắn, không tính hàng tồn kho để cấp HM)\n\n'''
        row['DK116'] ='Pass'  
        return None
    except Exception as e:
        row['KHOẢN PHẢI THU'] = 'Không có thông tin'
        logger.error(f"Error in processing DK116: {e}")
        row['DK116'] = None
        return None
    

#     return row['KHOẢN PHẢI THU']