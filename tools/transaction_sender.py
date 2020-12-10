import asyncio
import aiohttp
import datetime
import json
import requests
import argparse
import time
from typing import cast
from statistics import mean
import solana

from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.account import Account
from solana.rpc.api import Client
from solana.blockhash import Blockhash

from solana.rpc.types import RPCMethod, RPCResponse
from base64 import b64encode

# Nonce-info передавать разный
# у каждого блока найти таймстэмп
# посчитать среднее время транзакции


async def post_transaction(session, url, params, request_id):
    headers = {"Content-Type": "application/json"}
    method = RPCMethod("sendTransaction")
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method,
                       "params": [params, {"skipPreflight": True,
                                           "preflightCommitment": "max", "encoding": "base64"}]})
    async with session.post(url, headers=headers, data=data) as response:
        response_text = await response.text()
        validating_dict[json.loads(response_text)["result"]] = None  # adding transaction to validating_set


async def post_transaction_checker(session, url, tx_sig, request_id):
    headers = {"Content-Type": "application/json"}
    method = RPCMethod("getConfirmedTransaction")
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method,
                       "params": [tx_sig, "json"]})
    async with session.post(url, headers=headers, data=data) as response:
        response_text = await response.text()
        if json.loads(response_text)["result"] is None:
            validating_dict[tx_sig] = None
        else:
            validating_dict[tx_sig] = json.loads(response_text)["result"]['slot']


async def batch_checker(validating_list):
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        request_id = 3  # comment this
        for txn in validating_list:
            request_id += 1
            post_tasks.append(post_transaction_checker(session, host, txn, request_id))
        await asyncio.gather(*post_tasks)


async def batch_sender(tx_list):
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        request_id = 3  # comment this
        for txn in tx_list:
            request_id += 1
            if isinstance(txn, bytes):
                txn = b64encode(txn).decode("utf-8")
            post_tasks.append(post_transaction(session, host, txn, request_id))
        await asyncio.gather(*post_tasks)


def airdrop_request(url, pubkey, value):
    request_id = 1
    method = RPCMethod("requestAirdrop")
    headers = {"Content-Type": "application/json"}
    params = [str(pubkey), value, {"commitment": "max"}]
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
    print(data, requests.post(url, headers=headers, data=data))


def get_recent_blockhash(url):
    request_id = 2
    method = RPCMethod("getRecentBlockhash")
    headers = {"Content-Type": "application/json"}
    params = [{"commitment": "max"}]
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
    print(datetime.datetime.now() - start, "start creating transactions")
    batch_transactions = []
    for i in range(n):
        tx = Transaction().add(transfer(TransferParams(from_pubkey=sender.public_key(),
                                                       to_pubkey=recipient.public_key(), lamports=lamports + i)))
        tx.recent_blockhash = blockhash
        tx.sign(sender)
        batch_transactions.append(tx.serialize())
    return batch_transactions, blockhash_response['result']['context']['slot']


def check_transactions(batch_slot):
    incorrect_transaction_cnt = 0
    latency = []
    time.sleep(20)
    print(hc.get_balance(recipient.public_key()))

    asyncio.run(batch_checker(validating_dict.keys()))

    for transaction in validating_dict.keys():
        if validating_dict[transaction] is None:
            incorrect_transaction_cnt += 1
        else:
            latency.append(validating_dict[transaction] - batch_slot)
    print("Transactions:", len(latency),
          "Not passed transactions:", incorrect_transaction_cnt)
    if len(latency):
        print('Mean latency:', mean(latency), 'slots')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Velas performance test')
    parser.add_argument('--tps', default=10, type=int, help='tps (batch transactions)')
    parser.add_argument('--host', type=str, default="http://devnet.solana.com", help='host')
    parser.add_argument('--lamports', default=1234567890, type=int, help='airdrop value')
    parser.add_argument('--mode', default='one', help='mode of sender: one - just one batch of tps txs, multi - still DEV')
    args = parser.parse_args()

    host = args.host + ":8899"
    start = datetime.datetime.now()
    print("START : ", start)
    hc = Client(host)
    sender, recipient = Account(6), Account(7)
    airdrop_request(host, sender.public_key(), args.lamports)
    time.sleep(5)
    print(hc.get_balance(sender.public_key()))
    print(hc.get_balance(recipient.public_key()))
    validating_dict = {}

    if args.mode == 'multi':
        for transactions_per_batch in [10, 100, 1000]:
            for second in range(5):
                time.sleep(1)
                tx_list, slot = create_batch_transactions(transactions_per_batch, sender, recipient) # add slot to valid dict
                asyncio.run(batch_sender(tx_list))
                print(datetime.datetime.now() - start, "batch is sent : ", transactions_per_batch)

    elif args.mode == 'one':
        tx_list, slot = create_batch_transactions(args.tps, sender, recipient)
        print(datetime.datetime.now() - start, "start sending transactions")
        asyncio.run(batch_sender(tx_list))
        print(datetime.datetime.now() - start, "batch is sent")

    check_transactions(slot)
    print("END : ", datetime.datetime.now())



# python tools/transaction_sender.py --tps 100 --mode one"