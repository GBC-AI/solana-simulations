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


## Docker-compose
in ```docker-two/``` docker-compose for two nodes. Current state: cannot connect second node to main node.  