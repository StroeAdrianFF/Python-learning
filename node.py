from python_blockchain import Blockchain
from verification import Verification
from uuid import uuid4

class Node:
    def __init__(self):
        """ self.id = str(uuid4()) """
        self.id = "Adrian"
        self.blockchain = Blockchain(self.id)

    def get_trans_value(self):
        trans_recipient = input('Enter recipient of transaction:')
        trans_amount = float(input('Amount to be transacted: '))
        return (trans_recipient, trans_amount)


    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input


    def print_blockchain(self):
        for block in self.blockchain.chain:
            print('Outputting a block')
            print(block)



    def listen_for_input(self):
        waiting_input = True
        while waiting_input:
            print('Choose: ')
            print('1: Add new value')
            print('2: Mine new block')
            print('3: Output blocks')
            print('4: Exit')
            print('5: Check transaction validity')
            user_choice = self.get_user_choice()

            if user_choice == '1':
                transaction_data = self.get_trans_value()
                recipient, amount = transaction_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain()
            elif user_choice == '4':
                waiting_input = False
            elif user_choice == '5':
                
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balances):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions')
            else:
                print('Input is invalid. Try again!')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain()
                print('Invalid blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(self.id, self.blockchain.get_balances()))


node = Node()
node.listen_for_input()