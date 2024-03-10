import socket

# Função checksum

def checksum(data):
    # Transforma bytes em bits
    message_bits = bin(int.from_bytes(data, byteorder='big'))[2:]
    # Dividindo em 8 bits
    bytes_parts_list = []   # cria uma lista para as partes em 8 bits
    part_lenght = 8
    # Loop para dividir a mensagem em partes de 8 bits
    while message_bits:
        byte_part = message_bits[0:part_lenght]
        # Adiciona as partes na lista
        bytes_parts_list.append(byte_part)

    # Soma as partes
    for bit_part in bytes_parts_list:
        # soma cada parte com a seguinte
        bits_sum = bin(int(bit_part, 2))[2:]
        return bits_sum

    # Adicionando o overflow
    if len(bits_sum > part_lenght):
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
    return the_checksum

#função de enviar
def rdt_send(data, seqnumb, receiver):
    data = data.encode()
    #primeiro fazendo o checksum dos dados
    cks = checksum(data, len(data))
    #criamos o pacot com o id, os dados e o checksum
    sndpkt = [seqnumb, data, cks]
    #envia o pacote pro destinatario
    socket.sendto(sndpkt, receiver)


#função de receber
def rdt_rcv():
    rcvpkt, sender = socket.recvfrom(1024)
    seqnumb = rcvpkt[0]
    data = rcvpkt[1]
    cks = checksum(data)
    if cks == rcvpkt[2]:
        rdt_send('ACK', seqnumb, sender)
    else:
        rdt_send('NAK', seqnumb, sender)
