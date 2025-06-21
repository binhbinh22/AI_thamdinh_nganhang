import pandas as pd
import re

def DK113(row):
    ttcbrr = str(row['Thông tin cảnh báo rủi ro'])
    if not re.search(r'Không có thông tin cảnh báo', ttcbrr, re.IGNORECASE):
        row['DK113'] = False
        return '''-Chưa thỏa mãn điều kiện 113 Thực hiện giải trình làm rõ, cung cấp hồ sơ đã khắc phục nội dung cảnh báo'''
    row['DK113'] = 'Pass'
    return None

def DK115(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])
    tvpl = str(row['Tư vấn pháp lý đối với ngành nghê KD có điều kiện (Dẫn chiếu Quy định từng thời kỳ)*'])
    # print(tvpl +"10000000000000000")
    if  not re.search(r'kinh doanh có điều kiện', ptk1, re.IGNORECASE) and not re.search(r'kinh doanh có điều kiện', ptk2, re.IGNORECASE) and pd.notna(tvpl):
        row['DK115'] = 'FAIL'
        return '''-Chưa thỏa mãn điều kiện 115 Đánh giá về pháp lý hoạt động kinh doanh của Khách hàng, cung cấp hồ sơ pháp lý ngành có điều kiện theo quy định pháp luật'''
    row['DK115'] = 'PASS'
    


def DK117(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])

    if re.search(r'Chênh lệch giá trị hàng tồn kho theo sổ sách và ảnh chụp', ptk1, re.IGNORECASE) or re.search(r'Chênh lệch giá trị hàng tồn kho theo sổ sách và ảnh chụp', ptk2, re.IGNORECASE):
        row['DK117'] = False
        return '''-Chưa thỏa mãn điều kiện 117 Chênh lệch giá trị hàng tồn kho theo sổ sách và ảnh chụp: ĐVKD đánh giá đặc thù Hoạt động kinh doanh của khách hàng
        /cung cấp thêm chứng từ (phiếu xuất nhập kho/ảnh chụp/trích xuất camera...)'''
    row['DK117'] = 'Pass'
    return None

def DK119(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])

    if not re.search(r'khả năng thu hồi Khoản phải thu', ptk1, re.IGNORECASE) or not re.search(r'khả năng thu hồi Khoản phải thu', ptk2, re.IGNORECASE):
        row['DK119'] = False
        return '''-Chưa thỏa mãn điều kiện 119 ĐVKD đánh giá bổ sung khả năng thu hồi Khoản phải thu: ĐVKD thu thập sổ sách bán hàng/theo dõi Khoản phải thu để đánh giá tốc độ thu hồi Khoản phải thu của KH'''
    row['DK119'] = 'Pass'
    return None


def DK123(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])

    if re.search(r'Sổ sách', ptk1, re.IGNORECASE) or re.search(r'Bảng kê', ptk1, re.IGNORECASE) or re.search(r'Sổ sách', ptk2, re.IGNORECASE) or re.search(r'Bảng kê', ptk2, re.IGNORECASE):
        row['DK123'] = False
        return '''-Chưa thỏa mãn điều kiện 123 Những lưu ý khi cung cấp sổ sách/bảng kê:
1. Cung cấp sổ sách/bảng kê tối thiểu 10 ngày liên tiếp/3 tháng gần nhất và thể hiện đơn giá, số lượng, thành tiền đảm bảo:
- Số lượng hàng bán: phù hợp với quy mô/mặt hàng, tính mùa vụ của sản phẩm.
- Đơn giá bán: phù hợp mặt hàng, giá cả thị trường
2. Khách hàng tái cấp: Nếu bảng giá/số lượng các mặt hàng bán ra không thay đổi so với thời điểm hạn mức cũ (12 tháng) 
=> Cung cấp sổ sách/bảng kê phù hợp với thực tế kinh doanh hiện tại của Khách hàng.
3. Khách hàng không buôn bán vào ngày nghỉ lễ tết nhưng sổ sách bảng kê thể hiện bán vào cả ngày nghỉ lễ tết => Giải trình phù hợp tại mục phân tích khác. 
4. Sổ sách bảng kê không được có cả các ngày không có thật (VD ngày 30/2; 31/06).'''
    row['DK123'] = 'Pass'
    return None
