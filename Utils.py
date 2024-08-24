import hashlib


class Utils:

    @staticmethod
    def hash_data(data):
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_concat(left, right):
        return hashlib.sha256((left + right).encode('utf-8')).hexdigest()

    @staticmethod
    def verify_data(data, proof, root_hash):
        hashed = Utils.hash_data(data)  # Hash of the data chunk
        for sibling in proof:
            hashed = Utils.hash_concat(hashed, sibling)  # Combine with sibling hashes
        return hashed == root_hash  # Verify against the root hash

    # Function to build a Merkle tree and get root hash
