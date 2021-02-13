import os
import time
import yaml
import random
import tarfile
import argparse
from subprocess import Popen


def create_stack_file(logs_path, config_path, tps=2000, validators=4):
    with open('docker-multinode/docker-stack.yml') as f:
        templates = yaml.safe_load(f)
        templates['services']['config_generator']['volumes'][0] = config_path + ':/solana/config'
        templates['services']['genesis_node']['volumes'][0] = logs_path + ':/mnt/logs'
        templates['services']['genesis_node']['volumes'][1] = config_path + ':/solana/config'
        templates['services']['validator']['volumes'][0] = logs_path + ':/mnt/logs'
        templates['services']['validator']['volumes'][1] = config_path + ':/solana/config'
        templates['services']['transaction']['volumes'][0] = logs_path + ':/mnt/logs'
        templates['services']['sync_watcher']['volumes'][0] = logs_path + ':/sync_watch/output'

        templates['services']['validator']['deploy']['replicas'] = validators
        templates['services']['transaction']['command'] = 'bash -c "sleep 15 && python velas-ss/transaction_sender.py --tps '+\
                                                   str(tps)+' --s 20 --host http://genesis_node"'

        with open(logs_path + '/docker-stack.yml', 'w') as fo:
            yaml.dump(templates, fo, default_flow_style=False)


def gzip_datapoint(b_path, output_name):
    tar = tarfile.open(b_path + 'archives/' + output_name + ".tar.gz", "w:gz", compresslevel=5)
    tar.add(b_path + output_name, arcname=output_name + 'tar')
    tar.close()


def run_cluster(b_path, name):
    path = b_path + name + '/logs/'
    process1 = Popen('docker stack deploy -c '+path+'docker-stack.yml solana_stack', shell=True)
    time.sleep(300)
    extra_time = 0
    while extra_time < 14:
        time.sleep(60)
        if os.path.isfile(path+'simulation_result.json'):
            break
        else:
            extra_time += 1
    process2 = Popen('docker stack rm solana_stack', shell=True)
    time.sleep(30)
    #gzip_datapoint(b_path, name)


parser = argparse.ArgumentParser(description='Run Solana-velas performance test')
parser.add_argument('--start', default=1, type=int, help='first number of the experiment')
parser.add_argument('--n', default=1, type=int, help='number of the experiment s')
args = parser.parse_args()

base_path = '/mnt/nfs_share/store2/solana/datapoints/'
try:
    time.sleep(1)
    original_umask = os.umask(0)
    os.makedirs(base_path, mode=0o777)
    os.umask(original_umask)
except:
    pass

for i in range(args.start, args.start + args.n):
    original_umask = os.umask(0)
    os.makedirs(base_path + str(i), mode=0o777)
    os.makedirs(base_path + str(i) + '/logs', mode=0o777)
    os.makedirs(base_path + str(i) + '/config', mode=0o777)
    os.umask(original_umask)
    create_stack_file(base_path + str(i) + '/logs', base_path + str(i) + '/config',
                      tps=random.choice(range(100, 4000, 10)), validators=random.choice(range(3, 7)))
    time.sleep(2)
    run_cluster(base_path, str(i))
