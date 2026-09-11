input_file: str = 'output.csv'

with open(input_file) as file:
    lines = file.readlines()

def lzfill(string, width):
    return string[::-1].zfill(width)[::-1]

def lpad(string, width):
    return ' ' * (width - len(string)) + string

def rpad(string, width):
    return string + ' ' * (width - len(string))

table: list[list[str]] = [line.rstrip('\n').split(',') for line in lines[1:]]

for row_index, row in enumerate(table):
    table[row_index][0] = lpad(row[0], 2)

    for col_index, entry in enumerate(row[1:11], start = 1):
        table[row_index][col_index] = ' ' * 5 if entry == '' else entry.zfill(5) 

    for col_index, entry in enumerate(row[11:], start = 11):
        table[row_index][col_index] = lpad(entry, 3)

header: list[str] = ['  '] + [f'  {i}  ' for i in range(10)] + [f' {i} ' for i in range(1, 10)] + ['Ē-7', 'E-7']
table.insert(0, header)

# to .txt
lines: list[str] = [' '.join(row) + '\n' for row in table]
with open('output.txt', 'w') as file:
    file.writelines(lines)

# to .md
lines: list[str] = ['| '+ ' | '.join(row) + ' |\n' for row in table]
lines.insert(1, '|-' * len(table[0]) + '|\n')
with open('output.md', 'w') as file:
    file.writelines(lines)

