from utils.binary_utils import split_binary_to_chunks


while True:
    print('|OPTIONS|')
    print('1 - \'int\' to \'UINT32\'-binary')
    print('2 - \'binary\' to \'int\'')
    selection = int(input('Select an option -> '))

    data = input('> ')
    if selection == 1:
        num_binary_str = str(bin(int(data)))[2:].zfill(20)

        print(f'{split_binary_to_chunks(num_binary_str, 4)}')
        print('9876 5432 1098 7654 3210')

    elif selection == 2:
        num_int = int(data, 2)

        print(f'{num_int}')
