FROM python:3.9.9-alpine3.14
COPY . ./lab-spo
WORKDIR /lab-spo
CMD ["python", "main.py"]