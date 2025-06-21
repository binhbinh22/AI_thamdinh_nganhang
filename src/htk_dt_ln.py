import os
import sys

sys.path.append(os.getcwd())
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
import config
## ==============SCHEMA===================================
import unicodedata
dict_nltc = {
    "tr đồng": " triệu đồng",
    "trđ": " triệu đồng",
    "trd": " triệu đồng",
    "tr/": " triệu đồng/ ",
    ", ": " ",
    "tr": " tr",
    "thu nhập":"lợi nhuận",
    "khoảng":" ",
    "khách hàng":" ",
    "HTK": "hàng tồn kho",
    "KPT": "khoản phải thu",
    "bình quân": " ",
    "lợinhuận": "lợi nhuận",
    "doanhthu": "doanh thu",
    "lợi nhuận": "lợi nhuận: ",
    "ln": "lợi nhuận:",
    "dt": "doanh thu",
    "tương đương": "",
    "tỷ suất": "",
    "trung bình": " ",
    "tương ứng" : "",
    "đạt" : "",
    "mỗi": "",
    "dthu":"doanh thu",
    "doanh số": "doanh thu",
    "ước tính":"",
}
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def remove_vietnamese_accent(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
def replace_text(text):
    pattern = re.compile("|".join(re.escape(key) for key in dict_nltc.keys()))
    result = pattern.sub(lambda match: dict_nltc[match.group(0)], text)
    return result

def replace_text_kpt(text):
    pattern = re.compile("|".join(re.escape(key) for key in dict_nltc.keys()))
    result = pattern.sub(lambda match: dict_nltc[match.group(0)], text)
    return result



response_schemas = [
#     ResponseSchema(
#         name="khoản phải thu",
#         description="giá trị công nợ, giá trị phải thu, Nợ phải thu, giá trị khoản phải thu, KPT, công nợ, khoản phải thu hồ sơ, giá trị PTK",
#      ),
    ResponseSchema(
        name="hàng tồn kho",
        description="giá trị hàng tồn kho, hàng tồn kho, HTK, lượng hàng tồn kho, giá trị HTK, hàng tồn kho hiện nay",
    ),    
#     ResponseSchema(
#         name="doanh thu",
#         description="doanh thu, Doanh thu, định dạng: số tiền/đơn vị thời gian",
#     ),
#         ResponseSchema(
#         name="lợi nhuận",
#         description="lợi nhuận, thu nhập, lợi nhuận bình quân,LN, mức thu thập, mức thu nhập bình quân, nguồn thu nhập tính theo đơn vị thời gian",
#     ),
]
 
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
 
format_instructions = output_parser.get_format_instructions()
 
prompt = PromptTemplate(
    template="""
    Bạn là chuyên gia AI thông minh trích xuất thông tin hữu ích trong lĩnh vực kinh doanh.
    Hãy đọc thật kĩ, hiểu nội dung và trích xuất thông tin chính xác nhất theo từng thuộc tính trong đoạn văn bản sau.
    Hãy suy luận và đưa ra kết quả cuối cùng.
    Hãy trả về kết quả thỏa mãn đồng thời các điều kiện chú ý cho mỗi thuộc tính, nếu 1 điều kiện không đúng, trả về '' cho thuộc tính đó.
    Chú ý đặc biệt: chỉ đưa ra các giá trị phải có đơn vị tiền tệ đi kèm, nếu không phải giá trị tiền, hãy trả về ''.
    Chú ý: hãy chắc chắn có thông tin về các thuộc tính thì trả về kết quả, nếu không có thông tin trả về ''.
    Nếu kết quả có kí tự '-' hoặc '%' thì trả về ''.

    Văn bản: {text}
 
    {format_instructions}""",
    input_variables=["text"],
    partial_variables={"format_instructions": format_instructions},
)



llama = OllamaLLM(model=config.model_llm,format = 'json',temperature=0,base_url=config.base_url)
# llama = ChatOllama(model="llama3.1",format = 'json',temperature=0,base_url='http://10.233.85.97:11434')
chain = prompt | llama



list_DK30 = ["ton kho","tk","tai kho"]
def check_DK30(text):
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', str(text)).strip().lower() 
    text = replace_text(text)
    text = re.sub(r'(?<=\n)\d+\.\s*|\ \*', '', text)  
    text_no = remove_vietnamese_accent(text)
    text_DK30 = []  

    for term in list_DK30:
        term = term.lower()
        
        matches = list(re.finditer(re.escape(term), text_no))
        
        for match in matches:
            start_index = match.end() 
            words_after = text[start_index:].split()[:30]
            
            if words_after:  
                text_DK30.append('\n'+str(term)+' '+ ' '.join(words_after))

    return ' '.join(text_DK30) 

#=====Doanh thu=========
prompt_dt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Bạn là chuyên gia hữu ích trong lĩnh vực kinh doanh.    
            Nhiệm vụ của bạn là trích xuất số tiền và đơn vị theo thời gian của giá trị doanh thu trong đoạn văn bản phân tích hồ sơ vay vốn.
            Định dạng: Tiền + đơn vị/thời gian 
            Ví dụ: 
            input: "",
            Kết quả: {{"doanh thu":''}},
            
            input: doanh thu = ~ 3.5 tỷ đồng/năm,
            Kết quả: {{"doanh thu":'3.5 tỷ đồng/năm'}},
            
            input: doanh thu tháng: 3,600,000,000 đồng,
            kết quả: {{"doanh thu":'3,600,000,000 đồng/tháng'}},
            
            
            input: doanh thu bình quân là 3.000.000.000 đồng/tháng,
            Kết quả: doanh thu":'3.000.000.000 đồng/tháng,
            
            input: Doanh thu hiện tại qua phỏng vấn KH trong 1 tháng ~ 1.600 trđ,
            Kết quả: {{"doanh thu":' 1.600 trđ/tháng'}},
            
            input: - Tổng doanh thu 7 ngày từ 24/07 đến ngày 30 /07/2023: ~ 619 triệu đồng, Doanh thu bình quân ngày là: ~88 triệu đồng, Doanh thu bình quân năm với số ngày thực tế 345 ngày/ năm: ~ 30 tỷ đồng,
            Kết quả: {{"doanh thu":'30 tỷ đồng/năm'}},
            
            input: Doanh thu 3 ngày: 270,000,000 đồng;,
            Kết quả: {{"doanh thu":'270,000,000 đồng/3 ngày'}},
            
            input: Doanh thu bình quân là 291.4tr đồng/ 7 ngày kiểm tra, tương ứng doanh thu bình quân năm là 14.989.656.600 đồng,
            Kết quả: {{"doanh thu":'14.989.656.600 đồng/năm'}},
            
            input: Doanh thu 1 tháng của KH ~ 8.2 tỷ đồng/tháng, 
            Kết quả: {{"doanh thu":'8.2 tỷ đồng/tháng'}},
            
            input:doanh thu là doanh thu của HKD theo hồ sơ cung cấp là 80 tỷ < 100 tỷ ,doanh thu hkd là 80 tỷ <100 tỷ 
            Kết quả: {{"doanh thu":''}},
            
            input: Tổng doanh thu ĐVKD đề xuất là 98.5 tỷ đồng đáp ứng theo TB 12,
            Kết quả: {{"doanh thu":''}},
            
            input: doanh thu cần bổ sung vào 31 tỷ,
            Kết quả: {{"doanh thu":''}},
            
            input: Doanh thu: 360,000,000 đồng,
            kết quả:  {{"doanh thu":''}},
            
            input: Doanh thu: 2 tỷ đồng,
            kết quả:  {{"doanh thu":''}},
                
            input: "",
            Kết quả: {{"doanh thu":''}},
            
            Kết quả bạn trả về của giá trị theo format sau:
            {{'doanh thu': Tiền + đơn vị/thời gian }}.
            
            Chú ý: Nếu không xác định được giá trị doanh thu hoặc bạn không chắc chắn, hãy trả về None JSON. Thông thường giá trị 
            doanh thu nằm sau từ doanh thu.
            
            """,
        ),
        ("human", "{input}"),
    ]
)

chain_dt = prompt_dt | llama


list_dt = ["doanh thu","DT"]

def check_dt(text):
    text = text.lower()
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', str(text)).strip().lower() 
    text = replace_text(text)
    text = re.sub(r'(?<=\n)\d+\.\s*|\ \*', '', text)  # xóa 10. 2. - 
    text_no = remove_vietnamese_accent(text)
    text = re.sub(r'\s*\d+(\.\d+)?%\s*', ' ', text).strip()  # loại bỏ số và %
    text = re.sub(r'(?<=\n)\d+\.\s*|\\s*', '', text)  
    text = re.sub(r'trung bình', '', text)
    text_dt = []  

    for term in list_dt:
        term = term.lower()
        matches = list(re.finditer(re.escape(term), text))
        
        for match in matches:
            # Vị trí bắt đầu và kết thúc của từ tìm được
            start_index = match.start()
            end_index = match.end()

            # Lấy 7 từ trước từ tìm được
            words_before = text[:start_index].split()[-7:]  # 7 từ trước
            words_before = [re.sub(r'\d+', '', word) for word in words_before] # loại bỏ các số
            words_after = text[end_index:].split()[:18]     # 16 từ sau

            # Kết hợp từ khóa, 7 từ trước và 16 từ sau
            combined_text = '\n' + ' '.join(words_before) + ' ' + term + ' ' + ' '.join(words_after)
#             combined_text = '\n' + ' ' + term + ' ' + ' '.join(words_after)
            text_dt.append(combined_text)
    
    return ' '.join(text_dt)

import re
import json

def revenue(text):
    """
    Trích xuất giá trị doanh thu từ văn bản dựa trên regex.
    """
    import re

    # Tập hợp các biểu thức regex để tìm kiếm doanh thu
    patterns = [
        r"doanh thu[^\d]*([\d,.]+(?: tỷ| triệu| nghìn| đồng| VND)+/(?:tháng|năm))",  # Pattern cũ
        r"doanh thu\s*(tháng|năm):?\s*([\d,.]+(?: tỷ| triệu| nghìn| đồng| đ| VND)+)",  # Pattern bổ sung: thời gian trước, số tiền sau
    ]

    # Duyệt qua từng pattern để tìm khớp
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            # Kiểm tra các group từ pattern
            if len(match.groups()) > 1:
                period = match.group(1).strip().lower()  # Bắt được thời gian (tháng/năm)
                amount = match.group(2).strip()          # Bắt được số tiền
                return {"doanh thu": f"{amount}/{period}"}
            else:
                # Nếu chỉ có số tiền và đơn vị thời gian
                return {"doanh thu": match.group(1).strip()}

    # Trả về giá trị rỗng nếu không khớp với bất kỳ pattern nào
    return {"doanh thu": ""}


#========Loi nhuan======
prompt_ln = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Bạn là chuyên gia hữu ích trong lĩnh vực kinh doanh.    
            Nhiệm vụ của bạn là trích xuất số tiền và đơn vị theo thời gian của giá trị lợi nhuận/thu nhập trong đoạn văn bản phân tích hồ sơ vay vốn.
            Định dạng: Tiền + đơn vị/thời gian 
            Ví dụ: 
            input: "",
            Kết quả: {{"lợi nhuận":''}},
            
            input: Lợi nhuận:  162,590,000 đồng/tháng,
            Kết quả: {{"lợi nhuận":'162,590,000 đồng/tháng'}},
            
            input: lợi nhuận = ~ 3.5 tỷ đồng/năm,
            Kết quả: {{"lợi nhuận":'3.5 tỷ đồng/năm'}},
            
            input:lợi nhuận: 125.5 triệu đồng/tháng,
            Kết quả: {{"lợi nhuận":'125.5 triệu đồng/tháng'}},
            
            input: thu nhập hiện tại qua phỏng vấn KH trong 1 tháng ~ 1.600 trđ,
            Kết quả: {{"lợi nhuận":' 1.600 trđ/tháng'}},
            
            input: - Tổng lợi nhuận 7 ngày từ 24/07 đến ngày 30 /07/2023: ~ 619 triệu đồng, lợi nhuận bình quân ngày là: ~88 triệu đồng, lợi nhuận bình quân năm với số ngày thực tế 345 ngày/ năm: ~ 30 tỷ đồng,
            Kết quả: {{"lợi nhuận":'30 tỷ đồng/năm'}},
            
            input: lợi nhuận 3 ngày: 270,000,000 đồng;,
            Kết quả: {{"lợi nhuận":'270,000,000 đồng/3 ngày'}},
            
            input: lợi nhuận bình quân là 291.4tr đồng/ 7 ngày kiểm tra, tương ứng lợi nhuận bình quân năm là 14.989.656.600 đồng,
            Kết quả: {{"lợi nhuận":'14.989.656.600 đồng/năm'}},
            
            input: thu nhập 1 tháng của KH ~ 8.2 tỷ đồng/tháng, 
            Kết quả: {{"lợi nhuận":'8.2 tỷ đồng/tháng'}},
            
            input: Lợi nhuận của khách hàng khoảng  162,590,000 đồng/tháng,
            Kết quả: {{"lợi nhuận":'162,590,000 đồng/tháng'}},
            
            input: lợi nhuận tháng: 100,192,480 đồng,
            Kết quả: {{"lợi nhuận":'100,192,480 đồng/tháng'}},
            
            input:lợi nhuận là lợi nhuận của HKD theo hồ sơ cung cấp là 80 tỷ < 100 tỷ ,lợi nhuận hkd là 80 tỷ <100 tỷ 
            Kết quả: {{"lợi nhuận":''}},
            
            input: lợi nhuận cần bổ sung vào 31 tỷ,
            Kết quả: {{"lợi nhuận":''}},
            
            input: lợi nhuận / tháng: 40,080,960 đồng
            Kết quả: {{"lợi nhuận":'40,080,960 đồng/tháng'}},

            input: lợi nhuận tháng: 100,192,480 đồng,
            Kết quả: {{"lợi nhuận":'100,192,480 đồng/tháng'}},

            input: "",
            Kết quả: {{lợi nhuận":''}},
            
            Kết quả bạn trả về của giá trị theo format sau:
            {{'lợi nhuận': Tiền + đơn vị/thời gian }}.
            
            Chú ý:Giá trị lợi nhuận nằm sau từ lợi nhuận/thu nhập. Nếu không xác định được giá trị lợi nhuận/thu nhập hoặc bạn không chắc chắn, hãy trả về None JSON. Giá trị 
            lợi nhuận nằm sau từ lợi nhuận/thu nhập.
            
            """,
        ),
        ("human", "{input}"),
    ]
)

