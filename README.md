#Generating datapoints:

#### 1. To download/build solana (and other) images:  

    docker pull nikromanov/solana-velas:1.5.0  #(both Alpha and Beta servers)
    docker pull python:3.8-slim
    docker build -t "python_trans_conf:5" .
    docker build -t "sync_watch:latest" dockers/docker_sync_watcher/

#### 2. Run datapoint_generator

    su - developer #+password
    cd velas-ss #go to the root velas-ss
    python datapoint_generator.py --start X #name the folder 

#### 3. Result

will creating folder at

    /mnt/nfs_share/store2/solana/datapoints/X