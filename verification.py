from  hash_util import  hash_string256, hash_block

class Verification:
    @staticmethod #because valid proof only gets input from outside, it's not accessing anything from the class itself
    def valid_proof(transactions, last_hash, proof_number):
        guess = (str([trans.to_ordered_dict() for trans in transactions])+ str(last_hash) + str(proof_number)).encode()
        guess_hash = hash_string256(guess)  #get valid string
        print(guess_hash)
        return guess_hash[0:2] == '00' #check if hash is valid only if it starts with 2 zeros

    @classmethod #accesses something from inside the class, in this case, valid_proof
    def verify_chain(cls, blockchain):
        # enumerate contains index of element and the element as a tuple
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index-1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balances):
        sender_balance = get_balances()
        return sender_balance >= transaction.amount
    
    @classmethod
    def verify_transactions(cls,  open_transactions, get_balances):
        return all([cls.verify_transaction(transaction, get_balances) for transaction in open_transactions])
