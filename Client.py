import queue
import time

from Utils import Utils


class Client:
    def __init__(self, main_server):
        self.main_server = main_server  # Reference to the main server

    def add_file(self, file):
        """
        Add a file to the file system.
        """
        with open(file, "r") as f:
            file_content = f.read()
        return self.main_server.add_file(file_content, file)

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
        return True, self.reassemble_file(retrieved_chunks[:file_metadata["num_parts"]], output_path)
