# Calcula complemento de 1
def complement(n, size):
    comp = n ^ ((1 << size) - 1)
    return '0b{0:0{1}b}'.format(comp, size)

# Soma de verificação


def checksum(origin_port, destiny_port, size):
    first_sum = bin(origin_port+destiny_port)[2:].zfill(16)
    if (len(first_sum) > 16):
        first_sum = first_sum[1:17]
        first_sum = bin(int(first_sum, 2) + 1)[2:].zfill(16)
    second_sum = bin(int(first_sum, 2)+size)[2:].zfill(16)
    if (len(second_sum) > 16):
        second_sum = second_sum[1:17]
        second_sum = bin(int(second_sum, 2) + 1)[2:].zfill(16)
    checksum = complement(int(second_sum, 2), 16)[2:]
    return int(checksum, 2)
