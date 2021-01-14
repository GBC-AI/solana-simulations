FROM python:3.7

ADD requirements.txt .
RUN pip install -r requirements.txt
COPY configs/ /velas-ss/

CMD /bin/bash -c "python velas-ss/transaction_sender.py --tps 100 --s 5"