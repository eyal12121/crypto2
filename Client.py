import os
import queue
import time
import zfec


from Utils import Utils

from reedsolo import RSCodec

class Client:
    def __init__(self, main_server):
        self.main_server = main_server

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


    def recover_data(self, encoded_chunks, k, r):
        rs = RSCodec(r)
        # Combine the available chunks into a single byte string
        available_chunks = b''.join(encoded_chunks)
        # Decode the combined data
        decoded_data = rs.decode(available_chunks)
        return decoded_data

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
        while retrieved < len(retrieved_chunks):
            try:
                # repeat = False
                verified, chunk_data, index = self.verify_chunk(chunks_queue.get(timeout=5), root_hash)
                if verified and index != 1:
                    retrieved_chunks[index] = chunk_data
                    retrieved += 1
                    indices.append(index)
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

        return True, self.reassemble_file(retrieved_chunks[:file_metadata["num_parts"]], output_path)
