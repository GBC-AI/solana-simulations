from utils import *
from time import localtime, strftime, sleep
from argparse import ArgumentParser
import os


if __name__ == '__main__':
    """ 
    This script will produce a file containing information about each node in a cluster 
    (its ip, processing slot and slot of the last confirmed block) and SKIP_RATIO value each 10 seconds. 
    """
    parser = ArgumentParser()
    parser.add_argument("-o", "--output", help="path to the result file", type=str, default="output/sync_result.txt")
    parser.add_argument("-u", "--url", help="Cluster URL", type=str, default="https://devnet.solana.com")
    args = parser.parse_args()
    sleep(10)
    if not os.path.isdir(args.output.split('/')[0]):
        os.mkdir(args.output.split('/')[0])
    while True:
        d = {}
        ips = get_cluster_info(args.url, 4)
        nodes_ips = ['http://' + i for i in ips if i is not None]
        requests_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

        nodes_slot_data = asyncio.run(batch_info(nodes_ips))
        clean_slot_data = [dat for dat in nodes_slot_data if (isinstance(dat, dict) and
                                                              isinstance(dat['slot'], int) and
                                                              isinstance(dat['last_block'], int))]
        d[requests_time] = {'sync_data': clean_slot_data, 'skip_rate': count_skip_rate(args.url, 100),
                            'total_nodes': len(ips), 'rpc_ips': ips}
        with open(args.output, 'a') as outfile:
            json.dump(d, outfile)
            outfile.write('\n')
        sleep(15)

