import asyncio
import aiohttp
import datetime
import json
import requests
import argparse
import time
from typing import cast
from statistics import mean
import logging
import subprocess

from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.account import Account
from solana.rpc.api import Client
from solana.blockhash import Blockhash

from solana.rpc.types import RPCMethod, RPCResponse
from base64 import b64encode


async def post_transaction(session, url, params, request_id, current_slot):
    headers = {"Content-Type": "application/json"}
    method = RPCMethod("sendTransaction")
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method,
                       "params": [params, {"skipPreflight": True,
                                           "preflightCommitment": "max", "encoding": "base64"}]})
    async with session.post(url, headers=headers, data=data) as response:
        response_text = await response.text()
        # adding transaction to validating_set
        validating_list[json.loads(response_text)["result"]] = {'sent_slot': current_slot,
                                                                'commitment_slot': None}


async def post_transaction_checker(session, url, tx_sign, request_id):
    # TODO: multi check with list
    headers = {"Content-Type": "application/json"}
    method = RPCMethod("getSignatureStatuses")
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": [tx_sign]})

    async with session.post(url, headers=headers, data=data) as response:
        response_text = await response.text()
        for tx, r in zip(tx_sign, json.loads(response_text)["result"]['value']):
            if r is None:
                validating_list[tx]['commitment_slot'] = None
            else:
                validating_list[tx]['commitment_slot'] = r['slot']


async def experiment_checker():
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        request_id = 3
        transaction_list = [*validating_list]
        it = len(transaction_list) // 256
        rem = len(transaction_list) % 256
        limits = [256 * i for i in range(1, it + 1)] + [it * 256 + rem]
        lower_limit = 0
        for lim in limits:
            request_id += 1
            post_tasks.append(post_transaction_checker(session, host, transaction_list[lower_limit:lim], request_id))
            lower_limit = lim
        await asyncio.gather(*post_tasks)


async def batch_sender(batch, current_slot):
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        request_id = 3  # each request must be with unique request_id
        for txn in batch:
            request_id += 1
            if isinstance(txn, bytes):
                txn = b64encode(txn).decode("utf-8")
            post_tasks.append(post_transaction(session, host, txn, request_id, current_slot))
        await asyncio.gather(*post_tasks)


def airdrop_request(url, pubkey, value):
    request_id = 1
    method = RPCMethod("requestAirdrop")
    headers = {"Content-Type": "application/json"}
    params = [str(pubkey), value, {"commitment": "max"}]
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
    logging.info(str(data) + str(requests.post(url, headers=headers, data=data)))


def get_recent_blockhash(url):
    request_id = 2
    method = RPCMethod("getRecentBlockhash")
    headers = {"Content-Type": "application/json"}
    params = [{"commitment": "single"}]
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
    try:
        raw_response = requests.post(url, headers=headers, data=data)
        return cast(RPCResponse, json.loads(raw_response.text))
    except:
        print("cannot get blockhash :", data)
        return None


def create_batch_transactions(n=10, sender=Account(4), recipient=Account(5), lamports=10000):
    blockhash_response = get_recent_blockhash(host)
    blockhash = Blockhash(blockhash_response["result"]["value"]["blockhash"])
    logging.info("start creating batch")
    batch_transactions = []
    for i in range(n):
        tx = Transaction().add(transfer(TransferParams(from_pubkey=sender.public_key(),
                                                       to_pubkey=recipient.public_key(), lamports=lamports + i)))
        tx.recent_blockhash = blockhash
        tx.sign(sender)
        batch_transactions.append(tx.serialize())
    return batch_transactions, blockhash_response['result']['context']['slot']


def check_transactions(output_path):
    incorrect_transaction_cnt = 0
    latency = []
    time.sleep(120)
    logging.info("balance recipient:" + str(hc.get_balance(recipient.public_key())['result']))

    asyncio.run(experiment_checker())

    for transaction in validating_list.keys():
        if validating_list[transaction]['commitment_slot'] is None:
            incorrect_transaction_cnt += 1
        else:
            latency.append(validating_list[transaction]['commitment_slot'] - validating_list[transaction]['sent_slot'])
    logging.info("Success:" + str(len(latency)) + " Error:" + str(incorrect_transaction_cnt))
    if len(latency):
        logging.info('Mean latency:' + str(mean(latency)))

    with open(output_path, "a") as output_file:
        simulation_result = {'start_time': start,
                             'host': host,
                             'tps': args.tps,
                             'batches_seconds': args.s,
                             'success_txn': len(latency),
                             'failed_txn': incorrect_transaction_cnt,
                             'recipient_balance': hc.get_balance(recipient.public_key())['result'],
                             'start_sending_transactions': start_sending_transactions,
                             'end_sending_transactions': end_sending_transactions}
        if len(latency):
            simulation_result['mean_latency'] = mean(latency)
        else:
            simulation_result['mean_latency'] = None
        json.dump(simulation_result, output_file, default=str)


