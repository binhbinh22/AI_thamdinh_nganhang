import re
def safe_extract_float(value, default=0.0, unit_to_remove=' tỷ đồng'):
    """
    Safely extracts a float from a string, removing unwanted units.
    If the value cannot be converted to a float, returns the default value.
    """
    if value and isinstance(value, str):  # Check if value is a non-empty string
        # Try to clean up and convert the value
        try:
            return float(value.replace(unit_to_remove, '').strip())
        except ValueError:  # Handle case where value is not numeric
            return default
    return default
def convert_money(data):
    def convert(value):
        if value is None or value.strip() == "":
            return ""
 
        # Bỏ các kí tự trong dấu ngoặc đơn và sau dấu '-'
        value = re.sub(r'\(.*?\)', '', value).lower().strip()
        value = re.sub(r'^.*?-', '', value).strip()
        value = re.sub(r'\+.*', '', value).strip()
        print(value)
        if "%" in value or 'JSON' in value or 'm' in value or 'h' in value or '/' in value:
            return "" 
        # Xử lý các giá trị có đơn vị tỷ hoặc ty
        if "tỷ" in value or "ty" in value or "tỉ" in value or "ti" in value:
            value = value.replace(',', '.')
            amount = re.sub(r'[^\d.]', '', value)
            if amount.count('.') > 1:
                amount = amount.replace('.', '', amount.count('.') - 1)
            amount = float(amount) if amount else 0
            return f"{amount} tỷ đồng"
 
        # Xử lý các giá trị triệu
        if "triệu" in value or "tr" in value or "trđ" in value:
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e3 if amount else 0
            return f"{amount} tỷ đồng"
        # Xử lý các giá trị nghìn
        elif "nghìn" in value:
            value = value.replace('.', '')
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e6 if amount else 0
            return f"{amount} tỷ đồng"
        # Xử lý các giá trị đồng hoặc đ
        elif "đồng" in value or "đ" or "vnd" or "vnđ" in value:
            value = value.replace('.', '')
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e9 if amount else 0
            return f"{amount} tỷ đồng"
        # Nếu không có đơn vị, trả về 0 tỷ đồng
        else:
            return ""
 
    # Áp dụng hàm convert cho từng giá trị trong data
    converted_data = {key: convert(value) for key, value in data.items()}
 
    return converted_data
 
def convert_money_dtln(data):
    def convert(value):
        if value is None or value.strip() == "":
            return ""
        if "%" in value or 'JSON' in value or 'm' in value:
            return ""
 
        # Bỏ các kí tự trong dấu ngoặc đơn và trước dấu '-'
        value = re.sub(r'\(.*?\)', '', value).lower().strip()
        value = re.sub(r'^.*?-', '', value).strip()
        value = re.sub(r'\+.*', '', value).strip()
        is_month = "tháng" in value #check month
 
        if "tỷ" in value or "ty" in value or "tỉ" in value or "ti" in value:
            value = value.replace(',', '.')
            amount = re.sub(r'[^\d.]', '', value)
            if amount.count('.') > 1:
                amount = amount.replace('.', '', amount.count('.') - 1)
            amount = float(amount) if amount else 0
            return f"{amount * (12 if is_month else 1)} tỷ đồng/năm"
 
        if "triệu" in value or "tr" in value or "trđ" in value or "triệu đồng" in value:
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e3 if amount else 0
            return f"{amount * (12 if is_month else 1)} tỷ đồng/năm"
 
        if "nghìn" in value:
            value = value.replace('.', '')
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e6 if amount else 0
            return f"{amount * (12 if is_month else 1)} tỷ đồng/năm"
 
        if "đồng" in value or "đ" in value or "vnd" in value or "vnđ" in value:
            value = value.replace('.', '')
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e9 if amount else 0
            return f"{amount * (12 if is_month else 1)} tỷ đồng/năm"
        else:
            return ""
    converted_data_dtln = {key: convert(value) for key, value in data.items()}
 
    return converted_data_dtln