import json
import gc
import logging
import ast
import gc
import re
import time
from log import *

def dk39(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])
 
    if re.search(r'Hình ảnh', ptk1, re.IGNORECASE) or re.search(r'Ảnh chụp', ptk1, re.IGNORECASE) or re.search(r'Hình ảnh', ptk2, re.IGNORECASE) or re.search(r'Ảnh chụp', ptk2, re.IGNORECASE) or re.search(r'Biển hiệu', ptk2, re.IGNORECASE) or re.search(r'Biển hiệu', ptk1, re.IGNORECASE):
        row['dk39'] = False
        return '''- Chưa thỏa mãn điều kiện 39:\n -> Giải pháp: Hình ảnh cơ sở kinh doanh phải thể hiện được tổng quát cơ sở kinh doanh, quy mô kinh doanh. Đảm bảo:
- Thể hiện bên trong, ngoài và tổng thể địa điểm, vị trí, thể hiện rõ địa chỉ  kinh doanh và quy mô kinh danh của KH và các căn liền kề (nếu có).
- Ảnh chụp qua app timestamp/MB capture có thông tin: thời gian chụp ảnh + bản đồ, toạ độ, địa chỉ của vị trí chụp ảnh
- Trường hợp không có biển hiệu kinh doanh: Làm rõ  nguyên nhân không biển hiệu tại mục Phân tích khác
- Trường hợp biển hiệu có thông tin tên/SĐT không phải của khách hàng: Đàm phán khách hàng bổ sung thông tin liên hệ trên biển hiệu hoặc Giải trình rõ nguyên nhân)'''
    row['dk39'] = None
    return None
 
