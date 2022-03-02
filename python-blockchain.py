# initializing blockchain list
blockchain = []


def get_last_blockchain_value():
    return blockchain[-1]


def add_values(amount, last_value=[1]):
    blockchain.append([last_value, amount])


def get_user_input():
    return float(input('Amount to be transacted: '))


transaction_amount = get_user_input()
add_values(transaction_amount)

transaction_amount = float(input('Amount to be transacted: '))
add_values(last_value=get_last_blockchain_value(), amount=transaction_amount)

transaction_amount = float(input('Amount to be transacted: '))
add_values(transaction_amount, get_last_blockchain_value())


print(blockchain)
