import hashlib


class Utils:

    @staticmethod
    def hash_data(data):
        """
        Hashes the given data.
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_concat(left, right):
        """
        Concatenates the given data and then hashes it.
        """
        return hashlib.sha256((left + right).encode('utf-8')).hexdigest()
