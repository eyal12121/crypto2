class Server:
    def __init__(self):
        self.storage = {}

    def store_data(self, file_name, chunk_data, chunk_index, chunk_requirements):
        """
        Store a chunk of data and its requirements.
        """
        self.storage[file_name] = chunk_data, chunk_index, chunk_requirements

    def remove_data(self, file_name):
        """
        Removes the requested data from the storage.
        """
        self.storage.pop(file_name)

    def push_data(self, file_name, chunks_queue):
        """
        Push the requested data into the given queue.
        """
        chunks_queue.put(self.storage.get(file_name, None))

    def check_data(self, file_name):
        return self.storage[file_name][0] == None
