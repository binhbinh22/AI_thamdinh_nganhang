import os
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_ollama.llms import OllamaLLM
from langchain_experimental.llms.ollama_functions import OllamaFunctions  # type: ignore
from langchain.output_parsers import ResponseSchema
from langchain_community.chat_models import ChatOllama
from langchain.output_parsers import StructuredOutputParser
from langchain_core.prompts import ChatPromptTemplate
import json
import gc
import logging
import ast
import gc
import re
from langchain_core.prompts import ChatPromptTemplate
from log import *
import pandas as pd
import config

## ==============SCHEMA===================================
# Schema for structured response
response_schemas_20 = [
    ResponseSchema(
        name="mặt hàng kinh doanh",
        description="Mặt hàng kinh doanh là sản phẩm, mặt hàng mà khách hàng kinh doanh, nếu không có thông tin hãy trả về ''.",
    ),
    ResponseSchema(name="địa điểm", description="Địa điểm kinh doanh, địa chỉ doanh nghiệp của khách hàng, nếu không có thông tin hãy trả về ''."),
    ResponseSchema(
        name="kinh nghiệm",
        description="Số năm kinh nghiệm buôn bán, thâm niên kinh doanh quản lý",
    ),
    ResponseSchema(
        name="phương thức thanh toán",
        description="Phương thức thanh toán tiền mặt,trích công nợ, chính sách công nợ...",
    ),
 
    ResponseSchema(
        name="phương thức mua bán",
        description="Các loại hình buôn bán: Bán lẻ, bán buôn, bán sỉ, buôn chuyến...",
    ),
    ResponseSchema(
        name="kho hàng",
        description="Loại kho lưu trữ: Kho hàng, kho lạnh, lưu kho, xưởng, nhà riêng,...",
    ),
]
 
# ================================MODEL=========================  
 
output_parser_20 = StructuredOutputParser.from_response_schemas(response_schemas_20)
format_instructions_20 = output_parser_20.get_format_instructions()
prompt_20 = PromptTemplate(
    template="""
    Bạn là chuyên gia AI trong lĩnh vực kinh doanh.
    Hãy trích xuất thông tin theo từng thuộc tính trong đoạn văn bản sau.
    Hãy đưa ra thông tin chính xác nhất. 
    Nếu không có thông tin của các thuộc tính, hoặc không chắc chắn, hãy trả về ''.
    Văn bản: {text}
    {format_instructions_20}""",
    input_variables=["text"],
    partial_variables={"format_instructions_20": format_instructions_20},
)
 
llm_20=ChatOllama(model=config.llm_text, format = 'json', temperature=0.2, base_url=config.port)
chain_20 = prompt_20 | llm_20
 
dict_nltc = {
    "HTK": "Hàng tồn kho",
    "tr đồng": "triệu đồng",
    "trđ": "triệu đồng",
    "trđồng": "triệu đồng",    
}
list_dv_dr = ["đầu vào", "đầu ra"]
list_kn = ["kinh doanh", "kinh nghiệm", "thâm niên"]
#replace dict nltc
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
    return ', '.join(empty_attributes)
# extract function
 
def process_business(text):
 
    res = None
    empty_attributes = ''
    text = replace_text(str(text))
 
    if text == '\n':
        res = { "mặt hàng kinh doanh": "", "địa điểm": "",  "kinh nghiệm": "", "phương thức thanh toán": "", "phương thức mua bán": "", "kho hàng": "" }
 
    else:
        business_instance = chain_20.invoke({"text": text})
        res = json.loads(business_instance.content)
    if  (res.get("kinh nghiệm", "").lower() == 'không có thông tin'):
        res['kinh nghiệm'] == ''
    list_kn = ["kinh nghiệm", "thâm niên"]
    if ((res.get("kinh nghiệm", "") == "") ) and any(i in text.lower() for i in list_kn):
        res["kinh nghiệm"] = "Có kinh nghiệm kinh doanh"
 
    empty_attributes = find_empty_attributes(res)
 
    list_dv_dr = ["đầu vào", "đầu ra"]
 
    missing_attributes = [i for i in list_dv_dr if i not in text.lower()]
 
    if missing_attributes:
        empty_attributes += ', ' + ', '.join(missing_attributes)
 
    return empty_attributes, res


