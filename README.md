#### How to run Solana single-local-node

1). Building takes  more than 10 mins, (900 mb image).
```bash
$ docker build -t solana142 .
```

2). "-it" will open shell inside ubuntu container

```bash
$ docker container run -it solana142
```

3). Run a validator in VM shell. You will see a lot of logs:)  
```bash
$ USE_INSTALL=1 ./multinode-demo/bootstrap-validator.sh
```

### /docker-two 
docker-compose for running 2 nodes in compose-network. Use SHELL from 3rd container for using solana CLI and creating transactions.

### /docker-solana-config
dockerfile for building image from sources. 
```
# to start node: 

TOML_CONFIG=$PWD/config.toml ./multinode-demo/setup.sh
TOML_CONFIG=$PWD/config.toml ./multinode-demo/bootstrap-validator.sh
```
