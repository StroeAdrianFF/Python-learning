from functools import reduce
import hashlib as hashing
from  hash_util import   hash_block
import json
import pickle #import python data to binary data in a file to serialize and unserialize

from block import Block
from transaction import Transaction
from verification import Verification

MINING_REWARD = 10
class Blockchain:
    def __init__(self, host_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block] #empty blockchain
        self.__open_transactions = []
        self.load_data()
        self.host_node = host_node_id


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
            with open('savedChain.txt', mode='r') as opened:#rb = read binary
                #content = pickle.loads(opened.read())
                content = opened.readlines()
                
                #blockchain = content['chain']
                #open_transactions = content['ot']
                blockchain = json.loads(content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_transactions = [Transaction(trans['sender'], trans['recipient'], trans['amount']) for trans in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_transactions, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(content[1])
                updated_transactions = []
                for trans in open_transactions:
                    updated_transaction = Transaction(trans['sender'], trans['recipient'], trans['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
           pass
        finally:
            print('Cleanup!')
        



    def save_data(self):
        try:
            with open('savedChain.txt', mode = 'w') as saved:#wb = write binary
                savable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [trans.__dict__ for trans in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                savable_trans = [trans.__dict__ for trans in self.__open_transactions]
                saved.write(json.dumps(savable_chain))
                saved.write('\n')
                saved.write(json.dumps(savable_trans))
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


    def get_balances(self):
        participant = self.host_node
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



    def add_transaction(self, recipient, sender, amount=1.0):
    #    transaction = {
    #        'sender': sender,
    #        'recipient': recipient,
    #        'amount': amount
    #    } 
        transaction = Transaction(sender, recipient, amount)
        
        if Verification.verify_transaction(transaction, self.get_balances):     
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False


    def mine_block(self):
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.pow()

        reward_transaction = Transaction('MINING', self.host_node, MINING_REWARD)
        copied_transactions = self.__open_transactions[:] #copy open transactions from start to end
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)
        
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True



