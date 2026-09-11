# MF means main factor (the left 10 columns)
# MD means mean difference (the right 9 columns)

from math import floor, ceil
from math import log10
from statistics import mean
from typing import Any

#def log_round(num):
#    f = floor(num)
#    c = ceil(num)
#    return f if f else c

# parameters. i probably wont use BASE but its there to let you know the context
BASE = 10
RADIX = 10
DIGITS = 5

# ---
# get inputs
# ---

# read file
with open('inputs.csv') as file:
    lines: list[str] = file.readlines()

# inputs[row][column] = entry
inputs: list[list[None | float]] = []

for line in lines:
    entries = line.rstrip('\n').split(',')

    print(entries)

    for index, entry in enumerate(entries):
        entries[index] = None if entry == '' else float(entry)

    inputs.append(entries)

'''
# parse lines
for line in lines:
    # line could be '\t\t1.02\t1.03\t\n'
    
    # remove trailing newline
    line: str = line.rstrip('\n')
    
    # split into ['', '', '1.02', '1.03', '']
    entries: list[str] = line.split('\t')
    
    # extend to 10 entries, cause some lines dont always have trailing tabs
    entries.extend([''] * (10 - len(entries)))

    # entries is all strings. convert to None and float types
    entries: list[None | float] = [None if entry == '' else float(entry) for entry in entries]

    inputs.append(entries)
'''

# show inputs
print('\ninputs:')
for row in inputs:
    print(' '.join('     ' if entry is None else f'{entry:.3f}' for entry in row))

# ---
# calculate actual main factors
# ---

# actual_mfs[row][column] = entry
actual_mfs: list[list[float]] = [[None if entry is None else log10(entry) for entry in row] for row in inputs]

# show actual_mfs
print('\nactual_mfs:')
for row in actual_mfs:
    print(' '.join('       ' if entry is None else f'{entry:.5f}' for entry in row))

# ---
# create table
# ---

table: list[dict[str, None | int | list[None | int] | list[int]]] = [{
    'column index'   : None if row[0] is None else round(row[0] * 10),
    'main factor'    : [None] * 10,
    'mean difference': [None] * 9,
    'error mean'  : None,
    'error max'      : None,
} for i, row in enumerate(inputs)]

# ---
# calculate main factors
# ---

# a main factor is maximally accurate by itself in the case that you want a rough approximation, and you dont want to use the mean differences. that is why only a simple rounding is required for it
# main factor and mean difference trying to numerically maximize precision at the same time causes an optimization problem, which is overkill. and the 'i just need a rough approximation' justification is enough of a reason for me to not do that.
# so main factor is maximally accurate by itself, and mean difference tries its best to work with that

for i, row in enumerate(inputs):
    for j, entry in enumerate(row):
        if entry is None:
            pass
        elif isinstance(entry, float):
            entry: int = round(actual_mfs[i][j] * RADIX ** DIGITS)
        else:
            raise RuntimeError(f'unexpected entry {entry} of type {type(entry)}')
        
        table[i]['main factor'][j] = entry

# show main factors
print('\nmain factors:')
print('\t' + '\t'.join(str(idfk).center(DIGITS) for idfk in range(0, 10)))

for row in table:
    print(('\t' if row['column index'] is None else f"{row['column index']}\t") + '\t'.join(' '*DIGITS if mf is None else str(mf).zfill(DIGITS) for mf in row['main factor']))

# ---
# calculate mean differences
# ---

# a mean difference entry is calculated like this:
# "ah! a user wants to get log(1.001) but we only gave him log(1.00). lets give her an extra constant he can add to her answer to get the result of 1.001"
# "oh, but we need to provide accurate +0.001 results for all main factors in this row. we need to find the best number that takes into account the rounding that the table format caused, and also all the main factors in that row"
# "so say a row had only one main factor 00000 which came from the input 1.00. the +0.001 mean difference for that main factor is: log(input + 0.001) - main factor
# "nice! okay so say the row had two main factors 00000 and 00432 which came from the inputs 1.00 and 1.01. the +0.001 mean difference for that main factor is: mean(log(input1 + 0.001) - main_factor1), log(input2 + 0.001) - main_factor2)
# okay so the formula is:
# entry = mean(log(input_j + 0.001) - main_factor_j for j in uhhidk)

# actual_differences[row][digit] = [difference1, difference2, …] 
actual_differences: list[list[list[float]]] = [[None] * 9 for _ in range(len(inputs))]

for row_index, row in enumerate(table):
    for difference_index, difference_offset in enumerate(range(1, 10)):
        differences: list[float] = []
        
        for column_index, mf in enumerate(row['main factor']):    
            if inputs[row_index][column_index] is None:
                continue
            
            difference = log10(inputs[row_index][column_index] + difference_offset / 1000) - mf / RADIX ** DIGITS
            
            differences.append(difference)
        
        # there should only be as much things in differences as there are in that row's inputs
        assert len(differences) == len([input for input in inputs[row_index] if input is not None])
        
        actual_differences[row_index][difference_index] = differences

