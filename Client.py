import queue
import time

from Utils import Utils
from reedsolo import RSCodec
import secrets
from sympy import isprime


class Client:
    def __init__(self, main_server):
        self.main_server = main_server
        self.p, self._q = self.generate_safe_prime()
        self.g = self.find_generator()
        self._secret_key = self.generate_key()
        self.public_key = pow(self.g, self._secret_key, self.p)

    @staticmethod
    def generate_safe_prime(bits=32):
        """
        This function generates a safe prime p and its Sophie Germain prime q.
        """
        while True:
            q = secrets.randbits(bits - 1)
            p = 2 * q + 1
            if isprime(q) and isprime(p):
                return p, q

    def find_generator(self):
        """
        This function finds a generator for the multiplicative group of integers modulo p.
        """
        for g in range(2, self.p):
            if pow(g, self._q, self.p) != 1:
                return g
        raise Exception("No generator found")

    def generate_key(self):
        """
        This function generates a private key x in the range [1, q-1].
        """
        x = secrets.randbelow(self._q - 1) + 1
        return x

    def sign_object(self, obj):
        """
        This function signs an object using the entity's private key.
        """
        k = self.generate_key()
        r = pow(self.g, k, self.p)
        h = Utils.hash_concat(str(r), obj)
        sigma = (k - self._secret_key * int(h, 16))
        return sigma, int(h, 16)

    def add_file(self, file):
        """
        Add a file to the file system.
        """
        with open(file, "r") as f:
            file_content = f.read()
        return self.main_server.add_file(file_content, file, self.sign_object(file))

    @staticmethod
    def verify_chunk(chunk, root_hash):
        """
        Verify individual chunk.
        """
        chunk_data, index, siblings = chunk
        curr_data = Utils.hash_data(chunk_data)
        for sibling, sibling_side in siblings:
            if sibling_side == "right":
                curr_data = Utils.hash_concat(curr_data, sibling)
            else:
                curr_data = Utils.hash_concat(sibling, curr_data)

        return curr_data == root_hash, chunk_data, index

    @staticmethod
    def reassemble_file(chunks, output_path):
        """
        Reassemble the chunks into a complete file.
        """
        with open(output_path, 'wb') as output_file:
            for chunk in chunks:
                output_file.write(chunk)
        print(f"File reassembled and saved to {output_path}.")

    @staticmethod
    def recover_data(encoded_chunks, k, r):
        rs = RSCodec(r)
        # Combine the available chunks into a single byte string
        available_chunks = b''.join([chunk for chunk in encoded_chunks if chunk])
        # Decode the combined data
        decoded_data = rs.decode(available_chunks)
        return decoded_data

    def remove_file(self, file):
        return self.main_server.remove_file(file, self.p, self.g, self.public_key)

    def request_file(self, file_path, output_path):
        """
        Request a file from the main server and verify its integrity.
        """
        chunks_queue = queue.Queue()
        file_metadata = self.main_server.get_file(file_path, chunks_queue)
        if not file_metadata:
            print("File not found on the server.")
            return False, None

        root_hash = file_metadata["root_hash"]
        retrieved = 0
        repeat = False
        retrieved_chunks = [None] * (file_metadata["num_parts"] + file_metadata["redundant"])
        while retrieved < len(retrieved_chunks):
            try:
                repeat = False
                verified, chunk_data, index = self.verify_chunk(chunks_queue.get(), root_hash)
                if verified:
                    retrieved_chunks[index] = chunk_data
                    retrieved += 1
            except queue.Empty:
                if repeat:
                    break
                repeat = True
                time.sleep(5)
        retrieved_chunks[3] = None
        retrieved -= 1

        if (len(retrieved_chunks) - retrieved) > file_metadata["redundant"]:
            return False
        # Recover the missing chunk
        recovered_chunks = []
        for i in range(file_metadata["num_parts"] + file_metadata["redundant"]):
            if retrieved_chunks[i] is None:
                # Recover the lost chunk
                recovered_chunk = self.recover_data(retrieved_chunks, file_metadata["num_parts"],
                                                    file_metadata["redundant"])
                recovered_chunks.append(recovered_chunk)
            else:
                recovered_chunks.append(retrieved_chunks[i])

        return True, self.reassemble_file(retrieved_chunks[:file_metadata["num_parts"]], output_path)
