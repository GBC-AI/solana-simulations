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
                       "params": [params, {"skipPreflight": False,
                                           "preflightCommitment": "max", "encoding": "base64"}]})
    async with session.post(url, headers=headers, data=data) as response:
        await response.text()


async def batch_sender(tx_list):
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        r_id = 3
        for txn in tx_list:
            r_id += 1
            if isinstance(txn, bytes):
                txn = b64encode(txn).decode("utf-8")
            post_tasks.append(do_post(session, host, txn, r_id))
        await asyncio.gather(*post_tasks)


def airdrop_request(url, pubkey, value):
    request_id = 1
    method = RPCMethod("requestAirdrop")
    headers = {"Content-Type": "application/json"}
    params = [str(pubkey), value, {"commitment": "max"}]
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
    print(url, headers, data)
    raw_response = requests.post(url, headers=headers, data=data)
    print(raw_response)


def get_recent_blockhash(url):
    request_id = 2
    method = RPCMethod("getRecentBlockhash")
    headers = {"Content-Type": "application/json"}
    params = [{"commitment": "max"}]
    data = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
    print(url, headers, data)
    raw_response = requests.post(url, headers=headers, data=data)
    print(json.loads(raw_response.text))
    return cast(RPCResponse, json.loads(raw_response.text))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Velas performance test')
    parser.add_argument('--tps', default=10, type=int, help='tps (banch trxs)')
    parser.add_argument('--host', type=str, default="http://devnet.solana.com", help='host')
    parser.add_argument('--lampos', default=100000001, type=int, help='airdrop value')
    args = parser.parse_args()

    host = args.host + ":8899"
    start = datetime.datetime.now()
    print(start)
    sender, recipient = Account(147), Account(148)
    airdrop_request(host, sender.public_key(), args.lampos)
    time.sleep(5)
    recent_blockhash = Blockhash(get_recent_blockhash(host)["result"]["value"]["blockhash"])
    print(datetime.datetime.now() - start, "start creating txsns")
    print(Client(host).get_balance(sender.public_key()))
    print(Client(host).get_balance(recipient.public_key()))

    tx_list = []
    for i in range(args.tps):
        tx = Transaction().add(transfer(TransferParams(from_pubkey=sender.public_key(),
                                                       to_pubkey=recipient.public_key(), lamports=11111+i )))
        tx.recent_blockhash = recent_blockhash
        tx.sign(sender)
        tx_list.append(tx.serialize())

    print(datetime.datetime.now() - start, "start sending")
    asyncio.run(batch_sender(tx_list))
    print(datetime.datetime.now() - start, "done")
    print(Client(host).get_balance(recipient.public_key()))
    time.sleep(15)
    print(Client(host).get_balance(recipient.public_key()))

# python tools/transaction_sender.py --tps 15"