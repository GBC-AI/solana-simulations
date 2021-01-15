import os
import time
import yaml
from subprocess import Popen


def create_stack_file(logs_path, config_path):
    with open('docker-multinode/docker-stack.yml') as f:
        templates = yaml.safe_load(f)
        templates['services']['config_generator']['volumes'][0] = config_path + ':/solana/config'
        templates['services']['genesis_node']['volumes'][0] = logs_path + ':/mnt/logs'
        templates['services']['genesis_node']['volumes'][1] = config_path + ':/solana/config'
        templates['services']['validator']['volumes'][0] = logs_path + ':/mnt/logs'
        templates['services']['validator']['volumes'][1] = config_path + ':/solana/config'
        templates['services']['transaction']['volumes'][0] = logs_path + ':/mnt/logs'

        with open(logs_path + '/docker-stack.yml', 'w') as fo:
            yaml.dump(templates, fo, default_flow_style=False)


def run_cluster(path=''):
    process1 = Popen('docker stack deploy -c '+path+'docker-stack.yml solana_stack', shell=True)
    time.sleep(180)
    process2 = Popen('docker stack rm solana_stack', shell=True)
    time.sleep(30)

base_path = '/mnt/nfs_share/solana/ad160/'
#base_path = '/Users/korg/PycharmProjects/velas-ss/ad160/'
try:
    os.system('rm -rf ' + base_path)
    time.sleep(1)
    original_umask = os.umask(0)
    os.makedirs(base_path, mode=0o777)
    os.umask(original_umask)
except:
    pass

for i in [4, 5]:
    original_umask = os.umask(0)
    os.makedirs(base_path + str(i), mode=0o777)
    os.makedirs(base_path + str(i) + '/logs', mode=0o777)
    os.makedirs(base_path + str(i) + '/config', mode=0o777)
    os.umask(original_umask)
    create_stack_file(base_path + str(i) + '/logs', base_path + str(i) + '/config')
    time.sleep(2)
    run_cluster(base_path + str(i) + '/logs/')

