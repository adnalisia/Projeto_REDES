# Função checksum
def checksum(data):
    # Transforma bytes em bits
    message_bits = format(data[0], 'b')
    # Dividindo em 8 bits
    bytes_parts_list = []    # cria uma lista para as partes em 8 bits
    part_lenght = 8
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
    bits_sum = '00000000'
    for bit_part in bytes_parts_list:
        # soma cada parte com a seguinte
        bits_sum = bin(int(bits_sum, 2) + int(bit_part, 2))[2:]

    # Adicionando o overflow
    if len(bits_sum) > part_lenght:
        # Calcula os bits overflow
        exceed = len(bits_sum) - part_lenght
        # Soma os bits overflow ao resultado sem o overflow
        bits_sum = bin(int(bits_sum[0:exceed], 2)+int(bits_sum[exceed:], 2))[2:]
    # Adiciona zeros à esquerda em caso de soma menor que 8 bits
    if len(bits_sum) < part_lenght:
        bits_sum = '0' * (part_lenght - len(bits_sum)) + bits_sum
        
    final_checksum = complement_1(bits_sum)
    return final_checksum

# Calculando o complemento de 1
def complement_1(new_sum):
  #  print(new_sum)
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
def make_pkt(data, seqnumb):
    byte = data.encode()
    #primeiro fazendo o checksum dos dados
    cks = checksum(byte)
    #criamos o pacote com o id, os dados e o checksum
    pkt = [data, seqnumb, cks]
    sndpkt = str(pkt)
    return sndpkt

#função de receber
def open_pkt(rcvpkt):
    #recebe o pacote encapsulado com mensagem, numéro sequencial e checksum
    rcvpkt = eval(rcvpkt)
    #cria a variavel para os dados
    data = rcvpkt[0]
    byte = data.encode()
    #cria a variavel para o seqnumb
    seqnumb = rcvpkt[1]
    #checksum recebido com a mensagem
    cks_rcv = rcvpkt[2]
    #faz o checksum
    cks = checksum(byte)
    #compara o checksum recebido com o calculado
    if str(cks) == str(cks_rcv):
        #envia os dados e o ack
        return data, seqnumb, 'ACK'
    #caso os checksum's sejam diferentes
    else:
        #envia os dados e o nak
        return data, seqnumb, 'NAK'
