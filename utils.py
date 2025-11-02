def read_lines(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            yield line