chain_ln = prompt_ln | llama


list_ln = ["lợi nhuận","LN","nhuận","loi nhuan","lợi nhận","lợi"]
def check_ln(text):
    text = unicodedata.normalize('NFC', text)
    text = text.lower()
    text = re.sub(r'\s*\d+(\.\d+)?%\s*', ' ', text).strip()  # loại bỏ số và %
    text = re.sub(r'\s+', ' ', str(text)).strip().lower() # khoảng trắng thừa
    text = replace_text(text)
    text = re.sub(r'(?<=\n)\d+\.\s*|\ \*', '', text)  # xóa 10. 2. - 
    text_no = remove_vietnamese_accent(text)
    text = re.sub(r'trung bình', '', text)
    text_ln = []  

    for term in list_ln:
        term = term.lower()
        
        matches = list(re.finditer(re.escape(term), text_no))
        
        for match in matches:
            # Vị trí bắt đầu và kết thúc của từ tìm được
            start_index = match.start()
            end_index = match.end()

            # Lấy 7 từ trước từ tìm được
            words_before = text[:start_index].split()[-10:]  # 7 từ trước
            words_before = [re.sub(r'\d+', '', word) for word in words_before]
            words_before = [re.sub(r',', '', word) for word in words_before]
            
            words_after = text[end_index:].split()[:19]     # 16 từ sau

            # Kết hợp từ khóa, 7 từ trước và 16 từ sau
            combined_text = '\n' + ' '.join(words_before) + ' ' + 'lợi nhuận'   + ' '.join(words_after)
            text_ln.append(combined_text)

    return ' '.join(text_ln) 


import re
import json

def profit(text):
    """
    Trích xuất giá trị lợi nhuận từ văn bản dựa trên regex.
    Trả về một đối tượng dict trực tiếp.
    """
    import re

    # Biểu thức regex tìm kiếm giá trị lợi nhuận
    pattern = r"lợi nhuận[^\d]*([\d,.]+(?: tỷ| triệu| nghìn| đồng| VND)+/(?:tháng|năm))"

    # Tìm kiếm kết quả
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if match:
        # Trả về giá trị phù hợp
        return {"lợi nhuận": match.group(1).strip()}
    else:
        # Trả về giá trị rỗng nếu không khớp
        return {"lợi nhuận": ""}