import re
from src.dk116_cond import *
from src.dk118_cond import *
from src.convert_money import *
from src.dk114_cond import *
from src.dk34_cond import *
from src.kpt import *
from src.htk_dt_ln import *
from src.search import *
from src.semantic_cond import *
from src.log import *

def sort_conditions(text):
    # tách theo dòng
    lines = text.strip().split("\n")
    conditions = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "Chưa thỏa mãn điều kiện" in line:
            # Lấy số
            condition_number = int(re.search(r"điều kiện (\d+)", line).group(1))
            solution = []
            i += 1
            # Thu thập các dòng giải pháp ngay sau điều kiện
            while i < len(lines) and not re.search(r"Chưa thỏa mãn điều kiện \d+", lines[i]):
                solution.append(lines[i].strip())
                i += 1
            conditions.append((condition_number, line, "\n".join(solution)))
        else:
            i += 1
 
    conditions.sort(key=lambda x: x[0])
 
    sorted_text = "\n\n".join(f"{cond}\n{sol}" for _, cond, sol in conditions)
    return sorted_text

def clean_gp(text):
    if not isinstance(text, str):
        return text  # hoặc return '' nếu bạn muốn loại bỏ luôn những giá trị không phải chuỗi
    return re.sub(r"Chưa thỏa mãn điều kiện \d+\s*", "", text)


def apply_conditions(row):
    solutions = []
    for func in [DK113, DK116, DK115, DK117,DK118, DK123, DK124, DK125, DK122,DK126, DK114,DK120,DK121]:

        result = func(row)
        if result:
            solutions.append(result)
        import gc
        gc.collect()
    if solutions:
        text_gp = '\n \n'.join(solutions)
        sorted_text = sort_conditions(text_gp)
        row['GIAI_PHAP_TONG'] = sorted_text
    return row

# def process_row(row):
#     row = apply_conditions(row)
#     row['FLAG'] = 1
#     return row


def run(dt: pd.DataFrame) -> pd.DataFrame:
    try:
        columns_to_initialize = ['DK113', 'DK114', 'DK115', 'DK116', 'DK117', 'DK118', 'DK119', 
                                  'DK120','DK121', 'DK122', 'DK123', 'DK124', 'DK125', 'DK126', 'GIAI_PHAP']
        dt[columns_to_initialize] = 'Pass'
        dt['FLAG'] = 0
        dt = dt.apply(apply_conditions, axis=1)
#         dt = dt.progress_apply(check_conditions_flag3, axis=1)

        dt.columns = dt.columns.str.strip()
        column_mapping = {'Đại diện pháp luật trên ĐVKD:': 'Đại diện pháp luật trên ĐVKD:'}
        dt.rename(columns=column_mapping, inplace=True)
        columns_to_merge_114 = [
            'KHOẢN PHẢI THU', 'HÀNG TỒN KHO', 'DOANH THU', 'KINH NGHIỆM', 
            'LỢI NHUẬN', 'MẶT HÀNG KD', 'PT MUA BÁN', 'ĐỊA ĐIỂM', 'PT THANH TOÁN'
        ]
        dt['CT114'] = dt[columns_to_merge_114].apply(
            lambda row: ' | '.join([f"'{col}': {row[col]}" for col in columns_to_merge_114 if pd.notna(row[col])]), axis=1
        )
        columns_to_merge_113 = ['Thông tin cảnh báo rủi ro']
        dt['CT113'] = dt[columns_to_merge_113].apply(
            lambda row: ' | '.join([f"'{col}': {row[col]}" for col in columns_to_merge_113 if pd.notna(row[col])]), axis=1
        )
        columns_to_merge_115 = ['Tư vấn pháp lý đối với ngành nghê KD có điều kiện (Dẫn chiếu Quy định từng thời kỳ)*']
        dt['CT115'] = dt[columns_to_merge_115].apply(
            lambda row: ' | '.join([f"'{col}': {row[col]}" for col in columns_to_merge_115 if pd.notna(row[col])]), axis=1
        )
        columns_to_merge_116 = ['Giá trị hạn mức/Số tiền cho vay đề xuất', 'KHOẢN PHẢI THU']
        dt['CT116'] = dt[columns_to_merge_116].apply(
            lambda row: ' | '.join([f"'{col}': {row[col]}" for col in columns_to_merge_116 if pd.notna(row[col])]), axis=1
        )
        dt.loc[dt['DK117'] == 'False', 'CT117'] = 'Chênh lệch giá trị hàng tồn kho theo sổ sách và ảnh chụp'

        columns_to_merge_118 = ['Giá trị hạn mức/Số tiền cho vay đề xuất', 'KHOẢN PHẢI THU', 'HÀNG TỒN KHO']
        dt['CT118'] = dt[columns_to_merge_118].apply(
            lambda row: ' | '.join([f"'{col}': {row[col]}" for col in columns_to_merge_118 if pd.notna(row[col])]), axis=1
        )
        columns_to_merge_122 = ['Pháp lý:', 'Đại diện pháp luật trên ĐVKD']
        dt['CT122'] = dt[columns_to_merge_122].apply(
            lambda row: ' | '.join([f"'{col}': {row[col]}" for col in columns_to_merge_122 if pd.notna(row[col])]), axis=1
        )
        column_order = [
            'Mã phương án', 'CT113', 'DK113', 'CT114', 
            'DK114', 'CT115', 
            'DK115', 'CT116', 
            'DK116', 'CT117', 'DK117', 'CT118', 'DK118','DK119','CT120', 'DK120','CT121', 'DK121', 
            'CT122', 'DK122', 'DK123', 
            'DK124', 'DK125', 'DK126','GIAI_PHAP_TONG'
        ]
        column_order = [col for col in column_order if col in dt.columns]
        dt = dt[column_order]

        dt['GIAI_PHAP_CLEAN'] = dt['GIAI_PHAP_TONG'].apply(clean_gp)
        dt.drop(columns=['GIAI_PHAP_CLEAN'], inplace=True)
        dt.to_excel('result.xlsx', index=False)
        return dt
    except Exception as e:
        # Ghi log lỗi nếu có lỗi xảy ra
        logger.error("ERROR RUN SERVICE!", exc_info=e)
        return dt
