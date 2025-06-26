from fastapi import FastAPI, File, UploadFile, Request
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse, JSONResponse
from src.dk116_cond import *
from src.dk118_cond import *
from src.convert_money import *
from src.dk114_cond import *
from src.dk34_cond import *
from src.kpt import *
from src.htk_dt_ln import *
from src.search import *
from src.semantic_cond import *
from src.helper import *
from src.log import *
app = FastAPI()

import openpyxl

# Function to apply conditions

@app.post("/process-excel/")
async def process_excel(request: Request,file: UploadFile = File(...)):
    try:
        contents = await file.read()
        dt = pd.read_excel(BytesIO(contents))
        total_input = len(dt)
        api_logger.info(f"Received request from {request.client.host}, HTTP 200")
        api_logger.info(f"Số bản ghi đầu vào: {total_input}")
        if dt.empty:
            return {"error": "Uploaded Excel file is empty."}
    
        processed_dt = run(dt)
        total_output = len(processed_dt)
        error_rows = total_input - total_output  

        api_logger.info(f"Số bản ghi sau khi xử lý: {total_output}")
        api_logger.info(f"Số bản ghi lỗi: {error_rows}")
        if processed_dt.empty:
            api_logger.warning("Processed DataFrame is empty.")
            return JSONResponse(status_code=400, content={"error": "Xử lý ra file trống"})
        # print(processed_dt.head())
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            processed_dt.to_excel(writer, index=False)
    
        output.seek(0)  
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                headers={"Content-Disposition": "attachment; filename=processed_file.xlsx"})
    except Exception as e:
        api_logger.error(f"HTTP 500 - Exception: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Error occur"})
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8080)