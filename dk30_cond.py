from log import *
from convert_money import *
from kpt import *
from htk_dt_ln import *
def dk30(row):
    text1 = str(row.get('PTK1', ''))
    text2 = str(row.get('PTK2', ''))
 
 
#     text1 = str(row['PTK1']) 
#     text2 = str(row['PTK2'])
    if 0 < len(text1.split()) < 50:
        text1=''
    if 0 < len(text2.split()) < 50:
        text2 = ''
    text = text1 + '\n' +text2
    text = replace_text(text)
    AI = chain.invoke({'text': text})
 
    try:
 
        data = json.loads(AI)
        converted_data = convert_money(data)
    except Exception as e:
        return None
    htk_value = safe_extract_float(converted_data.get("hàng tồn kho", "0"))
 
 
    try:
        data_dtln = json.loads(AI)
        converted_data_dtln = convert_money_dtln(data_dtln)
 
    except Exception as e:
        return None
    dt_value = converted_data_dtln.get("doanh thu", "0")
    try:
        dt_value = float(str(dt_value).replace('tỷ đồng/năm', '').strip())
    except Exception as e:
        dt_value = 0.0
    ln_value = converted_data_dtln.get("lợi nhuận", "0")
    try:
        ln_value = float(str(ln_value).replace('tỷ đồng/năm', '').strip())
    except Exception as e:
        ln_value = 0.0 

    kpt_value = str(row.get('KHOẢN PHẢI THU', ''))
    try:
        kpt_value = float(str(kpt_value).replace('tỷ đồng', '').strip())
    except:
        kpt_value = 0
    row['HÀNG TỒN KHO'] = "Không có thông tin" if htk_value == 0.0 else f"{htk_value} tỷ đồng"
    row['DOANH THU'] = "Không có thông tin" if dt_value == 0.0 else f"{dt_value:.3f} tỷ đồng/năm"
    row['LỢI NHUẬN'] = "Không có thông tin" if ln_value == 0.0 else f"{ln_value:.3f} tỷ đồng/năm"
 
    try:
        gthm = float(row.get('Giá trị hạn mức/Số tiền cho vay đề xuất*', 0)) / 1e9  # Chuyển đổi sang tỷ đồng
    except Exception as e:
        gthm=0
        logger.error('Giá trị hạn mức',e)
#     if (float(kpt_value) + htk_value) > 0:
    if isinstance(kpt_value, (int, float)) and isinstance(htk_value, (int, float)) and (kpt_value + htk_value) > 0:
        if gthm > 20 and gthm > (kpt_value + htk_value):
            row['dk30'] = False
            return '''- Chưa thỏa mãn điều kiện 30: \n --> Giải pháp là: Giá trị hạn mức > 20 tỷ đồng và vượt quá quy mô Hàng tồn kho + Khoản phải thu: 
            Yêu cầu ĐVKD làm rõ nguyên nhân giá trị đề xuất tài trợ lớn hơn tổng quy mô HTK và KPT'''
    row['dk30'] = None
 
    return None