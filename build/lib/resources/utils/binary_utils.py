def split_binary_to_chunks(binary, chunkSize=4):
    processed = ''
    
    if binary.startswith('0b'):
        binary = binary[2:]

    for x, i in enumerate(str(binary)):
        processed += i

        if (x+1) % chunkSize == 0:
            processed += ' '

    return processed

def flags_data_extractor(flags ,bitA_index, bitB_index): # Ex for link nodes count: bitA_index = 0, bitB_index = 3    
    flags_binary = bin(int(flags))
    str_flags_binary = str(flags_binary)

    if bitA_index == 0:
        sliced_str_flags_binary = str_flags_binary[-bitB_index-1:]
    else:
        sliced_str_flags_binary = str_flags_binary[-bitB_index-1:-bitA_index]

    if len(sliced_str_flags_binary) == 1:
        return 0 if int(sliced_str_flags_binary) == 0 else 1
    else:
        return int(sliced_str_flags_binary, 2)