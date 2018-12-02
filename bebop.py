#!/usr/bin/python3
# Tested on python3.6.5

import string
import random
# Used for choosing which parent to apply majority distribution percentage to
from random import shuffle 
# Used for coding the Levenshtein distance algorithm (used for fitness function)
import numpy as np
# Used to floor percentages for crossover()
import math

# Output: Returns the edit distance between two strings
# source of function - https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
def levenshtein(seq1, seq2):  
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    # Begin with an empty matrix that has the size of the length of the strings
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y
    # Compare strings letter-by-letter row-wise and column-wise.
    for x in range(1, size_x):
        for y in range(1, size_y):
            # If two letters are equal, the new value at [x, y] is the min between the values of positions ([x-1, y] + 1), ([x-1, y-1]), and ([x, y-1] + 1)
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            # Otherwise it is the minimum between the value of position ([x-1, y] + 1), ([x-1, y-1] + 1), and [x, y-1] + 1)
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    #print (matrix) # DEBUG print
    # Return the edit distance which is at the lower right corner of the matrix
    return (matrix[size_x - 1, size_y - 1])

# Output: Returns a unique mixed-case alphabetic string to initially populate input fields
# source of function - https://realpython.com/python-random/
def unique_strings(k: int, ntokens: int,
               pool: str=string.ascii_letters) -> set:
    """Generate a set of unique string tokens.
        k: Length of each token
        ntokens: Number of tokens
        pool: Iterable of characters to choose from
    For a highly optimized version:
    https://stackoverflow.com/a/48421303/7954504
    """
    seen = set()
    # An optimization for tightly-bound loops:
    # Bind these methods outside of a loop
    join = ''.join
    add = seen.add
    while len(seen) < ntokens:
        token = join(random.choices(pool, k=k))
        add(token)
    seen = sorted(seen)
    uniqstr = ""
    for i in seen:
        uniqstr += i 
    return uniqstr

# Generate initial population of 10 inputs populating input fields with random values
# Output: returns a list of 10 unique mixed-case alphabetic inputs (initial population)
def init_population():
    init_population_list = []
    for i in range(0, 10):
        #print("Input [%d]" % i)
        # Randomly generate unique input fields for headers
        host = unique_strings(k=4, ntokens=5)
        agent = unique_strings(k=4, ntokens=5)
        accept = unique_strings(k=4, ntokens=5)
        payload = "GET / HTTP/1.1\r\nHost: " + host + "\r\nUser-Agent: " + agent + "\r\nAccept: " + accept + "\r\n"
        # Add unique input to population
        init_population_list.append(payload)
    return init_population_list

# Determine level of fitness (compare current population to original input and find best / worst input to use as parents)
# Fitness will describe how closely the payload currently compares to the original input
# Metric for "distance between strings" - Levenshtein distance or Edit distance (minimum number of edits needed to transform one string into the other)
# Input: population list
# Output: returns parents as a tuple (best, worst) of the corresponding indexes to be used in crossover step of genetic algorithm to select the inputs
def fitness(get_population):
    lev_distance_list = []
    for input_x in get_population:
        lev_distance_list.append(levenshtein(input_x, "GET / HTTP/1.1\r\nHost: localhost\r\nUser-Agent: Firefox\r\nAccept: */*\r\n"))
    # Get indexes of max and min edit distance values to return the corresponding payloads
    return lev_distance_list.index(max(lev_distance_list)), lev_distance_list.index(min(lev_distance_list))

