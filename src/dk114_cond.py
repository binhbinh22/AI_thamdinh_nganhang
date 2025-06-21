import os
import json
import gc
import logging
import ast
import re
import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import unicodedata
import config
## ==============SCHEMA===================================
# Schema for structured response
response_schemas_20 = [
    ResponseSchema(
        name="mặt hàng kinh doanh",
        description="Mặt hàng kinh doanh là sản phẩm, mặt hàng mà khách hàng kinh doanh, nếu không có thông tin hãy trả về ''.",
    ),
    ResponseSchema(
        name="địa điểm",
        description="Địa điểm kinh doanh, địa chỉ doanh nghiệp của khách hàng, nếu không có thông tin hãy trả về ''."),
    ResponseSchema(
        name="thời gian kinh doanh",
        description="thời gian, kinh nghiệm, thâm niên hoạt động sản xuất kinh doanh của khách hàng",
        # description="kinh nghiệm, thâm niên, thời gian kinh doanh quản lý, buôn bán",
    ),
    ResponseSchema(
        name="phương thức thanh toán",
        description="có thông tin phương thức thanh toán tiền mặt,trích công nợ, chính sách công nợ...",
    ),

    ResponseSchema(
        name="phương thức mua bán",
        description="có thông tin các loại hình buôn bán: Bán lẻ, bán buôn, bán sỉ, buôn chuyến...",
    ),
    ResponseSchema(
        name="kho hàng",
        description="có thông tin địa chỉ hoặc diện tích kho hàng hoặc cách thức lưu sản phẩm, mặt hàng của khách hàng",
    ),
    ResponseSchema(
        name="đầu vào",
        description="Nguồn cung ứng hàng hóa, nguyên vật liệu, thông tin nhà cung cấp, địa điểm nhập hàng hoặc cách thức nhập hàng. Nếu không có thông tin, hãy trả về ''.",
    ),   
    ResponseSchema(
        name="đầu ra",
        description="Thông tin về nơi tiêu thụ sản phẩm, khách hàng mục tiêu, thị trường phân phối hoặc địa điểm bán hàng. Nếu không có thông tin, hãy trả về ''.",
    )
]

# ================================MODEL=========================  

output_parser_20 = StructuredOutputParser.from_response_schemas(response_schemas_20)
format_instructions_20 = output_parser_20.get_format_instructions()
prompt_20 = PromptTemplate(
    template="""
    Bạn là chuyên gia trong lĩnh vực ngân hàng, đang thực hiện thẩm định hồ sơ vay vốn của một hộ kinh doanh hoặc doanh nghiệp.
    
    Nhiệm vụ của bạn là trích xuất thông tin tương ứng với từng thuộc tính bên dưới từ đoạn văn bản đầu vào. 
    Vui lòng tìm kiếm thông tin chính xác nhất. Nếu không có thông tin hoặc không chắc chắn, hãy trả về '' (chuỗi rỗng).
    
    Văn bản đầu vào: 
    {text}
    
    {format_instructions_20}
    """,
    input_variables=["text"],
    partial_variables={"format_instructions_20": format_instructions_20},
)
llm_20=ChatOllama(model=config.model_llm, format = 'json', temperature=0, base_url=config.base_url,keep_alive = -1)
chain_20 = prompt_20 | llm_20
 
dict_nltc = {
    "HTK": "Hàng tồn kho",
    "tr đồng": "triệu đồng",
    "trđ": "triệu đồng",
    "trđồng": "triệu đồng",
}
list_dv_dr = ["đầu vào", "đầu ra"]
list_kn = ["kinh doanh", "kinh nghiệm", "thâm niên"]
 
 
# replace dict nltc
def replace_text(text):
    pattern = re.compile("|".join(re.escape(key) for key in dict_nltc.keys()))
    result = pattern.sub(lambda match: dict_nltc[match.group(0)], text)
    return result
 
 
# check result not null
def all_values_not_null(d):
    return all(value is not None for value in d.values())
 
 
