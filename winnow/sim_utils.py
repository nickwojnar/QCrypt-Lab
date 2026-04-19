import random 
import numpy as np

class MockBitBuffer:
    def __init__(self, bits, seed=None):
        self.bits = list(np.array(bits).astype(int))
        self.seed = seed
        self._permutation_history = []
        
        # Initialize the internal RNG property
        self.rng = np.random.default_rng(seed)

    def set_seed(self, s):
        """Updates the seed and resets the internal RNG."""
        self.seed = s
        self.rng = np.random.default_rng(s)

    def get_length(self): return len(self.bits)
    def get_bit(self, i): return self.bits[i]
    def set_bit(self, i): self.bits[i] = 1
    def clear_bit(self, i): self.bits[i] = 0
    def flip_bit(self, i): self.bits[i] = 1 - self.bits[i]

    def permute_buffer(self):
        """Shuffles the bits using the internal RNG."""
        # Using the internal self.rng ensures consistency
        indices = np.arange(len(self.bits))
        self.rng.shuffle(indices)
        
        self.bits = [self.bits[i] for i in indices]
        self._permutation_history.append(indices)
# class MockBitBuffer:
#     def __init__(self, bits):
#         self.bits = list(np.array(bits).astype(int))
#         self.seed = None
#         self._permutation_history = []
#     def get_length(self): return len(self.bits)
#     def get_seed(self): return self.seed
#     def get_bit(self, i): return self.bits[i]
#     def set_bit(self, i): self.bits[i] = 1
#     def clear_bit(self, i): self.bits[i] = 0
#     def flip_bit(self, i): self.bits[i] = 1 - self.bits[i]
#     def set_seed(self, s): self.seed = s
#     # def permute_buffer(self): 
#     # def permute_buffer(self):
#     #     """
#     #     Shuffles the bits based on the seed. 
#     #     Alice and Bob use the same seed to ensure identical shuffles.
#     #     """
#     #     if self.seed is None:
#     #         raise ValueError("Seed must be set before permutation!")
        
#     #     # We use a local generator so we don't mess up other random streams
#     #     rng = np.random.default_rng(self.seed)
#     #     rng.shuffle(self.bits)
#     def permute_buffer(self):
#         if self.seed is None:
#             raise ValueError("Seed must be set before permutation!")
        
#         rng = np.random.default_rng(self.seed)
#         indices = np.arange(len(self.bits))
#         rng.shuffle(indices)
        
#         self.bits = [self.bits[i] for i in indices]
#         self._last_permutation = indices 
#         self._permutation_history.append(indices)


    def unpermute_all(self):
        """Invert all permutations in reverse order."""
        for indices in reversed(self._permutation_history):
            # The key is currently length L. 
            # The shuffle map 'indices' was created for length N (where N > L).
            # We need to find where the REMAING bits go.
            
            current_len = len(self.bits)
            
            # We only take the part of the shuffle map that corresponds 
            # to the bits we didn't discard.
            active_map = indices[:current_len]
            
            # Invert the mapping
            inverse = np.argsort(active_map)
            
            # Reorder
            self.bits = [self.bits[i] for i in inverse]
            
        self._permutation_history = []
    def discard_parity_bits(self, block_size: int, num_blocks: int):
        """Remove the last bit from each block after a Winnow pass."""
        kept = []
        for i in range(num_blocks):
            block_start = i * block_size
            block_end   = block_start + block_size - 1  # exclude last bit
            kept.extend(self.bits[block_start:block_end])
        self.bits = kept

    def set_length(self, new_length):
        """Truncates the bit list to the specified length."""
        self.bits = self.bits[:new_length]
    def set_rng(self, rng_instance):
        """
        Injects an external NumPy random generator.
        Allows Alice and Bob to share a synchronized RNG object.
        """
        if not isinstance(rng_instance, (np.random.Generator, np.random.RandomState)):
            raise TypeError("rng_instance must be a numpy random Generator or RandomState")
        
        self.rng = rng_instance
    def get_seed(self):
        """Returns the seed currently associated with this buffer."""
        return self.seed

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

