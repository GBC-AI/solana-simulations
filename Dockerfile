FROM python:3.7

ADD requirements.txt .
RUN pip install -r requirements.txt
COPY tools/transaction_sender.py /velas-ss/
COPY configs/ /velas-ss/
# CMD bin/bash
CMD /bin/bash -c "python velas-ss/config_generator.py &&\
                  mkdir -m 777 mnt/logs/exp1 && cp velas-ss/genenrated/config.toml mnt/logs/exp1/ &&\
                  sleep 30 &&\
                  python velas-ss/transaction_sender.py --tps 100 --s 5 --host http://genesis_node"