import threading

import reedsolo
from Utils import Utils

from Server import Server

CHUNKS_NUMBER = 13
REDUNDANT_SIZE = 3


class MainServer:

    def __init__(self):
        self.files_map = {}
        self.servers = [Server() for _ in range(CHUNKS_NUMBER + REDUNDANT_SIZE)]

    def add_file(self, file_contents, file_name):
        data_bytes = file_contents.encode('utf-8')

        encoder = reedsolo.RSCodec(REDUNDANT_SIZE)

        encoded_chunks = encoder.encode(data_bytes)

        chunk_size = len(encoded_chunks) // (CHUNKS_NUMBER + REDUNDANT_SIZE)
        chunks = [encoded_chunks[i:i + chunk_size] for i in range(0, len(encoded_chunks), chunk_size)]
        root_hash, proofs = self.build_merkle_tree(chunks)
        for ind, server in enumerate(self.servers):
            server.store_data(file_name, chunks[ind], ind, proofs[ind])

        self.files_map[file_name] = {
            "num_parts": CHUNKS_NUMBER,
            "redundant": 3,
            "root_hash": root_hash
        }
        return True, root_hash

    def get_file(self, filename, data_queue):
        for server in self.servers:
            server.push_data(filename, data_queue)
        return self.files_map[filename]

    def build_merkle_tree(self, leaves):
        current_level = [Utils.hash_data(leaf) for leaf in leaves]
        proofs = [[]] * len(leaves)
        cur = 1
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level) - 1, 2):
                left_hash = current_level[i]
                right_hash = current_level[i + 1]
                next_level.append(Utils.hash_concat(left_hash, right_hash))

                # Store proof for both leaves
                for ind in range(i * cur, (i+1) * cur):
                    proofs[ind].append((right_hash, "right"))
                for ind in range((i+1)  * cur, (i+2) * cur):
                    proofs[ind].append((left_hash, "left"))
                    # proofs[i // 2] = [right_hash] + (proofs[i] if proofs[i] else [])
                    # proofs[i // 2] += (proofs[i + 1] if proofs[i + 1] else [])
                    # proofs[i // 2].append(Utils.hash_concat(left_hash, right_hash))

            if len(current_level) % 2 == 1:
                next_level.append(current_level[-1])

            current_level = next_level
            cur *= 2


        return current_level[0], proofs