def dk20(row):
 
    try:
        #     row["GIẢI PHÁP"] = ""
        row["MẶT HÀNG KD"] = ""
        row["ĐỊA ĐIỂM"] = ""
        row["KINH NGHIỆM"] = ""
        row["PT THANH TOÁN"] = ""
        row["PT MUA BÁN"] = ""
        row["KHO HÀNG"] = ""
        text1 = str(row['PTK1']) 
        text2 = str(row['PTK2'])
        if 0 < len(text1.split()) < 50:
            text1=''
        if 0 < len(text2.split()) < 50:
            text2=''
 
        text = text1 + '\n' + text2
        empty_attributes, res = process_business(text)
        if  row['KHOẢN PHẢI THU'] == 'Không có thông tin' or row['KHOẢN PHẢI THU'] == '' :
            empty_attributes=empty_attributes + ', ' + 'khoản phải thu'
        if  row['HÀNG TỒN KHO'] == 'Không có thông tin' or row['HÀNG TỒN KHO'] == '' :
            empty_attributes=empty_attributes + ', ' + 'hàng tồn kho'
        if  row['LỢI NHUẬN'] == 'Không có thông tin' or row['LỢI NHUẬN'] == '' :
            empty_attributes=empty_attributes + ', ' + 'lợi nhuận'
        if row["DOANH THU"] == 'Không có thông tin' or row["DOANH THU"] == '' :
            empty_attributes = empty_attributes + ', ' + 'doanh thu'
#         if (row["DOANH THU"] == '') and (row['LỢI NHUẬN'] == ''):
#             empty_attributes = empty_attributes + ', ' + 'doanh thu'+ ', '+ 'lợi nhuận'
        row["MẶT HÀNG KD"] = str(res.get("mặt hàng kinh doanh", ""))
        row["ĐỊA ĐIỂM"] = str(res.get("địa điểm", ""))
        row["KINH NGHIỆM"] = str(res.get("kinh nghiệm", ""))
        row["PT THANH TOÁN"] = str(res.get("phương thức thanh toán", ""))
        row["PT MUA BÁN"] = str(res.get("phương thức mua bán", "")) 
        row["KHO HÀNG"] = str(res.get("kho hàng", ""))
        if re.search(r'lưu kho', text, re.IGNORECASE):
            row["KHO HÀNG"] = "lưu kho"
            empty_attributes= re.sub(r'kho hàng,','')
        if row["KHO HÀNG"] == 'kho hàng':
            if not re.search(r'kho hàng', text, re.IGNORECASE):
                row["KHO HÀNG"] = None
                empty_attributes = empty_attributes + ', ' + 'kho hàng'
        if re.search(r'không có',str(row["KHO HÀNG"]), re.IGNORECASE):
            row['KHO HÀNG'] = None 
            empty_attributes = empty_attributes + ', ' + 'kho hàng'
        if pd.isna(row['KHO HÀNG']):
            if re.search(r'ại cơ sở kinh doanh của khách hàng', text, re.IGNORECASE):
                row["KHO HÀNG"] = "tại cơ sở kinh doanh"
                empty_attributes= re.sub(r'kho hàng,','')
        if empty_attributes:
            return f"""- Chưa thỏa mãn điều kiện 20:\n -> Giải pháp là: Đề nghị RM bổ sung các thông tin: \n{empty_attributes}"""
 
        if all_values_not_null(res):
            return None
#         return row
 
        
    except Exception as e:
        logger.error(f"An error occurred in dk20: {e}")
        row["dk20"] = None
        return None
