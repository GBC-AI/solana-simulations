from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.account import Account
import solana

hc = Client("https://devnet.solana.com")

print(hc.get_fees())

sender, reciever = Account(5), Account(6)
hc.request_airdrop(sender.public_key(), 1000000)
for i in range(2):
    tx = Transaction().add(transfer(TransferParams(from_pubkey=sender.public_key(),\
                                               to_pubkey=reciever.public_key(), lamports=10000)))
    response = hc.send_transaction(tx, sender)
    print(response)

"""
http://devnet.solana.com:8899 {'Content-Type': 'application/json'} {"jsonrpc": "2.0", "id": 6, "method": "sendTransaction", "params": "AU5beTHRSOCpGs1GvsCd9tI4r7PqeFdf2cU6dFH0bChuBiLg5o7XHniX/YLWlGhdNkLuMhUEDus8ieHkOYIHWQEBAAED/eT7oDCtAC98L31MMx9J0T+w7HR+zuvsY08f9MvKne+0ySr7O6V/OrlZ/+bTGcmEhKIVWg9MZbLDcBH/0ZewdQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4mPWVlQxjHfNtXxKBfGW6jhSgcJiwerKBX7JbiSJYAgBAgIAAQwCAAAAECcAAAAAAAA="}
{"jsonrpc":"2.0","error":{"code":-32600,"message":"Invalid request"},"id":4}
"""

print(hc.get_confirmed_transaction('5DC8gxAVmxS85gUzdTEE61N4N5ZJRVNMQ5TH7GN3sGdTHdpmU3jrxKjXMEtcnvgtEVYrKbiXx1ZLSjAChYfGQ1Nw'))