FROM python:3.9.9-alpine3.14
COPY . ./lab-spo
WORKDIR /lab-spo
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]