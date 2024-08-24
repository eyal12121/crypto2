
import hashlib
class Utils:
    import hashlib
    # Function to hash data
    @staticmethod

    def hash_data(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    # Function to concatenate hashes
    @staticmethod

    def hash_concat(left, right):
        return hashlib.sha256((left + right).encode('utf-8')).hexdigest()
    @staticmethod

    def verify_data(data, proof, root_hash):
        hash = Utils.hash_data(data)  # Hash of the data chunk
        for sibling in proof:
            hash = Utils.hash_concat(hash, sibling)  # Combine with sibling hashes
        return hash == root_hash  # Verify against the root hash

    # Function to build a Merkle tree and get root hash