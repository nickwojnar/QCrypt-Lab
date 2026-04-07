import numpy as np

# -------------------------------
# Load CSVs
# -------------------------------
def load_data(init_file, ch1_file, ch2_file):
    init = np.loadtxt(init_file, delimiter=',', dtype=int)
    ch1 = np.loadtxt(ch1_file, delimiter=',')
    ch2 = np.loadtxt(ch2_file, delimiter=',')
    return init, ch1, ch2


# -------------------------------
# Convert counts → bitstring
# -------------------------------
def counts_to_bits(ch1, ch2):
    """
    Returns:
        B_received: array with {0,1,-1}
    """
    B = np.full(len(ch1), -1, dtype=int)

    for i in range(len(ch1)):
        if ch1[i] > ch2[i]:
            B[i] = 1
        elif ch2[i] > ch1[i]:
            B[i] = 0
        else:
            B[i] = -1  # tie → discard

    return B


# -------------------------------
# Sifting + index map
# -------------------------------
def create_sifted_index_arrays(A_repeat, B_received, N_duplicate):
    A_sifted = []
    B_sifted = []
    index_array = []

    for i in range(len(B_received)):
        if B_received[i] != -1:
            A_sifted.append(A_repeat[i])
            B_sifted.append(B_received[i])
            index_array.append(i // N_duplicate)

    return np.array(A_sifted), np.array(B_sifted), np.array(index_array)


# -------------------------------
# Cascade
# -------------------------------
def cascade_correct(A, B, n_passes=4):
    B = B.copy()
    N = len(A)

    def parity(x):
        return np.sum(x) % 2

    def binary_search(indices):
        if len(indices) == 1:
            return indices[0]

        mid = len(indices) // 2
        left = indices[:mid]
        right = indices[mid:]

        if parity(A[left]) != parity(B[left]):
            return binary_search(left)
        else:
            return binary_search(right)

    q = np.mean(A != B)
    k1 = max(8, int(1 / q)) if q > 0 else N

    for p in range(n_passes):
        block_size = k1 * (2 ** p)
        perm = np.random.permutation(N)

        for i in range(0, N, block_size):
            block = perm[i:i + block_size]
            if len(block) == 0:
                continue

            if parity(A[block]) != parity(B[block]):
                err_idx = binary_search(block)
                B[err_idx] ^= 1

    return B, q


# -------------------------------
# Reconstruct original
# -------------------------------
def reconstruct_original(B_sifted, index_array, original_length):
    buckets = [[] for _ in range(original_length)]

    for bit, idx in zip(B_sifted, index_array):
        buckets[idx].append(bit)

    result = np.zeros(original_length, dtype=int)

    for i in range(original_length):
        if len(buckets[i]) == 0:
            result[i] = 0
        else:
            result[i] = int(np.round(np.mean(buckets[i])))

    return result


# -------------------------------
# Full pipeline
# -------------------------------
def run_pipeline(init_file, ch1_file, ch2_file, N_duplicate=16):

    # Load
    A_repeat, ch1, ch2 = load_data(init_file, ch1_file, ch2_file)

    # Infer original length
    N_original = len(A_repeat) // N_duplicate
    A_original = A_repeat[::N_duplicate]

    # Build Bob's received bits
    B_received = counts_to_bits(ch1, ch2)

    # Sift
    A_sifted, B_sifted, index_array = create_sifted_index_arrays(
        A_repeat, B_received, N_duplicate
    )

    # Cascade
    B_corrected, q_initial = cascade_correct(A_sifted, B_sifted, n_passes=12)

    # Reconstruct
    B_final = reconstruct_original(
        B_corrected,
        index_array,
        N_original
    )

    # Final error
    final_error = np.mean(B_final != A_original)

    print("Initial sifted error rate:", q_initial)
    print("Final logical error rate:", final_error)

    return B_final