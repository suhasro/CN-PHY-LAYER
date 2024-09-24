import random

short_msg = bin(random.getrandbits(10))[2:].zfill(10)
long_msg = bin(random.getrandbits(20))[2:].zfill(20)

short_err = random.choice(range(1,11,1))/10
long_err1, long_err2 = map(lambda x: x/20, random.sample(range(1,21,1), k=2))

print(f"Short Message: {short_msg}")
print(f"Error: {round(short_err, 2)}")
print("")
print(f"Long Message: {long_msg}")
print(f"Errors: {round(long_err1, 2)} {round(long_err2, 2)}")
