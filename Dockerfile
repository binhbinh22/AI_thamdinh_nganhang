# Sử dụng Miniconda làm base image để cài đặt các gói khoa học dữ liệu nhanh hơn
FROM continuumio/miniconda3:latest

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirement.txt vào container
COPY requirements.txt .

# Cài đặt các gói từ requirement.txt bằng conda nếu có, nếu không thì dùng pip
RUN conda install -c conda-forge --file requirements.txt || pip install -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Mở cổng 8080 để truy cập API
EXPOSE 8080

# Lệnh để chạy ứng dụng FastAPI với uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

