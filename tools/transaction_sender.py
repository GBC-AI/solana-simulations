import asyncio
import aiohttp
import datetime
import json
import requests
import argparse
import time
from typing import cast
import solana

from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.account import Account
from solana.rpc.api import Client
from solana.blockhash import Blockhash

from solana.rpc.types import RPCMethod, RPCResponse
from base64 import b64encode

# Nonce-info передавать разный
# каждую транзакцию опросить receipt
# у каждого блока найти таймстэмп
# посчитать среднее время транзакции


async def do_post(session, url, params, request_id):
    headers = {"Content-Type": "application/json"}
    method = RPCMethod("sendTransaction")
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method,
                       "params": [params, {"skipPreflight": True,
                                           "preflightCommitment": "max", "encoding": "base64"}]})
    async with session.post(url, headers=headers, data=data) as response:
        response = await response.text()
        validating_dict[json.loads(response)["result"]] = None



async def batch_sender(tx_list):
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        request_id = 3  # comment this
        for txn in tx_list:
            request_id += 1
            if isinstance(txn, bytes):
                txn = b64encode(txn).decode("utf-8")
            post_tasks.append(do_post(session, host, txn, request_id))
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
    except:
        print("cannot get blockhash :", data)
    return cast(RPCResponse, json.loads(raw_response.text))


def create_batch_transactions(n=10, sender=Account(4), recipient=Account(5), lamports=10000):

    blockhash = Blockhash(get_recent_blockhash(host)["result"]["value"]["blockhash"])
    print(datetime.datetime.now() - start, "start creating transactions")
    batch_transactions = []
    for i in range(n):
        tx = Transaction().add(transfer(TransferParams(from_pubkey=sender.public_key(),
                                                       to_pubkey=recipient.public_key(), lamports=lamports + i)))
        tx.recent_blockhash = blockhash
        tx.sign(sender)
        batch_transactions.append(tx.serialize())
    return batch_transactions


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Velas performance test')
    parser.add_argument('--tps', default=10, type=int, help='tps (batch transactions)')
    parser.add_argument('--host', type=str, default="http://devnet.solana.com", help='host')
    parser.add_argument('--lamports', default=1234567890, type=int, help='airdrop value')
    parser.add_argument('--mode', default='one', help='mode of sender: one - just one batch of tps txs, multi')
    args = parser.parse_args()

    host = args.host + ":8899"
    start = datetime.datetime.now()
    print(start)
    hc = Client(host)
    sender, recipient = Account(6), Account(7)
    airdrop_request(host, sender.public_key(), args.lamports)
    time.sleep(5)
    print(hc.get_balance(sender.public_key()))
    print(hc.get_balance(recipient.public_key()))
    validating_dict = {}

    if args.mode == 'multi':
        for k in [10, 100, 1000]:
            for second in range(5):
                time.sleep(1)
                tx_list = create_batch_transactions(args.tps, sender, recipient)
                asyncio.run(batch_sender(tx_list))
                print(datetime.datetime.now() - start, "batch is sent : ", k)

    elif args.mode == 'one':
        tx_list = create_batch_transactions(args.tps, sender, recipient)
        print(datetime.datetime.now() - start, "start sending transactions")
        asyncio.run(batch_sender(tx_list))
        print(datetime.datetime.now() - start, "batch is sent")

    time.sleep(15)

    incorrect_transaction_cnt = 0
    print(hc.get_balance(recipient.public_key()))
    for transaction in validating_dict.keys():
        transaction_status = hc.get_confirmed_transaction(transaction)
        if transaction_status['result'] is None:
            incorrect_transaction_cnt += 1
        else:
            validating_dict[transaction] = transaction_status['result']['slot']
    print("Не прошло транзакций", incorrect_transaction_cnt)



# python tools/transaction_sender.py --tps 15 --mode multi"