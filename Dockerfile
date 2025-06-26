FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

COPY ./dependencies /dependencies/
RUN conda install -c conda-forge --file requirements.txt || pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

