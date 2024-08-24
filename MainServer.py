import threading

import reedsolo
from Utils import Utils

from Server import Server

CHUNKS_NUMBER = 7
REDUNDANT_SIZE = 1


class MainServer:

    def __init__(self):
        self.files_map = {}
        self.servers = [Server() for _ in range(CHUNKS_NUMBER + REDUNDANT_SIZE)]

    def generate_redundant_chunks(self, data_chunks, r):
        rs = RSCodec(r)
        encoded_data = rs.encode(b''.join(data_chunks))
        n = len(data_chunks) + r
        return split_into_chunks(encoded_data, n)

    def split_into_chunks(self, data, k):
        chunk_size = len(data) // k
        chunks = [data[i * chunk_size: (i + 1) * chunk_size] for i in range(k)]
        if len(data) % k != 0:
            chunks[-1] += data[k * chunk_size:]  # Add any remaining data to the last chunk
        return chunks

    def add_file(self, file_contents, file_name):
        encoded_chunks = file_contents.encode('utf-8')

        # encoder = reedsolo.RSCodec(REDUNDANT_SIZE)
        #
        # encoded_chunks = encoder.encode(data_bytes)
        i = len(encoded_chunks) % (CHUNKS_NUMBER )
        chunk_size = len(encoded_chunks) // (CHUNKS_NUMBER) + i
        chunks = [encoded_chunks[i:i + chunk_size] for i in range(0, len(encoded_chunks), chunk_size)]
        # Step 3: Generate the 4 redundant blocks using Reed-Solomon coding
        redundentChunks = self.generate_redundant_chunks(chunks, REDUNDANT_SIZE)
        chunks += redundentChunks[CHUNKS_NUMBER:]

        root_hash, proofs = self.build_merkle_tree(chunks)
        for ind, server in enumerate(self.servers):
            server.store_data(file_name, chunks[ind], ind, proofs[ind])

        self.files_map[file_name] = {
            "num_parts": CHUNKS_NUMBER,
            "redundant": REDUNDANT_SIZE,
            "root_hash": root_hash
        }
        return True, root_hash

    def get_file(self, filename, data_queue):
        for server in self.servers:
            server.push_data(filename, data_queue)
        return self.files_map[filename]

    def build_merkle_tree(self, leaves):
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
