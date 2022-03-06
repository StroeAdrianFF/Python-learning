from rfc3986 import is_valid_uri


MINING_REWARD = 10

# initializing blockchain list
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}
blockchain = [genesis_block]
open_transactions = []
owner = 'Adrian'
participants = {'Adrian'}


def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None  # returned none since there is nothing inside
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    if verify_transaction(transaction):     
        open_transactions.append(transaction)
        participants.add(sender)  # duplicates will be ignored
        participants.add(recipient)
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    copied_transactions = open_transactions[:] #copy open transactions from start to end
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions #ensure that we manipulate a list of transaction which is managed locally not globally
    }
    blockchain.append(block)
    return True


def get_trans_value():
    trans_recipient = input('Enter recipient of transaction:')
    trans_amount = float(input('Amount to be transacted: '))
    return (trans_recipient, trans_amount)


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain():
    for block in blockchain:
        print('Outputting a block')
        print(block)


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_balances(participant):
    trans_sender = [[transactions['amount'] for transactions in block['transactions'] if transactions['sender'] == participant] for block in blockchain]
    trans_recipient = [[transactions['amount'] for transactions in block['transactions'] if transactions['recipient'] == participant] for block in blockchain]
    open_trans_sender = [transactions['amount'] for transactions in open_transactions if transactions['sender'] == participant]
    trans_sender.append(open_trans_sender)
    amount_sent = 0
    for trans in trans_sender:
        if len(trans) > 0:
            amount_sent += trans[0]
    amount_received = 0
    for trans in trans_recipient:
        if len(trans) > 0:
            amount_sent += trans[0]
    return amount_received - amount_sent


def verify_chain():
    # enumarte contains index of element and the element as a tuple
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index-1]):
            return False
    return True


def verify_transaction(transaction):
    sender_balance  =get_balances(transaction['sender'])
    return sender_balance >= transaction['amount']
    

def verify_transactions():
    return all([verify_transaction(transaction) for transaction in open_transactions])

waiting_input = True
while waiting_input:
    print('Choose: ')
    print('1: Add new value')
    print('2: Mine new block')
    print('3: Output blocks')
    print('4: Exit')
    print('5: Manipulate block')
    print('6: Output participants')
    print('7: Check transaction validity')
    user_choice = get_user_choice()

    if user_choice == '1':
        transaction_data = get_trans_value()
        recipient, amount = transaction_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
    elif user_choice == '3':
        print_blockchain()
    elif user_choice == '5':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'chris', 'recipient': 'adi', 'amount': 100}]
            }
    elif user_choice == '4':
        waiting_input = False
    elif user_choice == '6':
        print(participants)
    elif user_choice == '7':
        if verify_transactions:
            print('All transactions are valid')
        else:
            print('There are invalid transactions')
    else:
        print('Input is invalid. Try again!')
    if not verify_chain():
        print_blockchain()
        print('Invalid blockchain!')
        break
    print(get_balances('Adrian'))
