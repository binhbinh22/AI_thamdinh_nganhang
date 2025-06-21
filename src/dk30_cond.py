import os
import sys

sys.path.append(os.getcwd())
from log import *
from src.convert_money import *
from kpt import *
from htk_dt_ln import *
def DK118(row):
    text1 = str(row.get('PTK1', ''))
    text2 = str(row.get('PTK2', ''))


#     text1 = str(row['PTK1']) 
#     text2 = str(row['PTK2'])

    text = text2 + '\n' +text1
    text = re.sub(r'\s+', ' ', text).strip() # loại bỏ khoảng trắng thừa
    
    #htk
    text_htk = check_DK30(text)
    AI_htk = chain.invoke({'text': text_htk})
    try:
        data_htk = json.loads(AI_htk)
        converted_data = convert_money(data_htk)
    except Exception as e:
        converted_data = {'hàng tồn kho': ''}
        
    htk_value = safe_extract_float(converted_data.get("hàng tồn kho", "0"))
    
    #dt
    text_dt= check_dt(text)
    AI_dt = revenue(text_dt)
    AI_dt_json = json.dumps(AI_dt)
    data_dt = json.loads(AI_dt_json)
    if AI_dt == {"doanh thu": ""}:
        AI_dt = chain_dt.invoke({'input': text_dt})
        data_dt = json.loads(AI_dt)
    try:
        dt = convert_dt(data_dt)
    except Exception as e:
        dt = {'doanh thu': ''}
        
    dt_value = dt.get("doanh thu", "0")
    try:
        dt_value = float(str(dt_value).replace('tỷ đồng/năm', '').strip())
    except Exception as e:
        dt_value = 0.0
        
    #ln
    text_ln = check_ln(text)
    AI_ln = profit(text_ln)
    AI_ln_json = json.dumps(AI_ln)
    data_ln = json.loads(AI_ln_json)
    if AI_ln == {"lợi nhuận": ""}:
        AI_ln = chain_ln.invoke({'input': text_ln})
        data_ln = json.loads(AI_ln)
    try:   
        ln = convert_dt(data_ln)
    except Exception as e:
        ln = {'lợi nhuận': ''}
    ln_value = ln.get("lợi nhuận", "0")
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
        gthm = 0 
        logger.error('Giá trị hạn mức',e)
    row['gthm'] = gthm
    row['kpt'] = kpt_value
    row['htk'] = htk_value
#     if (float(kpt_value) + htk_value) > 0:
    if kpt_value != 0 and htk_value != 0: 
        if gthm > 20 and gthm > (kpt_value + htk_value):
            row['DK118'] = False
            return '''- Giá trị hạn mức > 20 tỷ đồng và vượt quá quy mô Hàng tồn kho + Khoản phải thu: 
            Yêu cầu ĐVKD làm rõ nguyên nhân giá trị đề xuất tài trợ lớn hơn tổng quy mô HTK và KPT'''
    row['DK118'] = 'Pass'

    return None