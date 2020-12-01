FROM python:3.7

ENV PORT=8080
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD tools/transaction_sender.py .

CMD python transaction_sender.py --tps 500