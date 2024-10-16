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
import config
prompt_34 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Bạn là chuyên gia hữu ích trong lĩnh vực kinh doanh. Hãy phân tích văn bản và xác định khách hàng có thành lập,
            sở hữu hay xây dựng doanh nghiệp tư nhân hay không ?
            Đừng nhẫm lẫn giữa doanh nghiệp tư nhân và hộ kinh doanh. Phân biệt doanh nghiệp tư nhân với hộ kinh doanh:
            1. Khái niệm:
            - Doanh nghiệp tư nhân là doanh nghiệp do một cá nhân làm chủ và tự chịu trách nhiệm bằng toàn bộ tài sản của mình về mọi hoạt động của doanh nghiệp.
            - Hộ kinh doanh do một cá nhân là công dân Việt Nam hoặc một nhóm người hoặc một hộ gia đình làm chủ, và chỉ được đăng ký kinh doanh tại một địa điểm,
            sử dụng không quá 10 lao động, không có con dấu và tự chịu trách nhiệm bằng toàn bộ tài sản của mình đối với hoạt động kinh doanh.
            2. Chủ thể thành lập:
            - Doanh nghiệp tư nhân: một cá nhân có đủ điều kiện theo quy định của pháp luật, có thể là công dân Việt Nam hoặc người nước ngoài.
            - Hộ kinh doanh: cá nhân là công dân Việt Nam, một nhóm người, một hộ gia đình.
            3. Quy mô:
            - Doanh nghiệp tư nhân: không giới hạn quy mô, vốn, không giới hạn số lượng lao động.
            - Hộ kinh doanh: số lượng lao động không quá 10 người.
            4. Địa điểm kinh doanh:
            - Doanh nghiệp tư nhân: được mở nhiều địa điểm, chi nhánh.
            - Hộ kinh doanh: không được mở nhiều địa điểm kinh doanh.
            Hãy trả về kết quả về theo format json: {{'Khách hàng có phải doanh nghiệp tư nhân hay không': Có/Không/Null}}
            Nếu không có đủ thông tin xác định khách hàng là hộ kinh doanh hay doanh nghiệp tư nhân hãy trả về None JSON.
            """,
        ),
        ("human", "{input}"),
    ]
)
llm_34 = ChatOllama(model='llama3.1',format = 'json',temperature=0.2,base_url=config.port)
chain_34 = prompt_34 | llm_34
 
# ======================================MAIN-FUNCTION===================================
 
def dk34(row):
    try:
        # Ghép các trường PTK1 và PTK2 và thay thế 'HKD' bằng 'Hộ kinh doanh'
        ptk1 = str(row.get('PTK1', ''))
        ptk2 = str(row.get('PTK2', ''))
        text = f"{ptk1} {ptk2}".replace('HKD', 'Hộ kinh doanh')
 
        # Gọi AI chain
        AI = chain_34.invoke({'input': text})
        # Điều kiện 1: Kiểm tra cột 'Pháp lý: ' chứa cụm 'Đăng ký kinh doanh'
        phap_ly = str(row.get('Pháp lý: ', ''))
        if not re.search(r'Đăng ký kinh doanh', phap_ly, re.IGNORECASE):
            row['dk34'] = None
            return None
    except Exception as e:
        logger.error(f"Error checking 'Pháp lý: ' condition in dk34: {e}")
        row['dk34'] = None
        return None
 
    try:
        # Điều kiện 2: Kiểm tra cột 'Đại diện pháp luật trên ĐVKD: ' chứa cụm 'Khách hàng là người đứng tên duy nhất'
        dai_dien = str(row.get('Đại diện pháp luật trên ĐVKD: ', ''))
        if not re.search(r'Khách hàng là người đứng tên duy nhất', dai_dien, re.IGNORECASE):
            row['dk34'] = None
            return None
    except Exception as e:
        logger.error(f"Error checking 'Đại diện pháp luật trên ĐVKD: ' condition in dk34: {e}")
        row['dk34'] = None
        return None
 
    try:
        # Điều kiện 3: Kết quả JSON trả về 'Có' cho câu hỏi 'Khách hàng có phải doanh nghiệp tư nhân hay không'
        data = json.loads(AI.content)
        if data.get('Khách hàng có phải doanh nghiệp tư nhân hay không') != 'Có':
            row['dk34'] = None
            return None
 
    except Exception as e:
        logger.error(f"Error processing AI response in dk34: {e}")
        row['dk34'] = None
        return None

 
    # Nếu thỏa mãn tất cả điều kiện, đánh dấu dk34 = False và trả về thông báo
    row['dk34'] = False
    return '''- Chưa thỏa mãn điều kiện 34: \n --> Giải pháp là: KH có đăng ký kinh doanh và có doanh nghiệp tư nhân + ĐKKD đứng tên Khách hàng: 
    Chuyển ĐKKD đứng tên vợ/chồng và tạo khoản vay đứng tên vợ/chồng'''