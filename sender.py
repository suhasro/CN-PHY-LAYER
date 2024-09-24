#INSTRUCTIONS : ENTER THE INPUT STRING CONTAINING 0's AND 1's,ENTER TWO REAL NUMBERS IN THE RANGE(0,1) AND RUN THE CODE.

import pyaudio
import numpy as np
import math

def to_5bit_binary(n):
    binary_representation = bin(n)[2:]
    
    padded_binary = binary_representation.zfill(5)
    
    return padded_binary

def calculate_parity_bits(data, r):#Calculating the parity bits and inserting in the hamming code bit string
    n = len(data)
    for i in range(r):
        x = 2 ** i
        parity = 0
        for j in range(1, n + 1):
            if j & x == x:
                parity = parity ^ int(data[j - 1])
        data = data[:x - 1] + str(parity) + data[x:]
    return data

def insert_hamming_code(data):#Finding hamming code for a given string
    n = len(data)
    r = 0
   
    while (2 ** r) < (n + r + 1):
        r += 1

    j = 0
    k = 1
    m = len(data)
    result = ''
    for i in range(1, m + r + 1):
        if i == 2 ** j:
            result += '0'
            j += 1
        else:
            result += data[k - 1]
            k += 1

    result = calculate_parity_bits(result, r)
    return result

s = input("Enter a string containing 0's and 1's :")
index1 = input("Enter a real number between 0 and 1 :")
index2 = input("Enter a real number between 0 and 1 :")

a = float(index1)
b = float(index2)
p = 0

hamming = insert_hamming_code(s)

for i in range(len(hamming)):
    p = p^int(hamming[i])

codeword = s + str(p) + hamming #codeword = orgstring + parity-bit + hamming code

preamble = to_5bit_binary(len(s))
# print("preamble: " + preamble)

previous = preamble + codeword
print("previous: " + previous)

if b == 0:
    a = math.ceil(a*len(codeword))
    nc = '1' if codeword[a-1] == '0' else '0'
    codeword = codeword[:a - 1] + nc + codeword[a:]
else:
    a = math.ceil(a*len(codeword))
    b = math.ceil(b*len(codeword))
    nc = '1' if codeword[a-1] == '0' else '0'
    codeword = codeword[:a - 1] + nc + codeword[a:]
    nc = '1' if codeword[b-1] == '0' else '0'
    codeword = codeword[:b - 1] + nc + codeword[b:]

final = preamble + codeword

print("final transmitted message: " + final)

# Below part is extracted from ChatGpt
F_0 = 600
F_1 = 900
F_NULL = 1200
BIT_RATE = 15
FS = 44100

DURATION_PER_BIT = 1 / BIT_RATE
FORMAT = pyaudio.paFloat32
CHANNELS = 1
CHUNK = int(FS * DURATION_PER_BIT)

bit_sequence = "####" + final + "####"

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=FS, output=True, frames_per_buffer=CHUNK)

t = np.linspace(0, DURATION_PER_BIT, int(FS * DURATION_PER_BIT), endpoint=False)


for bit in bit_sequence:
    if bit == '0':
       
        tone = 0.5 * np.sin(2 * np.pi * F_0 * t)
    elif bit == '#':

        tone = 0.5 * np.sin(2 * np.pi * F_NULL * t)
    else:
       
        tone = 0.5 *np.sin(2 * np.pi * F_1 * t)
    
    
    tone = tone.astype(np.float32)
    stream.write(tone.tobytes())


stream.stop_stream()
stream.close()
p.terminate()
