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

    def verify_chunk(self, chunk, root_hash):
        """
        Verify individual chunk.
        """
        chunk_data, index, siblings = chunk
        curr_data = self.hash_data(chunk_data)
        for sibling, sibling_side in siblings:
            if sibling_side == "right":
                curr_data = self.hash_data(curr_data + sibling)
            else:
                curr_data = self.hash_data(sibling + curr_data)

        return curr_data == root_hash, chunk_data, index

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
            return False, None

        root_hash = file_metadata["root_hash"]
        chunks_queue = file_metadata["queue"]

        retrieved_chunks = [None] * len(chunks_queue)
        for chunk in chunks_queue:
            verified, chunk_data, index = self.verify_chunk(chunk, root_hash)
            if not verified:
                return verified, None
            retrieved_chunks[index] = chunk_data

        return True, self.reassemble_file(retrieved_chunks, output_path)
