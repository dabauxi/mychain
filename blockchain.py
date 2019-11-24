import hashlib
import time
import json


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
    def __init__(self, transactions: list, previous_tx: str, index: int):
        self.transactions = transactions
        self.timestamp = time.time()
        self.previous_tx = previous_tx
        self.index = index
        self.tx_id = self._hash()

    def _hash(self):
        self.tx_id = _sha256(f"{json.dumps(self.transactions)}{self.timestamp}")


class Blockchain:
    def __init__(self):
        self.blocks: list = list()
        self.mem_pool: list = list()
        self.head: str = _sha256("genesis")
        self._new_block()
        self.nr_of_blocks = -1

    def _new_block(self):
        self.blocks.append(Block(self.mem_pool, self.head, self.nr_of_blocks + 1))

    def add_transaction(self, transaction: Transaction):
        if len(self.mem_pool) < 16:
            self.mem_pool.append(transaction)
        else:
            self._new_block()
            self.mem_pool = list()

    def last_block(self):
        return self.blocks[-1]
