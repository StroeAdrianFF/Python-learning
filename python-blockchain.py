blockchain = [[1]]

def add_values(amount):
    blockchain.append([blockchain[-1], amount])
    print(blockchain)

add_values(2)
add_values(5)
add_values(8)
add_values(1.3)