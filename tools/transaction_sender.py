import asyncio
import aiohttp
import datetime
from aiohttp import ClientSession
import json
import solana
import itertools

from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.account import Account
from solana.rpc.api import Client
from solana.blockhash import Blockhash
from solana.rpc.types import URI, RPCMethod, RPCResponse

import itertools
import logging
import os
from typing import Any, Optional, cast
from solana.rpc._utils.encoding import FriendlyJsonSerde
from solana.rpc.types import URI, RPCMethod, RPCResponse
from solana.rpc.providers.base import BaseProvider
from base64 import b64encode
from solana.rpc.types import RPCMethod

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
          resp = await response.text()
          # print(resp, end='')

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


if __name__ == '__main__':
    host = "http://devnet.solana.com:8899"
    n = 100
    start = datetime.datetime.now()
    print(start)
    sender, recipient = Account(5), Account(6)
    hc = Client("https://devnet.solana.com")
    hc.request_airdrop(sender.public_key(), 1000000000)
    tx_list = []
    try:
        # TODO: Cache recent blockhash
        blockhash_resp = hc.get_recent_blockhash()
        if not blockhash_resp["result"]:
            raise RuntimeError("failed to get recent blockhash")
        recent_blockhash = Blockhash(blockhash_resp["result"]["value"]["blockhash"])
    except Exception as err:
        raise RuntimeError("failed to get recent blockhash") from err
    print(datetime.datetime.now() - start, "start creating txsns")
    for _ in range(n):
        tx = Transaction().add(transfer(TransferParams(from_pubkey=sender.public_key(),
                                                       to_pubkey=recipient.public_key(), lamports=11111 + _)))
        tx.recent_blockhash = recent_blockhash
        # tx.nonce_info = _ + 2
        tx.sign(sender)
        tx_list.append(tx.serialize())

    print(datetime.datetime.now() - start, "start sending")
    asyncio.run(batch_sender(tx_list))
    print(datetime.datetime.now() - start, "done")
