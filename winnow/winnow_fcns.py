import numpy as np

class Winnow:
    def __init__(self, raw_key=None, perm_seed: int = None):
        """
        Initializes the Winnow class.

        Args:
            raw_key: BitBuffer containing the sifted key. If None, prints a warning.
            perm_seed: Seed for the random permutation of bits.
        """
        if raw_key is None or perm_seed is None:
            print("Default constructor for Winnow... use other constructor.")
            return

        self._key_string = raw_key
        self._key_string.set_seed(perm_seed)
        self._bits_exposed = 0
        self._net_bits_exposed = 0
        self._setter_locked = False

        # Instance variables initialized in first_pass
        self._syndrome_length = None
        self._block_size = None
        self._num_of_blocks = None
        self._parity_check_matrix = None

    def first_pass(self, permute_bits: bool = False) -> int:
        """
        Prepares for the first pass. Initializes the block size schedule,
        determines the initial block size, syndrome length, and number of blocks,
        and generates the parity-check matrix.

        Args:
            permute_bits: If True, permutes the bits in the key buffer before the pass.

        Returns:
            0 on success
        """
        # For the first pass, always choose a block size of 8
        self._syndrome_length = 3
        self._block_size = 8

        # Does not include an incomplete final block
        self._num_of_blocks = self._key_string.get_length() // self._block_size

        self.create_matrix()

        if permute_bits:
            self._key_string.permute_buffer()

        return 0
    
    def next_pass(self, permute_bits: bool = False) -> int:
        """
        Prepares for the next pass of Winnow. Adjusts the block size according to
        the schedule, creates a new parity check matrix, and updates related values.

        Args:
            permute_bits: If True, permutes the bits in the key buffer between passes.

        Returns:
            0 on success, -1 if the schedule is exhausted
        """
        for i in range(8):
            if self._block_size_schedule[i] > 0:
                self._syndrome_length = i + 3
                self._block_size = 1 << self._syndrome_length
                self._block_size_schedule[i] -= 1
                break
            elif i >= 7:
                # Reached end of schedule with no block choices left
                print("Time to terminate.")
                return -1

        self._num_of_blocks = self._key_string.get_length() // self._block_size

        self.create_matrix()

        if permute_bits:
            self._key_string.permute_buffer()

        return 0
    
    #---------------------------------------------------------------------------------------------------
    #-----------------------------------------------reg utils---------------------------------------------
    #------------------------------------------------------------------------------------------------------
    
    def get_current_key(self, my_buf) -> None:
        """
        Copies the current key stored in _key_string into my_buf.

        Args:
            my_buf: BitBuffer to copy the current key into
        """
        return self._key_string

    def get_current_key_length(self) -> int:
        """
        Returns the length of the current key.
        """
        return self._key_string.get_length()

    def get_bits_exposed(self) -> int:
        """
        Returns the gross number of bits exposed.
        """
        return self._bits_exposed

    def get_net_bits_exposed(self) -> int:
        """
        Returns the net number of bits exposed (gross number - bits discarded).
        """
        return self._net_bits_exposed

    def get_block_size_schedule(self) -> list[int]:
        """
        Returns the block size schedule, with the first element incremented by 1.
        
        Returns:
            List of 8 block size schedule values
        """
        result = [self._block_size_schedule[0] + 1]
        result += self._block_size_schedule[1:8]
        return result

    def set_seed_value(self, seed: int) -> None:
        """
        Sets the seed used for the random permutation of bits.

        Args:
            seed: The seed value to set
        """
        self._key_string.set_seed(seed)

    def get_seed_value(self) -> int:
        """
        Returns the seed used for the random permutation of bits.
        """
        return self._key_string.get_seed()

    def print_matrix(self) -> None:
        """
        Displays the parity check matrix, for debugging.
        """
        print("Parity-Check matrix:")
        for i in range(self._syndrome_length):
            print(" ".join(str(self._parity_check_matrix[i][j]) for j in range(self._block_size)))


    def num_remaining_errors(self, other_buffer) -> int:
        """
        Counts the number of positions where other_buffer and the member key string differ.
        Only used for statistics collection and verification of algorithm effectiveness;
        not used in practice.

        Args:
            other_buffer: BitBuffer containing the key to compare to the member key string

        Returns:
            Number of positions where the two strings do not match
        """
        return sum(
            1 for i in range(self._key_string.get_length())
            if other_buffer.get_bit(i) != self._key_string.get_bit(i)
        )

    def get_num_remaining_passes(self) -> int:
        """
        Returns the number of passes left according to the block schedule.
        Responsible for determining termination of the algorithm.
        """
        return sum(self._block_size_schedule[:8])
    
    #-----------------------------------------------------------------------------------------------------------
    #--------------------------------------------syndrome fcns----------------------------------------------------
    #------------------------------------------------------------------------------------------------------------

    def get_syndrome(self, block_number: int) -> int:
        """
        Calculate the syndrome for a given block number.
        
        Args:
            block_number: The block number for which to calculate the syndrome
            
        Returns:
            The syndrome 
            
        Raises:
            ValueError: If the block number is out of range
        """

        if block_number >= self._num_of_blocks:
            raise ValueError(f"Illegal block number: {block_number}")

        new_syndrome = 0
        base_index = block_number * self._block_size

        for i in range(self._syndrome_length - 1, -1, -1):
            new_syndrome <<= 1
            temp = 0

            # [CHECK LOGIC]
            for j in range(self._block_size):
                print(f"parity check matrix {self._parity_check_matrix[i][j]} of type {type(self._parity_check_matrix[i][j])}")
                print(f"parity check matrix {self._key_string.get_bit(base_index + j)} of type {type(self._key_string.get_bit(base_index + j))}")
                temp ^= self._parity_check_matrix[i][j] & self._key_string.get_bit(base_index + j)

            new_syndrome += temp

        self._bits_exposed += self._syndrome_length
        self._net_bits_exposed += self._syndrome_length

        return new_syndrome


    def get_parities(self, parity_list) -> None:
        """
        Gets the parities for each block and stores them in the provided list.
        The indices of the list correspond to the block number of the parity bit.
        Incomplete final blocks are ignored.

        Args:
            parity_list: List to store the parity bits, indexed by block number
        """
        parity_list.set_length(self._num_of_blocks)

        for i in range(self._num_of_blocks):
            start = i * self._block_size
            end = start + self._block_size - 1

            parity = self._key_string.get_parity(start, end)

            self._bits_exposed += 1
            self._net_bits_exposed += 1

            if parity == 1:
                parity_buffer.set_bit(i)
            else:
                parity_buffer.clear_bit(i)


    def create_matrix(self) -> None:
        """
        Generates the parity check matrix used by Alice for computing syndromes
        and by Bob for correcting errors.
        """
        block_size = (1 << self._syndrome_length) - 1

        # [CHECK LOGIC]
        # self._parity_check_matrix = [
        #     [(j // (1 << i)) & 0x1 for j in range(1, block_size + 1)]
        #     for i in range(self._syndrome_length)
        # ]
        # We use self._block_size directly to ensure the matrix is wide enough
        self._parity_check_matrix = [
            [(j // (1 << i)) & 0x1 for j in range(1, self._block_size + 1)]
            for i in range(self._syndrome_length)
        ]


    def discard_syndrome_bits(self, error_blocks: list[int]) -> None:
        """
        Removes bits at indices of the form 2^j - 1 for the given error blocks.
        These correspond to the linearly independent columns of the parity check matrix.
        Despite appearance, this operation is O(n).

        Args:
            error_blocks: List of block numbers for which to discard syndrome bits
        """
        error_blocks_counter = 0
        new_counter = 0
        old_counter = 0

        for i in range(self._num_of_blocks):
            if error_blocks_counter < len(error_blocks) and i == error_blocks[error_blocks_counter]:
                error_blocks_counter += 1
                power_of_two = 1

                for j in range(self._block_size):
                    if j + 1 == power_of_two:
                        # Skip this bit — it's a syndrome bit (index of form 2^j - 1)
                        power_of_two <<= 1
                        old_counter += 1
                    else:
                        if self._key_string.get_bit(old_counter):
                            self._key_string.set_bit(new_counter)
                        else:
                            self._key_string.clear_bit(new_counter)
                        new_counter += 1
                        old_counter += 1
            else:
                for j in range(self._block_size):
                    if self._key_string.get_bit(old_counter):
                        self._key_string.set_bit(new_counter)
                    else:
                        self._key_string.clear_bit(new_counter)
                    new_counter += 1
                    old_counter += 1

        # Handle any remaining bits after the last full block
        while old_counter < self._key_string.get_length():
            if self._key_string.get_bit(old_counter):
                self._key_string.set_bit(new_counter)
            else:
                self._key_string.clear_bit(new_counter)
            new_counter += 1
            old_counter += 1

        self._key_string.set_length(new_counter)


    #----------------------------------------------------------------------------------------------------------
    # ------------------------------------Alice only functions--------------------------------------------------
    #----------------------------------------------------------------------------------------------------------
    def get_codeword(self, generator):
        return np.dot(self._key_string, generator)



    #----------------------------------------------------------------------------------------------------------
    # ------------------------------------Bob only functions--------------------------------------------------
    #----------------------------------------------------------------------------------------------------------
    def fix_with_syndrome(self, block_number: int, syndrome: int) -> None:
        """
        Used by Bob to correct a single bit error in a block using Alice's syndrome.
        XORs Alice's syndrome with Bob's own syndrome to find the error location,
        then flips the erroneous bit.

        Args:
            block_number: The block containing the error
            syndrome: Alice's syndrome for that block
        """
        my_syndrome = self.get_syndrome(block_number)

        syndrome ^= my_syndrome

        if syndrome == 0:
            # The error was discarded in the parity cleanup
            pass
        else:
            # [CHECK LOGIC]
            self._key_string.flip_bit(block_number * self._block_size + (syndrome - 1))

