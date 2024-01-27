import string
import random

# input => experiment, database, conc, file sizes

# output => relevant vizs, logs

def generate_rand_bytes(size):
    return bytes(random.choices(range(256), k=size))



# Example usage:
size_in_bytes = 100
byte_sequence = generate_rand_bytes(size_in_bytes)
print(byte_sequence)