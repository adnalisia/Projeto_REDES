import socket

# Função checksum
def checksum(data):
    # Transforma bytes em bits
    message_bits = bin(int.from_bytes(data, byteorder='big'))[2:]
    # Dividindo em 8 bits
    bytes_parts_list = []
    part_lenght = 8   # cria uma lista para as partes em 8 bits
    j = 8
    i = 0
    # Loop para dividir a mensagem em partes de 8 bits
    while i < len(message_bits) :
        byte_part = message_bits[i:j]
        i = j
        j = j + 8
        # Adiciona as partes na lista
        bytes_parts_list.append(byte_part)

    # Soma as partes
    for bit_part in bytes_parts_list:
        # soma cada parte com a seguinte
        bits_sum = bin(int(bit_part, 2))[2:]
        #return bits_sum

    # Adicionando o overflow
    if len(bits_sum) > part_lenght:
        # Calcula os bits overflow
        exceed = len(bits_sum) - part_lenght
        # Soma os bits overflow ao resultado sem o overflow
        new_sum = bin(int(bits_sum[0:exceed], 2)+int(bits_sum[exceed:], 2))[2:]
    # Adiciona zeros à esquerda em caso de soma menor que 8 bits
    if len(bits_sum) < part_lenght:
        new_sum = '0' * (part_lenght - len(bits_sum)) + bits_sum

    final_checksum = complement_1(new_sum)
    return final_checksum

# Calculando o complemento de 1
def complement_1(new_sum):
    the_checksum = ''
    for bit in new_sum:
        # Troca os 1 por 0
        if bit == '1':
            the_checksum += '0'
        # Troca os 0 por 1
        else:
            the_checksum += '1'
    inteiro = int(the_checksum,2) + 1
    the_checksum = format(inteiro, 'b')
    return the_checksum


#função de enviar
def rdt_send(data, seqnumb):
    data = data.encode()
    #primeiro fazendo o checksum dos dados
    cks = checksum(data)
    #chamar a função do complemento a dois
    cpmt1 = complement_1(cks)
    #criamos o pacot com o id, os dados e o checksum
    pkt = [seqnumb, data, cpmt1]
    sndpkt = str(pkt)
    return sndpkt


#função de receber
def rdt_rcv(rcvpkt):
    rcvpkt = eval(rcvpkt)
    #cria a variavel para o seqnumb
    seqnumb = rcvpkt[0]
    #cria a variavel para os dados
    data = rcvpkt[1]
    #pega o valor da soma
    cks = checksum(data)
    #faz o checksum
    start_number = int(cks, 2) + int(rcvpkt[2], 2)
    binary = bin(start_number)
    i = len(binary) - 8
    sum = binary[i:]
    #checa o checksum
    if sum == 0:
        #envia os dados e o ack
        return data, seqnumb, 'ACK'
    else:
        #envia os dados e o nak
        return data, seqnumb, 'NAK'