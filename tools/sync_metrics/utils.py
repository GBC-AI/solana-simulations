import json
import requests
import asyncio
import aiohttp


def count_skip_rate(url, num_slots, id1="1", id2="2", start_slot=None):
    headers = {"Content-Type": "application/json"}
    if start_slot is None:
        get_slot_data = json.dumps({"jsonrpc": "2.0", "id": id1, "method": "getSlot"})
        response_get_slot = requests.post(url, headers=headers, data=get_slot_data)
        slot_id = response_get_slot.json()['result']
        params = [max(0, slot_id - num_slots), slot_id]
    else:
        params = [start_slot, start_slot + num_slots]
    confirmed_blocks_data = json.dumps({"jsonrpc": "2.0", "id": id2, "method": "getConfirmedBlocks", "params": params})
    response_conf_blocks = requests.post(url, headers=headers, data=confirmed_blocks_data)
    confirmed_blocks_list = response_conf_blocks.json()['result']
    return (1 - (len(confirmed_blocks_list) / (num_slots+1))) * 100


def get_cluster_info(url, id1=1):
    headers = {"Content-Type": "application/json"}
    get_info_data = json.dumps({"jsonrpc": "2.0", "id": id1, "method": "getClusterNodes"})
    response_info = requests.post(url, headers=headers, data=get_info_data)
    return [i['rpc'] for i in response_info.json()['result']]


async def get_node_info(session, url, request_id, num_slots=10):
    headers = {"Content-Type": "application/json"}
    data_slot = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": "getSlot"})
    resp_slot = await session.post(url=url, data=data_slot, headers=headers)
    slot_json = await resp_slot.json()
    slot = slot_json['result']
    params_block = [max(0, slot - num_slots), slot]
    data_block = json.dumps({"jsonrpc": "2.0", "id": request_id + 1, "method": "getConfirmedBlocks",
                             "params": params_block})
    resp_block = await session.post(url=url, data=data_block, headers=headers)
    block_json = await resp_block.json()
    block = max(block_json['result'])
    print(f'Received data for url {url}')
    return {'node_ip': url, 'slot': slot, 'last_block': block}


async def batch_info(batch_ips):
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        request_id = 3
        for ip in batch_ips:
            request_id += 2
            post_tasks.append(get_node_info(session, ip, request_id))
        data = await asyncio.gather(*post_tasks, return_exceptions=True)
        return data
