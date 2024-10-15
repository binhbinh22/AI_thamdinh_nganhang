# llm = ChatOllama(model="llama3",format = 'json',temperature=0.2,base_url='http://10.233.85.97:11434')
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
import re
import config

prompt_kpt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Bạn là chuyên gia hữu ích trong lĩnh vực kinh doanh.    
            Nhiệm vụ của bạn là trích xuất số tiền và đơn vị của giá trị khoản phải thu hoặc giá trị công nợ trong đoạn văn bản phân tích hồ sơ vay vốn.
            Ví dụ: 
            input: "",
            Kết quả: {{"khoản phải thu":''}},
            input: Ước tính giá trị công nợ = ~ 3.5 tỷ đồng
            Kết quả: {{"khoản phải thu":'3.5 tỷ đồng'}},
            input: Công nợ bình quân là 3.000.000.000 đồng,
            Kết quả: khoản phải thu":'3.000.000.000 đồng,
            input: Khoản phải thu hiện tại qua phỏng vấn KH ~ 1.600 trđ,
            Kết quả: {{"khoản phải thu":' 1.600 trđ'}},
            input: Theo phỏng vấn KH : HTK đạt ~ 3 tỷ, Khoản phải thu đạt ~ 6.5 tỷ,
            Kết quả: {{"khoản phải thu":'6.5 tỷ '}},
            input: KPT bình quân 70 tỷ,
            Kết quả: {{"khoản phải thu":'70 tỷ'}},
            input: khoản phải thu: bình quân ~ 1,923,000,000 đồng, 
            Kết quả: {{"khoản phải thu":'1,923,000,000 đồng.'}},
 
            input: "",
            Kết quả: {{"khoản phải thu":''}},
            Kết quả bạn trả về của giá trị theo format sau:
            {{'khoản phải thu': giá trị khoản phải thu}}.
            Chú ý: Nếu không xác định được giá trị khoản phải thu hoặc bạn không chắc chắn, hãy trả về None JSON. Thông thường giá trị 
            khoản phải thu nằm sau từ Khoản phải thu.
 
            """,
        ),
        ("human", "{input}"),
    ]
)
llama = OllamaLLM(model=config.llm_number,format = 'json',temperature=0,base_url=config.port)

chain_kpt = prompt_kpt | llama
dict_nltc = {
    "KPT": "Khoản phải thu",
#     "HTK": "",
#     'hàng tồn kho':'',
#     'Hàng tồn kho':'',
#     "Doanh thu":'',
#     'doanh thu':'',
#     'lợi nhuận':'',
#     "Lợi nhuận":'',
#     "LN":'',
#     "DT":'',
    "tr đồng": "triệu đồng",
    "trđ": "triệu đồng",
}
 
def replace_text(text):
    pattern = re.compile("|".join(re.escape(key) for key in dict_nltc.keys()))
    result = pattern.sub(lambda match: dict_nltc[match.group(0)], text)
    return result
 
 
list_kpt = ["giá trị công nợ", "giá trị phải thu", "nợ phải thu", "khoản phải thu","công nợ","dư nợ"]
def check_kpt(text):
    text = replace_text(text)
    text = re.sub(r'(?<=\n)\d+\.\s*|\-\s*', '', text)  
    text = re.sub(r'\s+', ' ', str(text)).strip().lower() 
    text_kpt = []  
 
    for term in list_kpt:
        term = term.lower()
        matches = list(re.finditer(re.escape(term), text))
        for match in matches:
            start_index = match.end() 
            words_after = text[start_index:].split()[:18]
            if words_after:  
                text_kpt.append('\n'+str(term)+' '+ ' '.join(words_after))
 
    return ' '.join(text_kpt)