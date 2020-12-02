#### How to run Solana on Docker Swarm (on a few machines)

Build image with Solana binaries
```bash
docker build -t nikromanov/solana-velas:1.5.0 .
```

Deploy stack on Docker Swarm  
```bash
docker stack deploy -c docker-stack.yml solana_stack
```

Delete existing stack
```bash
docker stack rm solana_stack
```

#### How to run Solana on Docker Compose (on one machine)

Also build image as in previous example

Deploy on Docker Compose  
```bash
docker-compose up -d
```

Delete existing containers, networks and etc.
```bash
docker-compose down -t 1
```

#### Tips

You can install useful debug tools inside container
```bash
sudo apt-get update && sudo apt-get install nmap screen -y
```
