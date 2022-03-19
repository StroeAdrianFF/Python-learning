import json
import hashlib as hashing


def hash_string256(string):
    return hashing.sha256(string).hexdigest()


def hash_block(block):
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [trans.to_ordered_dict() for trans in hashable_block['transactions']]


    return hash_string256(json.dumps(hashable_block, sort_keys=True).encode()) #hash block from json string
