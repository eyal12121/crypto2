import threading

import reedsolo
import Utils

from Server import Server

CHUNKS_NUMBER = 10
REDUNDANT_SIZE = 3


class MainServer:

    def __init__(self):
        self.filesMap = None
        self.servers = [Server() for i in range(CHUNKS_NUMBER + REDUNDANT_SIZE)]

    def add_file(self, file, fileName):
        # Convert data to bytes (assuming data is a string)
        data_bytes = file.encode('utf-8')

        # Create Reed-Solomon encoder with 4 data chunks and 2 redundant chunks
        encoder = reedsolo.RSCodec(REDUNDANT_SIZE)

        # Encode data
        encoded_chunks = encoder.encode(data_bytes)

        # Split encoded data into chunks
        chunk_size = len(encoded_chunks) // (CHUNKS_NUMBER + REDUNDANT_SIZE)
        chunks = [encoded_chunks[i:i + chunk_size] for i in range(0, len(encoded_chunks), chunk_size)]
        root, proofs = self.build_merkle_tree(chunks)
        for ind, server in enumerate(self.servers):
            server.storeData(fileName, chunks[ind], ind,proofs[ind])

        self.filesMap[fileName] = {
            "numberOfparts": CHUNKS_NUMBER,
            "redundent": 3,
            "root": root
        }
        return True

    def get_file(self, filename, dataQueue):
        for server in self.servers:
            server.pushData(filename, dataQueue)
        return self.filesMap[filename]

    def build_merkle_tree(self, leaves):
        current_level = [self.hash_data(leaf) for leaf in leaves]
        proofs = [None] * len(leaves)

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level) - 1, 2):
                left_hash = current_level[i]
                right_hash = current_level[i + 1]
                next_level.append(Utils.Utils.hash_concat(left_hash, right_hash))

                # Store proof for both leaves
                if len(proofs) > 0:
                    proofs[i // 2] = [right_hash] + (proofs[i] if proofs[i] else [])
                    proofs[i // 2] += (proofs[i + 1] if proofs[i + 1] else [])
                    proofs[i // 2].append(Utils.Utils.hash_concat(left_hash, right_hash))

            if len(current_level) % 2 == 1:
                next_level.append(current_level[-1])

            current_level = next_level

        return current_level[0], proofs