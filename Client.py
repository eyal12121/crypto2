import os
import queue
import time
import zfec


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
        with open(file, "r", encoding='utf-8') as f:
            file_content = f.read()
        return self.main_server.add_file(file_content, file, self.sign_object(file))

    @staticmethod
    def verify_chunk(chunk, root_hash):
        """
        Verify individual chunk.
        """
        chunk_data, index, siblings = chunk
        if chunk_data is None or siblings is None:
            return False, None, index
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

        temp_path = output_path + '.temp'
        with open(temp_path, 'wb') as output_file:
            for chunk in chunks:
                output_file.write(chunk)

        # Step 2: Read the temporary file and strip trailing null bytes
        with open(temp_path, 'rb') as temp_file:
            data = temp_file.read().rstrip(b'\0')

        # Step 3: Write the cleaned data to the final output file
        with open(output_path, 'wb') as output_file:
            output_file.write(data)
        os.remove(temp_path)
        print(f"File reassembled and saved to {output_path}.")


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
        indices = []
        all_connections = []
        proofs = {}
        while retrieved < len(retrieved_chunks):
            try:
                # repeat = False
                chunk = chunks_queue.get(timeout=5)
                proofs[chunk[1]] = chunk[2]
                verified, chunk_data, index = self.verify_chunk(chunk, root_hash)
                if verified and index != 1:
                    retrieved_chunks[index] = chunk_data
                    retrieved += 1
                    indices.append(index)
                all_connections.append(index)
            except queue.Empty:
                # if repeat:
                break
                # repeat = True
                # time.sleep(5)



        if file_metadata["num_parts"] + file_metadata["redundant"] - retrieved > file_metadata["redundant"]:
            return False
        # Recover the missing chunk
        recovered_chunks = []
        if file_metadata["num_parts"] + file_metadata["redundant"] > retrieved:
            for ind in indices[:file_metadata["num_parts"]]:
                recovered_chunks.append(retrieved_chunks[ind])
            # Initialize the decoder
            decoder = zfec.Decoder(file_metadata["num_parts"], file_metadata["redundant"] + file_metadata["num_parts"])

            # Decode the data from the available shares
            retrieved_chunks = decoder.decode(recovered_chunks, indices[:file_metadata["num_parts"]])
            encoder = zfec.Encoder(file_metadata["num_parts"], file_metadata["redundant"] + file_metadata["num_parts"])
            shares = encoder.encode(retrieved_chunks)
            self.main_server.recover_servers(shares, indices, all_connections, file_path)

        return True, self.reassemble_file(retrieved_chunks[:file_metadata["num_parts"]], output_path)
