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
 
gc.collect()
response_schemas = [
#     ResponseSchema(
#         name="khoản phải thu",
#         description="giá trị công nợ, giá trị phải thu, Nợ phải thu, giá trị khoản phải thu, KPT, công nợ, khoản phải thu hồ sơ, giá trị PTK",
#      ),
    ResponseSchema(
        name="hàng tồn kho",
        description="giá trị hàng tồn kho, hàng tồn kho, HTK, lượng hàng tồn kho, giá trị HTK, hàng tồn kho hiện nay",
    ),    
    ResponseSchema(
        name="doanh thu",
        description="doanh thu, Doanh thu, DT theo thời gian",
    ),
        ResponseSchema(
        name="lợi nhuận",
        description="lợi nhuận, lợi nhuận bình quân,LN, mức thu thập, mức thu nhập bình quân, nguồn thu nhập",
    ),
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
 
 
llama = OllamaLLM(model=config.llm_number,format = 'json',temperature=0,base_url=config.port)
# llama = ChatOllama(model="llama3.1",format = 'json',temperature=0,base_url='http://10.233.85.97:11434')
chain = prompt | llama