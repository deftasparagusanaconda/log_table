# at the end, i realized we should actually start from the end counting downwards so some of the code is a bit botched and patched but its 95% the same code as if it were counting upwards

from collections.abc import Iterable
from typing import Callable
from statistics import mean
import pandas as pd

START: int = 999
STEP: int = -1
STOP: int = 99

COLUMN_COUNT: int = 10
FILENAME: str = 'inputs.csv'

# starting from bottom-right
row_index: int = 0
column_index: int = 0

# table[row][column] = entry
table: list[list[float]] = [[None] * COLUMN_COUNT]

def row_density(number: float) -> int:
    'return the number of entries a row should have'
#    return 10
    return round(number)

def count(iterable: Iterable, key: Callable[[float], int] = lambda item: item is not None) -> int:
    return sum(key(item) for item in iterable)

for number in range(START, STOP, STEP):
    number: float = number / 100
    
    table[row_index][column_index] = number
    
    column_index = (column_index + 1) % COLUMN_COUNT
    
    actual_row_entry_count = count(table[row_index])
    expected_row_entry_count = round(mean(row_density(number) for number in table[row_index] if number is not None))
    
    print(row_index, column_index, actual_row_entry_count, expected_row_entry_count, table[row_index])

    if actual_row_entry_count == expected_row_entry_count:
        row_index += 1
        table.append([None] * COLUMN_COUNT)

# magic. delete an unexplainable empty row
del table[-1]
'''
# the first rows which have only one entry technically want their rows filled completely. lets do that.
for index, row in enumerate(table):
    # early exit
    if count(row) != 1:
        continue
    
    # get the only entry in the row
    entry = [entry for entry in row if entry is not None][0]

    table[index] = [round(entry * 1000 + i) / 1000 for i in range(10)][::-1]

for row in table[::-1]:
    print(row[::-1])
'''
lines: list[str] = [','.join('' if entry is None else f'{entry:.3f}' for entry in row[::-1]) + '\n' for row in table]

with open(FILENAME, 'w') as file:
    file.writelines(lines[::-1])