# find emtpy entity
def find_empty_attributes(res):
    empty_attributes = [attribute for attribute, value in res.items() if value == ""]
    return ", ".join(empty_attributes)
 
 
# extract function
 
 
def process_business(text):
 
    res = None
    empty_attributes = ""
    text = replace_text(str(text))
 
    if text == "\n":
        res = {
            "mặt hàng kinh doanh": "",
            "địa điểm": "",
            "kinh nghiệm": "",
            "phương thức thanh toán": "",
            "phương thức mua bán": "",
            "kho hàng": "",
        }
 
    else:
        business_instance = chain_20.invoke({"text": text})
        res = json.loads(business_instance.content)
#         try:
#             res = json.loads(business_instance.content)
#         except Exception as e:
#             res = json.loads(business_instance)
        
    if res.get("kinh nghiệm", "").lower() == "không có thông tin":
        res["kinh nghiệm"] == ""
    list_kn = ["kinh nghiệm", "thâm niên"]
    if ((res.get("kinh nghiệm", "") == "")) and any(i in text.lower() for i in list_kn):
        res["kinh nghiệm"] = "Có kinh nghiệm kinh doanh"
 
    empty_attributes = find_empty_attributes(res)
 
    list_dv_dr = ["đầu vào", "đầu ra"]
 
    missing_attributes = [i for i in list_dv_dr if i not in text.lower()]
 
    if missing_attributes:
        empty_attributes += ", " + ", ".join(missing_attributes)
 
    return empty_attributes, res
 
# ====================================MAIN-FUNCTION=============================
def DK114(row):

    try:
        #     row["GIẢI PHÁP"] = ""

        row["MẶT HÀNG KD"] = ""
        row["ĐỊA ĐIỂM"] = ""
        row["KINH NGHIỆM"] = ""
        row["PT THANH TOÁN"] = ""
        row["PT BÁN HÀNG"] = ""
        row["KHO HÀNG"] = ""
        row["ĐẦU VÀO"] = ""
        row["ĐẦU RA"] = ""
        
        text1 = str(row['PTK1']) 
        text2 = str(row['PTK2'])
        if 0 < len(text1.split()) < 50:
            text1=''
        if 0 < len(text2.split()) < 50:
            text2=''

        text = text1 + '\n' + text2
        text = text.replace('hàng tồn kho', '')
        empty_attributes, res = process_business(text)
        
        if  row['KHOẢN PHẢI THU'] == 'Không có thông tin' or row['KHOẢN PHẢI THU'] == '' :
            empty_attributes=empty_attributes + ', ' + 'giá trị phải thu'
            
        if  row['HÀNG TỒN KHO'] == 'Không có thông tin' or row['HÀNG TỒN KHO'] == '' :
            empty_attributes=empty_attributes + ', ' + 'giá trị tồn kho'
        
        if  row['LỢI NHUẬN'] == 'Không có thông tin' or row['LỢI NHUẬN'] == '' :
            empty_attributes=empty_attributes + ', ' + 'lợi nhuận'
            
        if row["DOANH THU"] == 'Không có thông tin' or row["DOANH THU"] == '' :
            empty_attributes = empty_attributes + ', ' + 'doanh thu'
            
#         if (row["DOANH THU"] == '') and (row['LỢI NHUẬN'] == ''):
#             empty_attributes = empty_attributes + ', ' + 'doanh thu'+ ', '+ 'lợi nhuận'
        # print(res)
        row["MẶT HÀNG KD"] = str(res.get("mặt hàng kinh doanh", ""))
        row["ĐỊA ĐIỂM"] = str(res.get("địa điểm", ""))
        row["KINH NGHIỆM"] = str(res.get("thời gian kinh doanh", ""))
        row["PT THANH TOÁN"] = str(res.get("phương thức thanh toán", ""))
        row["PT BÁN HÀNG"] = str(res.get("phương thức mua bán", "")) 
        row["KHO HÀNG"] = str(res.get("kho hàng", ""))
        row["ĐẦU VÀO"] = str(res.get("đầu vào", ""))
        row["ĐẦU RA"] = str(res.get("đầu ra", ""))
        
