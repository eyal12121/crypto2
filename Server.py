

class Server:
    def __init__(self):
        self.storage = {}  # Dictionary to store chunks and their hashes

    def store_data(self, chunk_data, chunk_index, chunk_requirements):
        """
        Store a chunk of data and its requirements.
        """

        self.storage[chunk_data] = chunk_data, chunk_index, chunk_requirements

    def push_data(self, chunk_data, chunks_queue):
        """
        Push the requested data into the given queue.
        """
        chunks_queue.push(self.storage.get(chunk_data, None))
