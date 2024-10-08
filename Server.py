from random import getrandbits


class Server:
    def __init__(self):
        self.storage = {}

    def store_data(self, file_name, chunk_data, chunk_index, chunk_requirements):
        """
        Stores a chunk of data and its requirements.
        """
        self.storage[file_name] = chunk_data, chunk_index, chunk_requirements

    def remove_data(self, file_name):
        """
        Removes the requested data from the storage.
        """
        self.storage.pop(file_name)

    def push_data(self, file_name, chunks_queue):
        """
        Pushes the requested data into the given queue.
        """
        chunks_queue.put(self.storage.get(file_name, None))

    def check_data(self, file_name):
        """
        Checks if the data of a file is available.
        """
        return self.storage[file_name][0] is None

    def corrupt_data(self, file_name):
        """
        Changes the data of a file, used for testings.
        """
        self.storage[file_name] = bytearray(getrandbits(8) for _ in range(10)), self.storage[file_name][
            1], self.storage[file_name][2]
