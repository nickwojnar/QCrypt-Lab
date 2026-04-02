import numpy as np
import csv

def grayscale_unit_to_int_matrix(grayscale_image):
    int_image = 256*grayscale_image //1

    return int_image

def int_to_binary(N, size=8):
    n = int(N)
    if n ==0:
        return "0"*size
    res=""
    while n>0:
        res = str(n & 1) + res
        n >>= 1

    l = len(res)
    rem = size-l
    res = "0"*rem + res
    return res

def binaryToDecimal(b_string):
    b = int(b_string)
    d, p = 0, 0
    while b:
        d += (b % 10) * (2 ** p)
        b //= 10
        p += 1
    
    return d

def int_matrix_to_bitstring(int_matrix):
    array = int_matrix.flatten()
    bits= ""

    for a in array:
        bits+= int_to_binary(a)
    return bits

def split_string(string, slice_size=8):
    array = []
    string_length = len(string)

    steps = int(string_length/slice_size)

    for i in range(steps):
        left = i*slice_size
        right = (i+1)*slice_size

        array.append(string[left:right])

    return array

def bitstring_to_int_matrix(bit_string):
    string_array = split_string(bit_string,slice_size=8)
    int_array = []
    for i in string_array:
        int_array.append(binaryToDecimal(i))
    
    int_array=np.array(int_array)
    int_matrix = int_array.reshape(320,320)
    return int_matrix

def bit_duplication_string(string,bit_copies=1):
    final_string =""
    for char in string:
        final_string+= char*bit_copies
    
    return final_string

def bit_agreement(bit_dup_substring, keep_array):
    """
    Crude error correction method on bit_dup_substring
    Inputs:
        bit_dup_substring: duplication of a single bit (say 8 copies of a 0), which may have bit-flip errors
        keep_array: array of T/F that determines whether we keep the n-th bit.

    Output:
        final_bit: best guess for the original bit

        e.g. [11110111], [FFFTFFTT] --> 1
    """

    n_keep = 0
    bit_keep_tally = 0
    #cycle over bits
    for i in range(len(bit_dup_substring)):
        if keep_array[i]==1:
            n_keep+=1
            bit_keep_tally+= bit_dup_substring[i]
    
    final_bit = np.round(bit_keep_tally/n_keep)

    return final_bit

def determine_errors(input,received):
    """
    quantify errors
    """
    errors = 0
    for i in range(len(input)):
        if input[i]!=received[i]:
            errors+=1
    
    return errors


def make_received_bit_string(ch1,ch2):
    bit_string = ""
    keep_array = make_keep_array(ch1,ch2)
    for i in range(len(ch1)):
        if keep_array[i]==1:
            if ch1[i]==1:
                bit_string+="1"
            if ch2[i]==1:
                bit_string+="0"
        else:
            bit_string+="9"
    
    return bit_string

def csv_to_int_array(filename):
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append([int(x) for x in row])
    return data

def make_keep_array(ch1_array,ch2_array):
    return ch1_array ^ ch2_array

def write_bitstring_to_csv(bitstring, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(list(bitstring))  # split into individual bits