#         #lưu kho
#         if re.search(r'lưu kho', text, re.IGNORECASE):
#             # Tìm vị trí bắt đầu của "lưu kho"
#             match = re.search(r'lưu kho', text, re.IGNORECASE)
#             if match:
#                 start = match.end()  # Vị trí sau cụm "lưu kho"
#                 # Lấy phần còn lại của text sau "lưu kho"
#                 after_text = text[start:].strip()
#                 # Tách 7 từ tiếp theo
#                 words = after_text.split()
#                 kho_hang_info = ' '.join(words[:7])
#                 row["KHO HÀNG"] = f"lưu kho {kho_hang_info}"

#             # Cập nhật empty_attributes
#             empty_attributes = re.sub(r'kho hàng,', ',', empty_attributes)
            
        #kho hàng
        if re.search(r'kho tại', text, re.IGNORECASE):
            # Tìm vị trí bắt đầu của "lưu kho"
            match = re.search(r'kho tại', text, re.IGNORECASE)
            if match:
                start = match.end()  # Vị trí sau cụm "lưu kho"
                # Lấy phần còn lại của text sau "lưu kho"
                after_text = text[start:].strip()
                # Tách 7 từ tiếp theo
                words = after_text.split()
                kho_hang_info = ' '.join(words[:7])
                row["KHO HÀNG"] = f"kho tại {kho_hang_info}"

            # Cập nhật empty_attributes
            empty_attributes = re.sub(r'kho hàng,', ',', empty_attributes)
        #=======================
        elif row["KHO HÀNG"] == 'kho hàng' or row["KHO HÀNG"] == 'Kho hàng':
            if not re.search(r'Kho hàng', text, re.IGNORECASE):
                row["KHO HÀNG"] = ''
                empty_attributes = empty_attributes + ', ' + 'kho hàng'
        elif re.search(r'không có',str(row["KHO HÀNG"]), re.IGNORECASE):
            row['KHO HÀNG'] = ''
            empty_attributes = empty_attributes + ', ' + 'kho hàng'
            
        elif pd.isna(row['KHO HÀNG']):
            if re.search(r'ại cơ sở kinh doanh của khách hàng', text, re.IGNORECASE):
                row["KHO HÀNG"] = "tại cơ sở kinh doanh"
                empty_attributes= re.sub(r'kho hàng,',',',empty_attributes)
                
        kho_hang_keyword = row.get("KHO HÀNG", "")
        
        if kho_hang_keyword and re.search(kho_hang_keyword, text, re.IGNORECASE):
            match = re.search(kho_hang_keyword, text, re.IGNORECASE)
            if match:
                start = match.end()
                after_text = text[start:].strip()
                words = after_text.split()
                seven_words_after = ' '.join(words[:7])
                # print(f"7 từ sau '{kho_hang_keyword}': {seven_words_after}")
                row["KHO HÀNG"] = f"{kho_hang_keyword} {seven_words_after}"

        # kinh nghiệm 
        if pd.isna(row['KINH NGHIỆM']):
            if re.search(r'lâu năm', text, re.IGNORECASE):
                row['KINH NGHIỆM'] = 'lâu năm'
                empty_attributes= re.sub(r'kinh nghiệm,',',',empty_attributes)

        if empty_attributes:
            row["DK114"] = f'FAIL'
            return f"""-Chưa thỏa mãn điều kiện 114 Đề nghị RM bổ sung các thông tin: \n{empty_attributes}"""

        if all_values_not_null(res):
            row["DK114"] = "PASS"
            return None
#         return row

        
    except Exception as e:
        logger.error(f"An error occurred in DK20: {e}")
        row["DK114"] = "FAIL"
        return None