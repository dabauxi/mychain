import hashlib
import time
import json
import uuid

from flask import Flask, jsonify, request


def _sha256(input_: str):
    return hashlib.sha256(input_.encode()).hexdigest()


class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
        self.tx_id = _sha256(f"{self.sender}{self.recipient}{self.amount}{self.timestamp}")


class Block:
    def __init__(self, transactions: list, previous_tx: str, index: int, proof: int):
        self.transactions = transactions
        self.timestamp = time.time()
        self.previous_tx = previous_tx
        self.index = index
        self.tx_id = self._hash()
        self.proof = proof

    def _hash(self):
        self.tx_id = _sha256(f"{json.dumps(self.transactions)}{self.timestamp}")


class Blockchain:
    def __init__(self):
        self.blocks: list = list()
        self.mem_pool: list = list()
        self.head: str = _sha256("genesis")
        self.nr_of_blocks = -1
        self.difficulty = 5

    def add_block(self, block):
        last_block = self.last_block()
        last_proof = last_block.proof
        if len(block.transactions) > 16 or not self.validate_block(last_proof, block):
            return False
        self.blocks.append(block)
        return True

    def validate_block(self, last_proof, block):
        self.is_valid_hash(last_proof, block.proof)

    def get_transactions(self):
        return self.mem_pool

    def add_transaction(self, transaction: Transaction):
        if len(self.mem_pool) < 16:
            self.mem_pool.append(transaction)
            return transaction.tx_id
        else:
            return "mempool exhausted"


    def last_block(self):
        return self.blocks[-1]


    def proof_of_work(self, last_proof):
        proof = 0
        while self.is_valid_hash(last_proof, proof):
            proof += 1
        return proof


    def is_valid_hash(self, last_proof, new_proof):
        guess = f"{last_proof}{new_proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == "0" * self.difficulty

app = Flask(__name__)

node_uuid = str(uuid.uuid4()).replace("-", "")

blockchain = Blockchain()

@app.route("/mine", methods=["GET"])
def mine():
    last_block: Block = blockchain.last_block()
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    reward_transaction = Transaction("0", node_uuid, 1)

    transactions = blockchain.get_transactions()
    transactions.append(reward_transaction)
    del transactions[0]
    block = Block(transactions, last_block.tx_id, last_block.index+1, proof)
    blockchain.add_block(block)

    return ""

@app.route("/submit_transaction", methods=["POST"])
def new_transaction():
    values = request.get_json()

    required_fields = {"sender", "recipient", "amount"}

    if not all(r in values for r in required_fields):
        return "Missing value", 400

    transaction = Transaction(values["sender"], values["recipient"], values["amount"])
    tx_id = blockchain.add_transaction(transaction)

    response = f"Transaction {tx_id} added to mempool"

    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def chain():
    response = {
        "chain": blockchain.blocks,
        "length": blockchain.nr_of_blocks
    }
    return jsonify(response), 200

@app.route("/nodes/register", methods=["POST"])
def register_node():
    pass

@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)