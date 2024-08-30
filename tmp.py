import zfec

# Number of data shares and total shares (including parity)
data_shares = 6
total_shares = 8
encoder = zfec.Encoder(data_shares, total_shares)

# Data to be encoded
data = b"This is some data we want to protect with erasure coding"

# Ensure data length is a multiple of data_shares by padding if necessary
pad_len = data_shares - (len(data) % data_shares)
padded_data = data + b'\0' * pad_len

# Split the padded data into blocks
block_size = len(padded_data) // data_shares
blocks = [padded_data[i * block_size:(i + 1) * block_size] for i in range(data_shares)]


# Encode the data into shares
shares = encoder.encode(blocks)

# Display the generated shares
print("Generated shares:")
for i, share in enumerate(shares):
    print(f"Share {i + 1}: {share}")

# Simulate losing some shares (e.g., lose 2 shares)
# In this example, we'll lose shares 3 and 4
available_shares = [shares[i] for i in [0, 1 , 2, 5, 6,7 ]]
available_indices = [0, 1 , 2, 5, 6, 7]

# Initialize the decoder
decoder = zfec.Decoder(data_shares, total_shares)

# Decode the data from the available shares
decoded_blocks = decoder.decode(available_shares, available_indices)

# Combine the decoded blocks and remove padding
decoded_data = b''.join(decoded_blocks).rstrip(b'\0')

# Check if the decoded data matches the original data
if decoded_data == data:

    print("Success! The decoded data matches the original.")
else:
    print("Error: The decoded data does not match the original.")
