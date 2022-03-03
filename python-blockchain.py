# initializing blockchain list
blockchain = []


def get_last_blockchain_value():
    if len(blockchain) < 1:
        return None  # returned none since there is nothing inside
    return blockchain[-1]


def add_transaction(amount, last_value):
    if last_value == None:
        last_value = [1]
    blockchain.append([last_value, amount])


def get_trans_value():
    return float(input('Amount to be transacted: '))


def get_user_choice():
    return input('Your choice: ')


def print_blockchain():
    for block in blockchain:
        print('Outputting a block')
        print(block)


def verify_chain():
    is_valid = True
    for block_index in range(len(block_index)):
        if block_index == 0:
            continue
        elif blockchain[block_index][0] == blockchain[block_index-1]:
            is_valid = True
        else:
            is_valid = False
            break
    return is_valid


waiting_input = True
while waiting_input:
    print('Choose: ')
    print('1: Add new value')
    print('2: Output blocks')
    print('3: Exit')
    print('4: Manipulate block')
    user_choice = get_user_choice()

    if user_choice == '1':
        transaction_amount = get_trans_value()
        add_transaction(transaction_amount, get_last_blockchain_value())
    elif user_choice == '2':
        print_blockchain()
    elif user_choice == '4':
        if len(blockchain) >= 1:
            blockchain[0] = [2]
    elif user_choice == '3':
        waiting_input = False
    else:
        print('Input is invalid. Try again!')
    if not verify_chain():
        print_blockchain()
        print('Invalid blockchain!')
        break
