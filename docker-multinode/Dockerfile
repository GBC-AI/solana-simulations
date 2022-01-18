ARG USER=developer
ARG GROUP=developers
ARG UID=10000
ARG GID=2001

FROM rust:1.48 AS solana-build
COPY solana /solana
RUN apt-get update && \
    apt-get install -y --no-install-recommends libssl-dev libudev-dev pkg-config zlib1g-dev llvm clang && \
    rm -rf /var/lib/apt/lists/*
ENV RUSTFLAGS="-C target-feature=+avx,+avx2 ${RUSTFLAGS}" \
    TOML_CONFIG=/solana/config.toml \
    PATH="/solana/target/release:${PATH}" \
    NDEBUG=1
WORKDIR /solana
RUN rustup --version; \
    cargo --version; \
    rustc --version; \
    cargo build --release --all
RUN ./multinode-demo/setup.sh
# IMPORTANT! To run inside docker swarm you shouldn't check ports because it leads to fail.
# The next row will set --no-port-check flag when solana-validator will be called
RUN sed -i '/^default_arg\ \-\-require\-tower=*/adefault_arg --no-port-check' multinode-demo/validator.sh && \
    cp -R config ./config_default && \
    rm -rf target/release/deps

FROM ubuntu:18.04
ARG USER
ARG GROUP
ARG UID
ARG GID
ENV PATH="/solana/target/release/:${PATH}" \
    TOML_CONFIG=/solana/config.toml \
    USE_INSTALL=1
RUN groupadd -g $GID $GROUP && \
    useradd -p '*' -m -u $UID -g $GROUP -s /bin/bash $USER && \
    apt-get update && \
    apt-get install -y --no-install-recommends libssl-dev sudo && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    rm -rf /var/lib/apt/lists/*
COPY --from=solana-build --chown=${UID}:${GID} /solana /solana
USER developer
WORKDIR /solana
