# 900 MB image, solana142
# docker container run -it 20cd510d307b
# USE_INSTALL=1 ./multinode-demo/bootstrap-validator.sh [--gossip-host YOUR_IP]


FROM ubuntu
RUN apt-get -y update && apt-get install && apt-get -y install curl
RUN curl https://raw.githubusercontent.com/solana-labs/solana/master/install/solana-install-init.sh -o solana-install-init.sh
RUN sh ./solana-install-init.sh 1.4.2
RUN apt -y install git
RUN git clone https://github.com/solana-labs/solana.git
WORKDIR /solana
RUN git checkout a4ad292
RUN sh -c "$(curl -sSfL https://release.solana.com/v1.4.2/install)"
ENV PATH="/root/.local/share/solana/install/active_release/bin:$PATH"
RUN USE_INSTALL=1 ./multinode-demo/setup.sh

# USE_INSTALL=1 ./multinode-demo/setup.sh
# USE_INSTALL=1 ./multinode-demo/bootstrap-validator.sh --log ./logs/logs_genesis
# USE_INSTALL=1 ./multinode-demo/faucet.sh