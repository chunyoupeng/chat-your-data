import random

# Function to return True with a probability of 1/10
def one_in_ten_chance():
    return random.random() < 0.1

# Call the function and print the result
result = one_in_ten_chance()
result

for i in range(10):
    print(one_in_ten_chance())