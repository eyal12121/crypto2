import hashlib


class Client:
    def __init__(self, main_server):
        self.main_server = main_server  # Reference to the main server

    def hash_data(self, data):
        """
        Generate a SHA-256 hash of the given data.
        """
        return hashlib.sha256(data).hexdigest()

    def add_file(self, file):
        """
        Add a file to the file system.
        """
        return self.main_server.add_file(file)

    def build_merkle_tree(self, chunks):
        """
        Build a Merkle tree from file chunks and return the root hash.
        """
        chunk_hashes = [self.hash_data(chunk) for chunk in chunks]

        # Build the Merkle tree bottom-up
        current_layer = chunk_hashes
        while len(current_layer) > 1:
            new_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i+1] if i+1 < len(current_layer) else left
                combined_hash = self.hash_data((left + right).encode())
                new_layer.append(combined_hash)
            current_layer = new_layer

        return current_layer[0] if current_layer else None

    def verify_chunk(self, chunk, root_hash):
        """
        Verify individual chunk.
        """
        chunk_data, siblings = chunk
        curr_data = self.hash_data(chunk_data)
        for sibling, sibling_side in siblings:
            if sibling_side == "right":
                curr_data = self.hash_data(curr_data + sibling)
            else:
                curr_data = self.hash_data(sibling + curr_data)

        return curr_data == root_hash, chunk_data

    def reassemble_file(self, chunks, output_path):
        """
        Reassemble the chunks into a complete file.
        """
        with open(output_path, 'wb') as output_file:
            for chunk in chunks:
                output_file.write(chunk)
        print(f"File reassembled and saved to {output_path}.")

    def request_file(self, file_path, output_path):
        """
        Request a file from the main server and verify its integrity.
        """
        file_metadata = self.main_server.get_file_metadata(file_path)
        if not file_metadata:
            print("File not found on the server.")
            return False

        root_hash = file_metadata["root_hash"]
        chunks_queue = file_metadata["queue"]

        # verify chunks
        retrieved_chunks = []
        for chunk in chunks_queue:
            verified, chunk_data = self.verify_chunk(chunk, root_hash)
            if not verified:
                return verified, None
            retrieved_chunks.append(chunk_data)

        return True, self.reassemble_file(retrieved_chunks, output_path)
