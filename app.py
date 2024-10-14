from fastapi import FastAPI, File, UploadFile
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
from dk28_cond import *
from dk30_cond import *
from convert_money import *
from dk20_cond import *
from dk34_cond import *
from kpt import *
from htk_dt_ln import *
from re_search_cond import *
from semantic_cond import *
app = FastAPI()
from log import *
 
#====DK 39 32 34 28 30 20 ====
def apply_conditions(row):
    try:
        solutions = []
        for func in [dk39, dk32, dk34, dk28, dk30, dk20]:
            result = func(row)
            if result:
                solutions.append(result)
        if solutions:
            text_gp = '\n \n'.join(solutions)
            sorted_text = sort_conditions(text_gp)
            row['GIAI_PHAP'] = sorted_text
        return row
    except Exception as e:
        logger.error("Apply condition failed!", exc_info=e)
 
def run(df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Khởi tạo các cột cần thiết
        columns_to_initialize = ['dk39', 'dk32', 'dk34', 'dk28', 'dk30', 'dk20', 'GIAI_PHAP']
        df[columns_to_initialize] = None
 
        # Áp dụng điều kiện lên từng hàng của DataFrame
        df = df.apply(apply_conditions, axis=1)
 
        # Lưu DataFrame sau khi xử lý vào file Excel
        df.to_excel('hello.xlsx', index=False)
 
        # Trả về DataFrame đã xử lý
        return df
    except Exception as e:
        # Ghi log lỗi nếu có lỗi xảy ra
        logger.error("ERROR RUN SERVICE!", exc_info=e)
        return df
 
 
 
@app.post("/process-excel/")
async def process_excel(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))
 
    if df.empty:
        return {"error": "Uploaded Excel file is empty."}
   
    processed_df = run(df)
 
    if processed_df.empty:
        return {"error": "Processed DataFrame is empty."}
   
    print(processed_df.head())
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        processed_df.to_excel(writer, index=False)
 
    output.seek(0)  
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=processed_file.xlsx"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8080)