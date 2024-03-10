import socket

# Calcula complemento de 1
def complement(n, size):
    comp = n ^ ((1 << size) - 1)
    return '0b{0:0{1}b}'.format(comp, size)

# Soma de verificação
def checksum(data, size):
    first_sum = bin(data)[2:].zfill(16)
    if (len(first_sum) > 16):
        first_sum = first_sum[1:17]
        first_sum = bin(int(first_sum, 2) + 1)[2:].zfill(16)
    second_sum = bin(int(first_sum, 2)+size)[2:].zfill(16)
    if (len(second_sum) > 16):
        second_sum = second_sum[1:17]
        second_sum = bin(int(second_sum, 2) + 1)[2:].zfill(16)
    checksum = complement(int(second_sum, 2), 16)[2:]
    return int(checksum, 2)


#função de enviar
def rdt_send(data, seqnumb):
    data = data.encode()
    #primeiro fazendo o checksum dos dados
    cks = checksum(data, len(data))
    #chamar a função do complemento a dois
    cpmt2 = complement(cks)
    #criamos o pacot com o id, os dados e o checksum
    sndpkt = [seqnumb, data, cpmt2]
    return sndpkt


#função de receber
def rdt_rcv():
    rcvpkt, sender = socket.recvfrom(1024)
    seqnumb = rcvpkt[0]
    data = rcvpkt[1]
    cks = checksum(data)
    sum = int(bin(cks+rcvpkt[2]))
    if sum == 0:
        rdt_send('ACK', seqnumb, sender)
    else:
        rdt_send('NAK', seqnumb, sender)
    return data, seqnumb