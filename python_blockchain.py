from functools import reduce
import hashlib as hashing
import json
import pickle
from flask import request #import python data to binary data in a file to serialize and unserialize
import requests

from block import Block
from transaction import Transaction
from utility.hash_util import hash_block
from utility.verification import Verification 
from wallet import Wallet
MINING_REWARD = 10
class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block] #empty blockchain
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()


    @property #what to get if you want to access chain
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val



    def get_open_transactions(self):
        return self.__open_transactions[:]


    def load_data(self):
        try:
            with open(f'savedChain-{self.node_id}.txt', mode='r') as opened:#rb = read binary
                #content = pickle.loads(opened.read())
                content = opened.readlines()
                
                #blockchain = content['chain']
                #open_transactions = content['ot']
                blockchain = json.loads(content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_transactions = [Transaction(trans['sender'], trans['recipient'], trans['signature'], trans['amount']) for trans in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_transactions, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(content[1])
                updated_transactions = []
                for trans in open_transactions:
                    updated_transaction = Transaction(trans['sender'], trans['recipient'], trans['signature'], trans['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup!')
        



    def save_data(self):
        try:
            with open(f'savedChain-{self.node_id}.txt', mode = 'w') as saved:#wb = write binary
                savable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [trans.__dict__ for trans in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                savable_trans = [trans.__dict__ for trans in self.__open_transactions]
                saved.write(json.dumps(savable_chain))
                saved.write('\n')
                saved.write(json.dumps(savable_trans))
                saved.write('\n')
                saved.write(json.dumps(list(self.__peer_nodes)))
                #save_data = {
                #    'chain': blockchain,
                #    'ot': open_transactions
                #}
                #saved.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')


    def pow(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof


    def get_balances(self, sender=None):
        if sender == None:
            if self.public_key == None:
                return None
            participant = self.public_key
        else:
            participant = sender
        trans_sender = [[transactions.amount for transactions in block.transactions if transactions.sender == participant] for block in self.__chain]
        trans_recipient = [[transactions.amount for transactions in block.transactions if transactions.recipient == participant] for block in self.__chain]
        open_trans_sender = [transactions.amount for transactions in self.__open_transactions if transactions.sender == participant]
        trans_sender.append(open_trans_sender)
        amount_sent = reduce(lambda trans_sum,trans_amount:trans_sum+sum(trans_amount) if len(trans_amount)>0 else trans_sum + 0, trans_sender, 0)
        amount_received = reduce(lambda trans_sum, trans_amount: trans_sum+sum(trans_amount) if len(trans_amount)>0 else trans_sum + 0, trans_recipient, 0)
    
        return amount_received - amount_sent


    def get_last_blockchain_value(self):
        if len(self.__chain) < 1:
            return None  # returned none since there is nothing inside
        return self.__chain[-1]



    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving = False):
    #    transaction = {
    #        'sender': sender,
    #        'recipient': recipient,
    #        'amount': amount
    #    } 

        if self.public_key == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balances):     
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = f'http://{node}/broadcast-transaction'
                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False


    def mine_block(self):
        """ if self.public_key == None:
            return None """
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.pow()

        reward_transaction = Transaction('MINING', self.public_key, '', MINING_REWARD)
        copied_transactions = self.__open_transactions[:] #copy open transactions from start to end
        for trans in copied_transactions:
            if not Wallet.verify_transaction(trans):
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)
        
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        for node in self.__peer_nodes:
            url = f'http://{node}/broadcast-block'
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [trans.__dict__ for trans in converted_block['transactions']]
            try:
                response = requests.post(url,json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block


    def add_block(self, block):
        transactions = [Transaction(trans['sender'], trans['recipient'], trans['signature'], trans['amount']) for trans in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True


    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = f'http://{node}/chain'
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block['index'], block['previous_hash'], [Transaction(trans['sender'], trans['recipient'], trans['signature'], trans['amount']) for trans in block['transactions']], block['proof'], block['timestamp']) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError: 
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace


    def add_peer_node(self,node):
        self.__peer_nodes.add(node) #add() special set method
        self.save_data()


    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    
    def get_peer_nodes(self):
        return list(self.__peer_nodes)