FROM ubuntu
RUN apt-get -y update && apt-get install && apt-get -y install curl
RUN apt-get install make
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup component add rustfmt && rustup update
RUN apt-get -y install libssl-dev libudev-dev
ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y pkg-config zlib1g-dev llvm clang

COPY ./solana ./solana
WORKDIR /solana
RUN cargo build
CMD /bin/bash


# TOML_CONFIG=$PWD/config.toml ./multinode-demo/setup.sh
# TOML_CONFIG=$PWD/config.toml ./multinode-demo/bootstrap-validator.sh