def multi_stacking(host_connection, path):
    time.sleep(120)
    i = 0
    while i < 6:
        i += 1
        time.sleep(30)
        nodes = host_connection.get_vote_accounts()
        vote_accounts_address = [x['votePubkey'] for x in nodes['result']['current']]
        delinquent_address = [x['votePubkey'] for x in nodes['result']['delinquent']]
        logging.info(str(vote_accounts_address) + str(delinquent_address))
        if len(vote_accounts_address) > 2:
            logging.info("get_vote_accounts() : " + str(nodes))
            break
    try:
        subprocess.check_output('solana config set --url ' + host, shell=True)
        logging.info(subprocess.check_output('solana validators', shell=True))
        subprocess.check_output('solana-keygen new  --no-passphrase --force', shell=True)
        logging.info(subprocess.check_output('solana airdrop 10', shell=True))
        time.sleep(15)
        for v in vote_accounts_address:
            subprocess.check_output('solana-keygen new -o ' + path + v + '.json --no-passphrase --force', shell=True)
            time.sleep(1)
            subprocess.check_output('solana create-stake-account ' + path + v + '.json 1', shell=True)
            time.sleep(1)
            logging.info(subprocess.check_output('solana delegate-stake ' + path + v + '.json ' + v, shell=True))

        i = 0
        while i < 10:
            i += 1
            time.sleep(60)
            nodes = host_connection.get_vote_accounts()
            vote_accounts_address = [x['votePubkey'] for x in nodes['result']['current']]
            delinquent_address = [x['votePubkey'] for x in nodes['result']['delinquent']]
            share_active = [0, 0]
            for v in nodes['result']['current']:
                if v['epochVoteAccount'] and v['activatedStake'] > 0:
                    share_active[0] += 1
                else:
                    share_active[1] += 1
            logging.info(str(share_active))
            if sum(share_active) > 2 and share_active[1] + 1 < share_active[0]:
                break
        logging.info(subprocess.check_output('solana validators', shell=True))
        logging.info(str(host_connection.get_vote_accounts()))
    except Exception as e:
        logging.info("not stacked! : " + str(e.__class__))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Solana-velas performance test')
    parser.add_argument('--tps', default=100, type=int, help='tps (batch transactions)')
    parser.add_argument('--host', type=str, default="http://devnet.solana.com", help='host')
    parser.add_argument('--s', default=20, type=int, help='duration of experiment in seconds')
    parser.add_argument('--output', default='/mnt/logs/', type=str, help='output folder path')
    args = parser.parse_args()
    logging.basicConfig(filename=args.output + 'sender_tr.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    host = args.host + ":8899"
    start = datetime.datetime.now()
    logging.info("------------START--------------")
    time.sleep(10)
    hc = Client(host)
    sender, recipient = Account(4), Account(5)
    airdrop_request(host, sender.public_key(), (15000+args.tps)*args.tps*args.s)
    time.sleep(2)
    logging.info("TPS: "+str(args.tps))
    logging.info("balance sender:" + str(hc.get_balance(sender.public_key())['result']))
    logging.info("balance recipient:" + str(hc.get_balance(recipient.public_key())['result']))

    multi_stacking(hc, args.output)

    validating_list = {}
    start_sending_transactions = datetime.datetime.now()
    for second in range(args.s):
        tx_list, slot = create_batch_transactions(args.tps, sender, recipient) # add slot to valid dict
        logging.debug((datetime.datetime.now() - start, "start sending batch of {} part {}".format(args.tps, second+1)))
        asyncio.run(batch_sender(tx_list, slot))
        logging.debug("batch is sent")
        time.sleep(0.5)
    end_sending_transactions = datetime.datetime.now()
    logging.info("experiment is sent")

    check_transactions(args.output + 'simulation_result.json')
    logging.info("---END---")

# python tools/transaction_sender.py --tps 100 --s 5 --output 'my_vol/' "
