# MF means main factor (the left 10 columns)
# MD means mean difference (the right 9 columns)

from math import log, floor, ceil
from statistics import mean

BASE = 10
RADIX = 10
DIGITS = 5
COLUMN_COUNT = 10
ERROR_SCALE = -7

# preimages --------------------------------------------------------------------

preimage_MFs: list[list[None | float]] = [[None] * COLUMN_COUNT]

row = 0
col = 0
current_row_entry_count = 0
for number in [x / 100 for x in range(999, 99, -1)]:
    preimage_MFs[row][col] = number
    current_row_entry_count += 1
    
    expected_row_entry_count = round(mean(
        #COLUMN_COUNT # use this if you want a traditional log table
        round(number)
        for number in preimage_MFs[row] 
        if number is not None))
    
    col = (col + 1) % COLUMN_COUNT
    
    if current_row_entry_count >= expected_row_entry_count:
        preimage_MFs.append([None] * COLUMN_COUNT)
        current_row_entry_count = 0
        row += 1

preimage_MFs = [row[::-1] for row in preimage_MFs[-2::-1]]

# row counters -----------------------------------------------------------------

row_counter = 9
row_counters = [
    (row_counter := row_counter + 1)
    if row[0] is not None 
    else None 
    for row in preimage_MFs]

# main factors -----------------------------------------------------------------

rounded_MFs: list[list[None | int]] = [   
    [   round(log(entry,BASE) * RADIX ** DIGITS)
        if entry is not None
        else None
        for entry in row]
    for row in preimage_MFs]

# mean differences -------------------------------------------------------------

rounded_MDs: list[list[float]] = [
    [
        round(mean(   
            log(preimage_MF + difference_offset / 1000, BASE) - rounded_MF / RADIX ** DIGITS
            for preimage_MF, rounded_MF in zip(preimage_MFs_row, rounded_MFs_row)
            if preimage_MF is not None and rounded_MF is not None) * RADIX ** DIGITS)
        for difference_offset in range(1, COLUMN_COUNT)]
    for preimage_MFs_row, rounded_MFs_row in zip(preimage_MFs, rounded_MFs)]

# average and max errors -------------------------------------------------------

def lookup(number: int) -> int:
    'perform a lookup on the log table'
    if not isinstance(number, int) or not (1000 <= number < 10000):
        raise ValueError('number must be an integer in [1000, 10000)')

    row = number // 100
    col = (number % 100) // 10
    md = number % 10

    # get the correct row index in the table
    row_index = 0
    while row_counters[row_index] != row:
        row_index += 1

    # lookup diagonally
    column_index = 0
    while column_index < col:
        column_index += 1
        row_index += rounded_MFs[row_index][column_index] is None

    return rounded_MFs[row_index][column_index] + (0 if md == 0 else rounded_MDs[row_index][md - 1])

def table_log(number: float) -> float:
    'calculate log using the table'
    offset = floor(log(number, BASE))
    number = round(number / RADIX ** (offset - 3))
    result = lookup(number)
    return offset + result / RADIX ** DIGITS

def roundtrip(number):
    return BASE ** table_log(number)

# actually calculate them
tablevals: list[float] = [
    lookup(i) / RADIX ** DIGITS 
    for i in range(1000, 10000)]

actuals: list[float] = [
    log(i / 1000, BASE) 
    for i in range(1000, 10000)]

abs_errors: list[float] = [
    abs(tableval - actual) 
    for tableval, actual in zip(tablevals, actuals, strict = True)]

avg_Es: list[int] = [
    round(mean(abs_errors[row_index: row_index + 10]) / RADIX ** ERROR_SCALE)
    for row_index in range(0, len(abs_errors), 10)]

max_Es: list[int] = [
    ceil(max(abs_errors[row_index: row_index + 10]) / RADIX ** ERROR_SCALE)
    for row_index in range(0, len(abs_errors), 10)]

# export -----------------------------------------------------------------------

table: list[list[str]] = [
    (
        ['' if row_counter is None else str(row_counter)] +
        [   '' if rounded_MF is None else str(rounded_MF).zfill(DIGITS)
            for rounded_MF in rounded_MF_row] +
        [   str(rounded_MD) 
            for rounded_MD in rounded_MD_row] +
        [str(avg_E)] +
        [str(max_E)])
    for row_counter, rounded_MF_row, rounded_MD_row, avg_E, max_E
    in zip(row_counters, rounded_MFs, rounded_MDs, avg_Es, max_Es)]

for row_index, row in enumerate(table):
    table[row_index][0] = str.rjust(row[0], 3)

    for col_index, entry in enumerate(row[1:11], start = 1):
        table[row_index][col_index] = ' ' * 5 if entry == '' else entry.zfill(5) 

    for col_index, entry in enumerate(row[11:], start = 11):
        table[row_index][col_index] = str.rjust(entry, 3)

table.insert(0, (
        [f'E-{DIGITS}'] + 
        [f'  {i}  ' for i in range(10)] + 
        [f' {i} ' for i in range(1, 10)] + ['Ē-7', 'E-7']))

# to .txt
open('log table.txt', 'w').writelines(' '.join(row) + '\n' for row in table)

# to .csv
open('log table.csv', 'w').writelines(','.join(row) + '\n' for row in table)

# to .md
table.insert(1, ['-'*len(entry) for entry in table[0]])
open('log table.md', 'w').writelines('| ' + ' | '.join(row) + ' |\n' for row in table)
del table[0]
