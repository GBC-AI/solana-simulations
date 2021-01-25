import os
import time
import yaml
import random
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

        templates['services']['validator']['deploy']['replicas'] = validators

        templates['services']['transaction']['command'] = 'bash -c "sleep 25 && python velas-ss/transaction_sender.py --tps '+\
                                                   str(tps)+' --s 20 --host http://genesis_node"'

        with open(logs_path + '/docker-stack.yml', 'w') as fo:
            yaml.dump(templates, fo, default_flow_style=False)


def run_cluster(path=''):
    process1 = Popen('docker stack deploy -c '+path+'docker-stack.yml solana_stack', shell=True)
    time.sleep(540)
    process2 = Popen('docker stack rm solana_stack', shell=True)
    time.sleep(30)

base_path = '/mnt/nfs_share/solana/ad160/'
#base_path = '/Users/korg/PycharmProjects/velas-ss/ad160/'
try:
    time.sleep(1)
    original_umask = os.umask(0)
    os.makedirs(base_path, mode=0o777)
    os.umask(original_umask)
except:
    pass

for i in range(32, 132):
    original_umask = os.umask(0)
    os.makedirs(base_path + str(i), mode=0o777)
    os.makedirs(base_path + str(i) + '/logs', mode=0o777)
    os.makedirs(base_path + str(i) + '/config', mode=0o777)
    os.umask(original_umask)
    create_stack_file(base_path + str(i) + '/logs', base_path + str(i) + '/config',
                      tps=random.choice(range(1500, 8000, 500)), validators=random.choice(range(3, 7)))
    time.sleep(2)
    run_cluster(base_path + str(i) + '/logs/')

