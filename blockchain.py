import datetime
import hashlib
import json
from flask import Flask, jsonify

'''
Building a Blockchain
'''
class Blockchain: 
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):

        # create a dict for the block
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
        }

        self.chain.append(block)
        
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    # the function that miners need to execute to find the proof
    # difficult to solve, easy to verify
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            # more leading zeroes, more diff to solve the problem
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest() # need to be asymetric
            
            # check with the fist 4 characteres of hash_operation (need to be 0000)
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
            
        return new_proof

    def hash(self, block):
        # get an object and take as string
        encoded_block = json.dumps(block, sort_keys= True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_idx = 1

        while block_idx < len(chain):

            # 1. check with the previous_hash is equal to the hash of the previous block
            block = chain[block_idx]
            if block['previous_hash'] != self.hash(previous_block): # -> using the method hash.
                return False
            
            # 2. proof of each bloock is valid
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_idx += 1
        
        return True


'''
Mining our Blockchain
'''

# 1. Create an web app
app = Flask(__name__)

# 2. Creating the blockchain
blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    # mine a block = solve the proof of work
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']

    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'Congratulations, you just mined a block!', 
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)

    if is_valid:
        response = { 'message': 'Blockchain is valid.'}
    else:
        response = { 'message': 'Houston, we have a problem.'}
    
    return jsonify(response), 200



# running app
app.run(host= '0.0.0.0', port= 5001)