# show actual differences
#for row in actual_differences:
#    for differences in row:
#        print(differences)

# store mean differences in table
for row_index, row in enumerate(table):
    for difference_index, differences in enumerate(actual_differences[row_index]):
        row['mean difference'][difference_index] = round(mean(differences) * RADIX ** DIGITS)

# show mean differences

print('\nmean differences:')
print('\t' + '\t'.join(str(idfk).rjust(DIGITS) for idfk in range(1, 10)))
for row in table:
    print(('\t' if row['column index'] is None else f"{row['column index']}\t") + '\t'.join(str(mf).rjust(DIGITS) for mf in row['mean difference']))

# ---
# calculate errors
# ---

# errors are calculated like so:
# "so the table can calculate anything like log(1.001) but how far is it from the actual result? i want a single entry on each row that shows the mean error, and also the max error so i can pin tolerance values on my conversions"
# so we maintain an errors list for each possible value in the log table. 

def lookup(number: int, table = table):
    'perform a lookup on a function table'
    if not isinstance(number, int) or not (1000 <= number < 10000):
        raise ValueError('number must be an integer in [1000, 10000)')

    row = number // 100
    col = (number % 100) // 10
    md = number % 10

    # get the correct row index in the table
    row_index = 0
    while table[row_index]['column index'] != row:
        row_index += 1

    # lookup diagonally
    column_index = 0
    while column_index < col:
        column_index += 1
        row_index += table[row_index]['main factor'][column_index] is None

    return table[row_index]['main factor'][column_index] + (0 if md == 0 else table[row_index]['mean difference'][md - 1])

def table_log(number: float, table = table):
    'calculate log using the table'
    offset = floor(log10(number))
    number = round(number / RADIX ** (offset - 3))
    result = lookup(number, table = table)
    return offset + result / RADIX ** DIGITS

def roundtrip(number, table = table):
    return BASE ** table_log(number, table = table)

# actually calculate them
tablevals: list[float] = [lookup(i) / RADIX ** DIGITS for i in range(1000, 10000)]
actuals: list[float] = [log10(i / 1000) for i in range(1000, 10000)]
errors: list[float] = [tableval - actual for tableval, actual in zip(tablevals, actuals, strict = True)]

ERROR_SCALE = RADIX ** 7

# calculate mean errors and max errors for each row in the table
for row_index, row in enumerate(table):
    row['error mean'] = round(mean(abs(error) for error in errors[10 * row_index: 10 * row_index + 10]) * ERROR_SCALE )
    row['error max'] = ceil(max(abs(error) for error in errors[10 * row_index: 10 * row_index + 10]) * ERROR_SCALE)

# display errors
print('\nerrors:')
for i, row in enumerate(table):
    print(i, row['column index'], row['error mean'], row['error max'], sep = '\t')

# chart error results

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, sosfiltfilt

# cause i hate moving means. they are crude lowpasses. yuck
def lowpass(data, cutoff, fs = 1, order=1):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    sos = butter(order, normal_cutoff, btype='low', output='sos')
    return sosfiltfilt(sos, data)

X = [i/1000 for i in range(1000, 10000)]

plt.plot(X, [abs(error) for error in errors])

for i in [-8, -10]:#range(-6, -12, -2):
    Y = lowpass([abs(error) for error in errors], cutoff=2**i)
    plt.plot(X, Y)

# mean error line
plt.plot([1, 10], [mean(abs(error) for error in errors)] * 2)

plt.show()

# ---
# write table to csv file
# ---

header: list[str] = ['', 'mf0', 'mf1', 'mf2', 'mf3', 'mf4', 'mf5', 'mf6', 'mf7', 'mf8', 'mf9', 'md1', 'md2', 'md3', 'md4', 'md5', 'md6', 'md7', 'md8', 'md9', 'AvgE', 'MaxE']
lines: list[str] = [','.join(header) + '\n', ]

for row in table:
    entries: list[Any] = [row['column index']]
    entries.extend(row['main factor'])
    entries.extend(row['mean difference'])
    entries.append(row['error mean'])
    entries.append(row['error max'])

    lines.append(','.join('' if entry is None else str(entry) for entry in entries) + '\n')

with open('output.csv', 'w') as file:
    file.writelines(lines)

#for i, row in enumerate(range(100, 1000, 10)):
#    for j, column in enumerate(range(0, 10)):
#        inputs[i][j] = (row + column) / 100


#for row_factor, row in enumerate(table, start = 10):
#    for column_factor, column



'daa, if we have mean difference as a convenient way to compress the table on one level, why not have a mean difference of mean difference? a second layer of mean difference lookup'
' - we lose a lot of accuracy. and you can mentally try a two-layer mean difference lookup in a real scenario. it is completely not worth the mental effort. thats why we dont do that.'
