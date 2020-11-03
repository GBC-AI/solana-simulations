To run Solana single-local-node:
1.  docker build -t solana142 .
# building will take >10 mins, (900 mb image )

2. docker container run -it solana142
# -it will open shell inside ubuntu container

# next run the local validator. You will see a lot of logs :) 
3. USE_INSTALL=1 ./multinode-demo/bootstrap-validator.sh

