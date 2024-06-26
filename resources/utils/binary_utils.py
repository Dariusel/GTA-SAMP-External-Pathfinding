def split_binary_to_chunks(str, chunkSize=4):
    processed = ''
    
    if str.startswith('0b'):
        str = str[2:]

    for x, i in enumerate(str):
        processed += i

        if (x+1) % chunkSize == 0:
            processed += ' '

    return processed

def flags_data_extractor(flags ,bitA_index, bitB_index): # Ex for link nodes count: bitA_index = 0, bitB_index = 3
    flags_binary = bin(int(flags))
    str_flags_binary = str(flags_binary)[2:].zfill(16) # Convert to string and slice off the initial 0b & Ensure binary is atleast 2bytes (16 digits)

    if bitA_index == 0:
        sliced_str_flags_binary = str_flags_binary[-bitB_index-1:]
    else:
        sliced_str_flags_binary = str_flags_binary[-bitB_index-1:-bitA_index]

    return int(sliced_str_flags_binary, 2)

