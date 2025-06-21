import re

def process_number(number):
    if "," in number and "." not in number:
        number = number.split(",")
        if len(number[-1]) != 3:
            number = ",".join(number[:-1]) + "." + number[-1]
        else:
            number = ",".join(number)
    if "." in number and "," not in number:
        number = number.split(".")
        if len(number[-1]) != 3:
            number = ",".join(number[:-1]) + "." + number[-1]
        else:
            number = ".".join(number)
    else:
        if len(number.split(",")[-1]) != 3:
            number = ",".join(number.split(",")[:-1]).replace(".", ",") + "." + number.split(",")[-1]
    return number

def convert_dt(data):
    def extract_amount(text):
        text = re.sub(r'\(.*?\)', '', text).lower().strip()  # loại bỏ kí tự trong () 
        text = re.sub(r'^.*?-', '', text).strip() # lấy kí tự sau -
        text = re.sub(r'^.*?~', '', text).strip() # lấy kí tự sau ~
#         text = re.sub(r'\~.*', '', text).strip() # lấy kí tự trước ~
        text = re.sub(r'm.*', 'm', text).strip() # lấy kí tự trước m
        
        numbers = re.findall(r"\b\d{1,4}(?:[.,]\d{1,3})*(?:[.,]\d{1,3})?\b", text)
        print(text)
        print(numbers)
        if len(numbers) == 1:
            numbers = numbers + ["1"]
        
        # Số lượng và thời gian
        amount_str, date_str = numbers[0], numbers[1]
        if ("tỷ" in text or "ty" in text or "tỉ" in text or "ti" in text) and len(amount_str)>7 :
            amount = amount_str.replace(',', '').replace(".","")
            amount = float(amount)
            amount = amount * 1e-9

        
        elif "tỷ" in text or "ty" in text or "tỉ" in text or "ti" in text:
            amount = amount_str.replace(',', '.')
            amount = float(amount)
        elif ("triệu" in text or "tr" in text or "trđ" in text or "triệu đồng" in text) and len(amount_str)>5:
            amount = amount_str.replace(',', '')
            if len(amount) >7:
                amount = float(amount)
                amount = amount * 1e-6
            else: 
                amount = float(amount)

        else:
            amount_str= process_number(amount_str)
            amount_str = amount_str.replace('.', '')
            try:
                amount = float(amount_str)
            except:
                amount_str = re.sub(r',','',amount_str)   #2,222tr=2222tr
                amount = float(amount_str)

        date = float(date_str)
        # Xác định hệ số tiền tệ
        if "tỷ" in text or "ty" in text or "tỉ" in text or "ti" in text:
            factor = 1
        elif "triệu" in text or "tr" in text or "trđ" in text or "triệu đồng" in text:
            print("v")
            factor = 1e-3
        elif "nghìn" in text:
            factor = 1e-6
        elif "đồng" in text or "vnd" in text or "vnđ" in text or "đ" in text:
            factor = 1e-9
        else:
            factor = 1e-9

        # Xử lý đơn vị thời gian
        if "ngày" in text or "day" in text or "ngay" in text:
            if date == 7:
                amount = (amount * factor) * 50
            elif date == 3:
                amount = (amount * factor) * 115
            elif date == 10:
                amount = (amount * factor) * 35
            else:
                amount = (amount * factor * 365) / date
        elif "tháng" in text or "month" in text or "thang" in text or "/th" in text:
            if date == 12:
                amount = amount * factor
            elif date == 1:
                amount = (amount * factor) * 12
            elif date == 3:
                amount = (amount * factor) * 4
            else:
                amount = (amount * factor * 12) / date
        else:
            amount = (amount * factor) / date

        return f'{amount} tỷ đồng/năm'
    convert_dt = {key: extract_amount(value) for key, value in data.items()}

    return convert_dt

def safe_extract_float(value, default=0.0, unit_to_remove=' tỷ đồng'):
    if value and isinstance(value, str): 
        try:
            return float(value.replace(unit_to_remove, '').strip())
        except ValueError:
            return default
    return default

def convert_money(data):
    def convert(value):
        if value is None or value.strip() == "":
            return ""
        # Loại bỏ tất cả các ký tự sau dấu gạch chéo "/" đầu tiên (bao gồm cả gạch chéo)
        value = re.sub(r'\/.*', '', value).strip()

#         # Loại bỏ tất cả dấu chấm "." khỏi chuỗi
#         value = re.sub(r'\.*', '', value).strip() 

        # Loại bỏ các nội dung bên trong dấu ngoặc đơn "(...)", bao gồm cả dấu ngoặc
        value = re.sub(r'\(.*?\)', '', value).lower().strip()

        # Loại bỏ tất cả ký tự trước và bao gồm dấu gạch ngang "-" đầu tiên
        value = re.sub(r'^.*?-', '', value).strip()
        value = re.sub(r'đ.*', 'đ', value).strip()      # lấy kí tự trước đ


        if any(x in value for x in ["%", "json", "tấn", "m", "h", "*","đơn"]):
            return ""
        
        # Xử lý các giá trị có dạng "1 tỷ 800 triệu", "1 tỷ 8", "2 tỷ 4", "1 tỷ 800"
        match = re.match(r'(\d+(\.\d+)?)\s*t[ỷỉi]\s*(\d+(\.\d+)?)?\s*(tr|triệu)?', value)
        if match:
            billion_part = float(match.group(1))  # Phần tỷ
            # Nếu có phần triệu hoặc số sau phần tỷ, chuyển đổi sang đơn vị tỷ
            if match.group(3):
                million_part = float(match.group(3)) / 10 if not match.group(5) else float(match.group(3)) / 1000
            else:
                million_part = 0

            total_amount = billion_part + million_part
            return f"{total_amount} tỷ đồng"
# 1 tỷ 800 triệu = 1.8 tỷ đồng
# 1 tỷ 8 = 1.8 tỷ đồng
# 2 tỷ 4 = 2.4 tỷ đồng
# 1 tỷ 800 = 1.8 tỷ đồng

        if "tỷ" in value or "ty" in value or "tỉ" in value or "ti" in value:
            value = value.replace(',', '.')
            amount = re.sub(r'[^\d.]', '', value)
            print("111")
            if amount.count('.') > 1:
                amount = amount.replace('.', '', amount.count('.') - 1)
            amount = float(amount) if amount else 0
            return f"{amount} tỷ đồng"

        if "triệu" in value or "tr" in value or "trđ" in value:
            value = re.sub(r'\.*', '', value).strip() 
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e3 if amount else 0
            return f"{amount} tỷ đồng"

        if "nghìn" in value:
            value = re.sub(r'\.*', '', value).strip() 
            value = value.replace('.', '')
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e6 if amount else 0
            return f"{amount} tỷ đồng"

        elif "đồng" in value or "đ" in value or "vnd" in value or "vnđ" in value:
            print(value)
            value = re.sub(r'\.*', '', value).strip() 
            value = value.replace('.', '')
            value = value.replace(',', '')
            amount = re.sub(r'[^\d]', '', value)
            amount = float(amount) / 1e9 if amount else 0
            return f"{amount} tỷ đồng"
        else:
            return ""

    converted_data = {key: convert(value) for key, value in data.items()}

    return converted_data