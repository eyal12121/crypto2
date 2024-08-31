import sys
import zfec
from Utils import Utils
from Server import Server

CHUNKS_NUMBER = 13
REDUNDANT_SIZE = 3


class MainServer:

    def __init__(self):
        self.files_map = {}
        self.servers = [Server() for _ in range(CHUNKS_NUMBER + REDUNDANT_SIZE)]

    @staticmethod
    def check_signature(obj, signature, signer_prime, signer_generator, signer_public_key):
        """
        Checks the validity of an object's signature.
        """
        check = pow(signer_generator, signature[0], signer_prime) * pow(signer_public_key, signature[1],
                                                                        signer_prime) % signer_prime
        return int(Utils.hash_concat(str(check), str(obj)), 16) == signature[1]

    def recover_servers(self, retrieved_chunks, indices, all_connections, file_name):
        """
        Recovers servers that have fallen or got malicious.
        """
        encoder = zfec.Encoder(CHUNKS_NUMBER, CHUNKS_NUMBER + REDUNDANT_SIZE)
        shares = encoder.encode(retrieved_chunks)
        proofs = MainServer.build_merkle_tree(shares)[1]
        for ind in range(CHUNKS_NUMBER + REDUNDANT_SIZE):
            if ind not in indices:
                if ind not in all_connections or not self.servers[ind].check_data(file_name):
                    new_server = Server()
                    for key in self.files_map.keys():
                        new_server.store_data(key, None, ind, None)
                    self.servers[ind] = new_server
                self.servers[ind].store_data(file_name, shares[ind], ind, proofs[ind])

    @staticmethod
    def split_into_chunks(data, k):
        """
        Splits the data into k chunks.
        """
        chunk_size = len(data) // k
        chunks = [data[i * chunk_size: (i + 1) * chunk_size] for i in range(k)]
        if len(data) % k != 0:
            chunks[-1] += data[k * chunk_size:]
        return chunks

    def add_file(self, file_contents, file_name, signature):
        """
        Adds a file to the system by dividing it into chunks and distributing it amongst different servers.
        """
        encoded_chunks = file_contents.encode('utf-8')

        # Ensure data length is a multiple of data_shares by padding if necessary
        pad_len = CHUNKS_NUMBER - (len(encoded_chunks) % CHUNKS_NUMBER)
        padded_data = encoded_chunks + b'\0' * pad_len

        # Split the padded data into blocks
        block_size = len(padded_data) // CHUNKS_NUMBER
        blocks = [padded_data[i * block_size:(i + 1) * block_size] for i in range(CHUNKS_NUMBER)]

        encoder = zfec.Encoder(CHUNKS_NUMBER, CHUNKS_NUMBER + REDUNDANT_SIZE)
        shares = encoder.encode(blocks)

        root_hash, proofs = self.build_merkle_tree(shares)
        for ind, server in enumerate(self.servers):
            server.store_data(file_name, shares[ind], ind, proofs[ind])

        self.files_map[file_name] = {
            "num_parts": CHUNKS_NUMBER,
            "redundant": REDUNDANT_SIZE,
            "root_hash": root_hash,
            "signature": signature
        }
        return True, root_hash

    def remove_file(self, filename, signer_prime, signer_generator, signer_public_key):
        """
        Removes file data chunks from the different servers only if client which requested to remove it is the one that
        uploaded the said file.
        """
        if filename not in self.files_map:
            print("File does not exist", file=sys.stderr)
            return False
        if self.check_signature(filename, self.files_map[filename]["signature"], signer_prime, signer_generator,
                                signer_public_key):
            for server in self.servers:
                server.remove_data(filename)
            self.files_map.pop(filename)
            return True
        print("No permissions to remove file", file=sys.stderr)
        return False

    def get_file(self, filename, data_queue):
        """
        Gets file data chunks from the different servers.
        """
        if filename not in self.files_map.keys():
            return None
        for server in self.servers:
            if server is not None:
                server.push_data(filename, data_queue)
        return self.files_map[filename]

    @staticmethod
    def build_merkle_tree(leaves):
        """
        Builds a merkle tree and calculates the proof data for each leaf.
        """
        current_level = [Utils.hash_data(leaf) for leaf in leaves]
        proofs = [[] for _ in leaves]
        cur = 1
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level) - 1, 2):
                left_hash = current_level[i]
                right_hash = current_level[i + 1]
                next_level.append(Utils.hash_concat(left_hash, right_hash))

                # Store proof for both leaves
                for ind in range(i * cur, (i + 1) * cur):
                    proofs[ind].append((right_hash, "right"))
                for ind in range((i + 1) * cur, min((i + 2) * cur, len(proofs))):
                    proofs[ind].append((left_hash, "left"))

            if len(current_level) % 2 == 1:
                next_level.append(current_level[-1])

            current_level = next_level
            cur *= 2

        return current_level[0], proofs

    def corrupt_data(self, file_name, num):
        """
        simulates corruption to a server.
        """
        # random_server = random.randint(0, len(self.servers) - 1)
        self.servers[num].corrupt_data(file_name)

    def connection_loss(self, num):
        """
        Simulates connection loss to a server.
        """
        # random_server = random.randint(0, len(self.servers) - 1)
        self.servers[num] = None
