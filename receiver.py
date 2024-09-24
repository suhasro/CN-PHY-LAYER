#INSTRUCTIONS : START THE EXECUTION OF RECEIVER FEW SECONDS BEFORE THE SENDER SO AS TO RECEIVE ALL THE BITS TRANSMITTED CORRECTLY AND AFTER STOP THE RECEIVER(Ctrl + C) WHEN THE SENDER GETS FINISHED.


import numpy as np
import pyaudio
import math
from scipy.fft import fft

F_0 = 600  # Frequency for bit '0'
F_1 = 900  # Frequency for bit '1'
F_NULL = 1200 # Frequency for bit '#'
BIT_RATE = 15   # Bits per second
FS = 44100     # Sampling rate (samples per second)
DURATION_PER_BIT = 1 / BIT_RATE  # Duration of each bit in seconds
FORMAT = pyaudio.paFloat32
CHANNELS = 1
CHUNK = int(FS * DURATION_PER_BIT)  # Number of samples per bit
epsilon = 30 #for extracting frequencies that got deviated due to noise

def detect_frequency(signal):
    signal_fft = fft(signal)
    freqs = np.fft.fftfreq(len(signal_fft), 1 / FS)
    
    peak_freq = abs(freqs[np.argmax(np.abs(signal_fft))])
    return peak_freq

def frequency_to_bit(frequency):
    if abs(frequency - F_0) < epsilon:
        return '0'
    elif abs(frequency - F_1) < epsilon:
        return '1'
    elif abs(frequency - F_NULL) < epsilon:
        return '#'
    else:
        return None

def receive_signal(): # This function is extracted from ChatGpt
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=FS, input=True, frames_per_buffer=CHUNK)

    print("Receiving signal...")
    received_bits = []

    try:
        while True:
            data = stream.read(CHUNK)

            signal = np.frombuffer(data, dtype=np.float32)
            
            detected_freq = detect_frequency(signal)
            
            bit = frequency_to_bit(detected_freq)
            if bit != None:
                received_bits.append(bit)
            print(f"Received bit: {bit}, {detected_freq}")
    
    except KeyboardInterrupt:
        print("\nStopped receiving.")
    
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    received_bits = ''.join(received_bits)

    i = 0
    start = 0
    end = 0

    while i < len(received_bits): # used to extract the bit string excluding #'s from the transmitted message.
        if received_bits[i] != '#':
            i = i + 1
            continue
        while(received_bits[i] == '#'):
            i = i+1
        start = i
        while(i < len(received_bits) and received_bits[i] != '#'):
            i = i + 1
        end = i
        break

    result = received_bits[start:end]

    return result 

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

def length(final): #Calculating the length of input message
    preamble = final[:5]
    
    preamble_len = int(preamble, 2)
    
    return preamble_len

def data_extract(data): #Extracting data from hamming code
    data_bits = ''
    
    for i in range(1, len(data) + 1):
        if (i & (i - 1)) == 0:
            continue

        data_bits += data[i - 1]
    
    return data_bits

def xor_strings(s1, s2): #Performing xor of two strings
    xor_result = ''
    
    for bit1, bit2 in zip(s1, s2):
        xor_result += '1' if bit1 != bit2 else '0'
    
    return xor_result

def calculate_parity_orgstring(data, r): #Extracting parity of received message
    result = ''
    for i in range(r):
        x = 2 ** i
        y = data[x - 1]
        result += y
    
    return result

def check_parity_bits(data, r): #To Tally the hamming parity bits with data bits
    n = len(data)
    for i in range(r):
        x = 2**i
        parity = 0
        for j in range(1, n + 1):
            if j != x and j & x == x:
                parity = parity ^ int(data[j - 1])
        if int(data[x-1]) != parity :
            return 0
    return 1

def calculate_parity_finstring(data, r): #Calculating parity of final string received
    n = len(data)
    result = ''
    for i in range(r):
        x = 2 ** i
        parity = 0
        for j in range(1, n + 1):
            if j != x and j & x == x:
                parity = parity ^ int(data[j - 1])
        result += str(parity)

    return result

def parity_cal(data): #Calculating parity bit of message
    n = len(data)
    parity = 0
    for i in range(n):
        parity = parity ^ int(data[i - 1])
    
    return str(parity)

final = receive_signal()
print("received message :" + final)
# print(len(final))

codeword_len = length(final)

a = final[5:5+codeword_len]
p = final[5+codeword_len]
b = final[6+codeword_len:]

parity_bits = len(b) - len(a)

even_parity = int(p)

parity_orgstring = calculate_parity_orgstring(b, parity_bits)

parity_finstring = calculate_parity_finstring(b, parity_bits)

for i in range(len(b)):
    even_parity = even_parity ^ int(b[i])

if even_parity == 0:#If even parity is zero it can have 0/2 flips in (b+p)
    #0/2 flips
    if check_parity_bits(b, parity_bits) == 1: #hamming code data bits tally with parity bits extract correct data bits from hamming code
        res = data_extract(b)
        ham_code = insert_hamming_code(res)
        correction = final[:5] + res + parity_cal(ham_code) + ham_code
        print("After correction of transmitted message :" + correction)
        print("correct input bit-string :" + res)

    else: #hamming code data bits doesn't tally with parity bits extract correct data bits from original string a
        #2 bit flips occur in (b+p)
        ham_code = insert_hamming_code(a)
        correction = final[:5] + a + parity_cal(ham_code) + ham_code
        print("After correction of transmitted message :" + correction)
        print("correct input bit-string :" + a)

else:#If even parity is not zero it has 1 flip in (b+p)
    #1 flip in (b+p)
    if check_parity_bits(b, parity_bits) == 1: #hamming code data bits tally with parity bits extract correct data bits from hamming code,bit flip in parity-bit
        res = data_extract(b)
        ham_code = insert_hamming_code(res)
        correction = final[:5] + res + parity_cal(ham_code) + ham_code
        print("After correction of transmitted message :" + correction)
        print("correct input bit-string :" + res)

    else:#hamming code data bits doesn't tally with parity bits, extract wrong data bit position from hamming code
        ans = xor_strings(parity_orgstring,parity_finstring)
        reversed_ans = ans[::-1]
        error_index = int(reversed_ans,2)
        # print(error_index)

        nc = '1' if b[error_index-1] == '0' else '0'
        codeword = b[:error_index - 1] + nc + b[error_index:]

        res = data_extract(codeword)
        ham_code = insert_hamming_code(res)
        correction = final[:5] + res + parity_cal(ham_code) + ham_code
        print("After correction of transmitted message :" + correction)
        print("correct input bit-string :" + res)