# Các hàm cập nhật GIAI_PHAP dựa trên điều kiện

def DK124(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])
    if re.search(r'Sao kê', ptk1, re.IGNORECASE) or re.search(r'Sao kê', ptk2, re.IGNORECASE) or re.search(r'giao dịch tài khoản', ptk2, re.IGNORECASE)  or re.search(r'tài khoản giao dịch', ptk2, re.IGNORECASE):
        row['DK124'] = False
        return '''-Chưa thỏa mãn điều kiện 124 Những lưu ý khi phân tích sao kê tài khoản:
1. Trường hợp Sao kê không thể hiện rõ bút toán thanh toán tiền hàng: Tính doanh thu dựa trên các bút toán thanh toán tiền hàng
/các giao dịch chuyển khoản loại trừ chuyển tiền lòng vòng, các giao dịch nộp tiền Tính doanh thu của KH căn cứ trên tỷ lệ bán hàng đầu ra CK/TM.
2. Trường hợp Sao kê tài khoản của bên thứ 3 (không phải vợ chồng khách hàng): Đánh giá mối quan hệ giữa khách hàng và Bên thứ 3. 
Làm rõ nguyên nhân chuyển khoản vào tài khoản bên thứ 3. Cách thức hoạt động và biện pháp quản lý.
3. Trường hợp Sao kê có các bút toán Cho vay, trả lãi của các cá nhân: Làm rõ khách hàng có thuộc đối tượng cho vay nặng lãi không, 
tra cứu thông tin bên thứ 3 (chuyển khoản cho khách hàng): khoản vay tại MB (nếu có)...)'''
    row['DK124'] = 'Pass'
    return None


def DK125(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])

    if re.search(r'Lợi nhuận', ptk1, re.IGNORECASE) or re.search(r'Lợi nhuận', ptk2, re.IGNORECASE) or re.search(r'\bLN\b',ptk1) or re.search(r'\bLN\b',ptk2) or re.search(r'\bLNBQ\b',ptk1) or re.search(r'\bLNBQ\b',ptk2):
        row['DK125'] = False
        return '''-Chưa thỏa mãn điều kiện 125 Lưu ý ghi nhận Lợi nhuận sau thuế = Doanh thu * TSLN (theo TSLN ngành) * 0.98 (thuế ghi nhận 2%))'''
    row['DK125'] = 'Pass'
    return None

def DK126(row):
    ptk1 = str(row['PTK1'])
    ptk2 = str(row['PTK2'])

    if re.search(r'Hình ảnh', ptk1, re.IGNORECASE) or re.search(r'Ảnh chụp', ptk1, re.IGNORECASE) or re.search(r'Hình ảnh', ptk2, re.IGNORECASE) or re.search(r'Ảnh chụp', ptk2, re.IGNORECASE) or re.search(r'Biển hiệu', ptk2, re.IGNORECASE) or re.search(r'Biển hiệu', ptk1, re.IGNORECASE):
        row['DK126'] = False
        return '''-Chưa thỏa mãn điều kiện 126 Hình ảnh cơ sở kinh doanh phải thể hiện được tổng quát cơ sở kinh doanh, quy mô kinh doanh. Đảm bảo:
- Thể hiện bên trong, ngoài và tổng thể địa điểm, vị trí, thể hiện rõ địa chỉ  kinh doanh và quy mô kinh danh của KH và các căn liền kề (nếu có). 
- Ảnh chụp qua app timestamp/MB capture có thông tin: thời gian chụp ảnh + bản đồ, toạ độ, địa chỉ của vị trí chụp ảnh
- Trường hợp không có biển hiệu kinh doanh: Làm rõ  nguyên nhân không biển hiệu tại mục Phân tích khác
- Trường hợp biển hiệu có thông tin tên/SĐT không phải của khách hàng: Đàm phán khách hàng bổ sung thông tin liên hệ trên biển hiệu hoặc Giải trình rõ nguyên nhân)'''
    row['DK126'] = 'Pass'
    return None