class Server:
    def __init__(self):
        self.storage = {}  # Dictionary to store chunks and their hashes

    def store_data(self, file_name, chunk_data, chunk_index, chunk_requirements):
        """
        Store a chunk of data and its requirements.
        """

        self.storage[file_name] = chunk_data, chunk_index, chunk_requirements

    def push_data(self, file_name, chunks_queue):
        """
        Push the requested data into the given queue.
        """
        chunks_queue.put(self.storage.get(file_name, None))