# Generate new population of 10 inputs via CROSSOVER of 2 parents
# Input: str1 (best) and str2 (worst)
# Output: Returns a new population [list] of 10 payloads
def crossover(father, mother):
    # Randomly choose a parent for majority distribution percentage
    parents = [father, mother]
    [shuffle(parents) for i in range(random.randint(1, 2))]
    # Randomly choose which distribution percentage to apply
    division_choice = random.randint(0, 2)
    if (division_choice == 0):
        # Traits passed will be 80 / 20
        # Get number of chars to take based on percentage of traits passed down
        # BUG or FEATURE?: The percentage is applied to the len of the payload and then applied to each individual input field, crossover() will return payloads greater in len than initial inputs
        maj_percentage = int(math.floor(0.4 * len(parents[0])))
    elif (division_choice == 1):
        # Traits passed will be 60 / 40
        maj_percentage = int(math.floor(0.3 * len(parents[0])))
    elif (division_choice == 2):
        # Traits passed will be 50 / 50
        maj_percentage = int(math.floor(0.2 * len(parents[0])))
    min_percentage = int(math.floor(0.5 * len(parents[1]))) - maj_percentage

    # Generate new population of 10
    new_population = []
    for x in range(0, 10):
        # Parse out input fields
        # BUG: This parsing is flawed if additional "\r\n" or " " are inserted via mutation
        ### Parent 0
        each_line_x = parents[0].split("\r\n")
        request_list_x = []
        # Split by spaces and append to request_list_x
        for i in each_line_x:
            request_list_x.append(i.split())

        ### Parent 1
        each_line_y = parents[1].split("\r\n")
        request_list_y = []
        for i in each_line_y:
            request_list_y.append(i.split())

        # Modify input fields
        for i in range(1, len(request_list_x) - 1):
            new_field = ""
            # Generate new input field with bytes obtained randomly out-of-order
            tmp_str_parent_zero = str(request_list_x[i][1])
            tmp_str_parent_one = str(request_list_y[i][1])
            # Concatenate bytes obtained from majority
            for j in range(0, maj_percentage):
                new_field += tmp_str_parent_zero[random.randint(0, len(tmp_str_parent_zero) - 1)]
            # Concatenate bytes obtained from minority
            for j in range(0, min_percentage):
                new_field += tmp_str_parent_one[random.randint(0, len(tmp_str_parent_one) - 1)]
            # Update the input field
            request_list_x[i][1] = new_field
        # Concatenate new final payload
        new_payload = ""
        for line in request_list_x:
            # If array is not empty
            if line:
                #print("line=",line)
                new_payload += ' '.join(line) + "\r\n"
        # Add new payload to the new population
        new_population.append(new_payload) 
    return new_population

# Mutate one of the children randomly with one of the possible mutations:
# Possible mutations:
#     1. Decrease length - remove bytes
#     2. Increase length - add bytes
#     3. Make an input field an empty string
#     4. Change a random byte to a NULL byte
#     5. Change a random byte to a new-line char
#     6. Change a random byte to a semicolon
#     7. Change a random int to a MAXINT
#     8. Change a random int to a MININT
#     9. Flip the sign of a random int
#    10. Insert format code %s, %n, or %x
#    11. Flip a random bit TODO
#    12. Flip every bit in a random byte TODO
def mutate(get_payload):
    # Randomly choose a mutation
    chooseMutation = random.randint(1, 10)
    print("\x1b[0;34;40m" + "Mutation #" + str(chooseMutation) + "\x1b[0m")

    # Randomly choose an input field
    chooseField = random.randint(2, 3)
 
    # Parse request line into tokens with "\r\n"; understandably this parsing is flawed
    each_line = get_payload.split("\r\n")
    request_list = []
    for i in each_line:
        request_list.append(i.split())

    # Modify chosen input field with a single mutation
    for i in range(1, chooseField):
        chooseRandByte = random.randint(1, len(request_list[i][1]) - 1)
        new_field = ""
        # Get char-by-char of an input field
        for c in range(0, len(request_list[i][1])):
            if chooseMutation == 3:
                new_field += " "
            elif c == chooseRandByte:
                # Insert mutated byte
                if chooseMutation == 1:
                    new_field += ""
                if chooseMutation == 2:
                    new_field += "AAAA"
                if chooseMutation == 4:
                    new_field += "\x00"
                if chooseMutation == 5:
                    new_field += "\n"
                if chooseMutation == 6:
                    new_field += ";"
                if chooseMutation == 7:
                    new_field += "\xFF\xFF\xFF\x7F"
                if chooseMutation == 8:
                    new_field += "\x00\x00\x00\x80"
                if chooseMutation == 9:
                    new_field += "\xFF"
                if chooseMutation == 10:
                    chooseFormat = random.randint(0, 2)
                    if chooseFormat == 0:
                        new_field += "%s"
                    if chooseFormat == 1:
                        new_field += "%n"
                    if chooseFormat == 2:
                        new_field += "%x"
            else:
                new_field += request_list[i][1][c]
        # Update request_list with new input field
        request_list[i][1] = new_field
        
    # Concatenate new final payload
    mutant_payload = ""
    for line in request_list:
        # If array is not empty
        if line:
            mutant_payload += ' '.join(line) + "\r\n"
    return mutant_payload
