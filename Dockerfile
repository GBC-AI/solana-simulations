FROM python:3.7

ADD requirements.txt .
RUN pip install -r requirements.txt
COPY configs/ /velas-ss/

#ARG USER=developer
#ARG GROUP=developers
#ARG UID=10000
#ARG GID=2001

#RUN groupadd -g $GID $GROUP && \
#    useradd -p '*' -m -u $UID -g $GROUP -s /bin/bash $USER && \
#    apt-get update

RUN sh -c "$(curl -sSfL https://release.solana.com/v1.5.5/install)"
ENV PATH="/root/.local/share/solana/install/active_release/bin:$PATH"

CMD /bin/bash -c "python velas-ss/transaction_sender.py --tps 100 --s 5"