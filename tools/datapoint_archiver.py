import tarfile
import argparse
from subprocess import Popen
import time
import datetime

base_path = '/mnt/nfs_share/store2/solana/datapoints2/'

parser = argparse.ArgumentParser(description='Run Solana-velas performance test')
parser.add_argument('--start', default=1, type=int, help='start')
parser.add_argument('--end', default=2, type=int, help='end')
args = parser.parse_args()

for i in range(args.start, args.end):
    stime = datetime.datetime.now()
    tar = tarfile.open(base_path + 'archives/' + str(i) + ".tar.gz", "w:gz", compresslevel=5)
    tar.add(base_path + str(i), arcname=str(i) + 'tar')
    tar.close()
    process2 = Popen('rm -rf '+base_path + str(i), shell=True)
    print(str(i), datetime.datetime.now() - stime)

