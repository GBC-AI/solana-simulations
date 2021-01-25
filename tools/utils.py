import json
import requests


def count_skip_rate(url, num_slots, id1="1", id2="2", start_slot=None):
    headers = {"Content-Type": "application/json"}
    get_slot_data = json.dumps({"jsonrpc": "2.0", "id": id1, "method": "getSlot"})
    response_get_slot = requests.post(url, headers=headers, data=get_slot_data)
    slot_id = response_get_slot.json()['result']
    if start_slot is None:
        params = [slot_id - num_slots, slot_id]
    else:
        params = [start_slot, start_slot + num_slots]
    data_confirmed_blocks = json.dumps({"jsonrpc": "2.0", "id": id2, "method": "getConfirmedBlocks", "params": params})
    response_conf_blocks = requests.post(url, headers=headers, data=data_confirmed_blocks)
    confirmed_blocks_list = response_conf_blocks.json()['result']
    return 1 - (len(confirmed_blocks_list) / (num_slots+1))
