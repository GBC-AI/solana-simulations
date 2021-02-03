FROM python:3.7.7

WORKDIR /sync_watch

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
