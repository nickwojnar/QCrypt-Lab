import random 
import numpy as np


class MockBitBuffer:
    def __init__(self, bits):
        self.bits = list(np.array(bits).astype(int))
        self.seed = None
        self._permutation_history = []
    def get_length(self): return len(self.bits)
    def get_seed(self): return self.seed
    def get_bit(self, i): return self.bits[i]
    def set_bit(self, i): self.bits[i] = 1
    def clear_bit(self, i): self.bits[i] = 0
    def flip_bit(self, i): self.bits[i] = 1 - self.bits[i]
    def set_seed(self, s): self.seed = s
    # def permute_buffer(self): 
    # def permute_buffer(self):
    #     """
    #     Shuffles the bits based on the seed. 
    #     Alice and Bob use the same seed to ensure identical shuffles.
    #     """
    #     if self.seed is None:
    #         raise ValueError("Seed must be set before permutation!")
        
    #     # We use a local generator so we don't mess up other random streams
    #     rng = np.random.default_rng(self.seed)
    #     rng.shuffle(self.bits)
    def permute_buffer(self):
        if self.seed is None:
            raise ValueError("Seed must be set before permutation!")
        
        rng = np.random.default_rng(self.seed)
        indices = np.arange(len(self.bits))
        rng.shuffle(indices)
        
        self.bits = [self.bits[i] for i in indices]
        self._last_permutation = indices 
        self._permutation_history.append(indices)


    def unpermute_all(self):
        """Invert all permutations in reverse order."""
        for indices in reversed(self._permutation_history):
            inverse = np.argsort(indices)
            self.bits = [self.bits[i] for i in inverse]
        self._permutation_history = []  # clear history after inverting

        
    def discard_parity_bits(self, block_size: int, num_blocks: int):
        """Remove the last bit from each block after a Winnow pass."""
        kept = []
        for i in range(num_blocks):
            block_start = i * block_size
            block_end   = block_start + block_size - 1  # exclude last bit
            kept.extend(self.bits[block_start:block_end])
        self.bits = kept

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
