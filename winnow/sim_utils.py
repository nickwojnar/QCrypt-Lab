import random 
import numpy as np


class MockBitBuffer:
    def __init__(self, bits):
        self.bits = list(bits)
        self.seed = None
    def get_length(self): return len(self.bits)
    def get_bit(self, i): return self.bits[i]
    def set_bit(self, i): self.bits[i] = 1
    def clear_bit(self, i): self.bits[i] = 0
    def flip_bit(self, i): self.bits[i] = 1 - self.bits[i]
    def set_seed(self, s): self.seed = s
    def permute_buffer(self): pass # Simplified for test

# def simulate_error(key, rng, ber=0.25, N=10):
#     mask = (rng.random(size=N) < ber).astype(int)
    
#     cooked_key = key ^ mask
    
#     return cooked_key

def simulate_error(key_buffer, rng, ber=0.25):
    # 1. Get the actual length from the buffer
    N = key_buffer.get_length()
    
    # 2. Generate the error mask (1 means flip, 0 means stay)
    mask = (rng.random(size=N) < ber).astype(int)
    
    # 3. Apply the mask to the buffer
    for i in range(N):
        if mask[i] == 1:
            key_buffer.flip_bit(i)
    
    return key_buffer # Returns the modified buffer object
