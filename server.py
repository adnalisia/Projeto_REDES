import socket
import threading
import queue
from pathlib import Path
import functions

class UDPServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = set()
        self.nicknames = {}
        self.seqnumber = {}
        self.lastack = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print('Aguardando conexão de um cliente')
    
    def broadcast(self):
        while True:
            while not self.messages.empty():
                #desempacota a tupla que contém mensagem e endereço que está na fila de mensagem
                message, address, seqnumb = self.messages.get()

                if address not in self.clients: #se o endereço não estiver na lista de clientes
                    self.clients.add(address) #adiciona na lista de endereços
                    print(f'Conexão estabelecida com {address}')
                    pkt = functions.rdt_send('SYNACK', 0)
                    self.sndpkt(pkt, address)

                try:
                    decoded_message = message.decode() #decodifica mensagem
                    #se cliente estiver se conectando com servidor
                    if decoded_message.startswith("hi, meu nome eh "):
                        nickname = decoded_message[16:]
                        #adiciona nickname ao dicionário de nicknames com a chave sendo o address
                        self.nicknames[address] = nickname
                        sndpkt = functions.rdt_send('ACK', 1)
                        self.send_to_all(decoded_message)
                        self.sndpkt(sndpkt, address)
                        #envia para o cliente seu ip e porta (do cliente)
                        sndpkt = functions.rdt_send(f"{address[0]}/{address[1]}", 0)
                        self.sndpkt(sndpkt, address)
                    else:
                        if decoded_message == "bye":
                            nickname = self.nicknames.get(address) #recupera nickname que está no dicionário com base no address
                            print(f'{nickname} saiu do servidor.') #print no terminal do servidor
                            self.send_to_all(f'{nickname} saiu do chat!') #envia mensagem para todos os clientes informando que cliente saiu
                            self.clients.remove(address) #remove cliente da lista de clientes (deveria remover do dicionário tbm, mas não remove)
                            self.seqnumber.remove(address)
                            self.nicknames.remove(address)
                            self.lastack.remove(address)
                            pkt = functions.rdt_send('FINACK')
                            self.sndpkt(pkt, address)
                        else: #se for uma mensagem normal para enviar
                            #envia a mensagem para todos
                            self.send_to_all(decoded_message)
                except:
                    pass

    #função para receber mensagens
    def receive(self):
        while True:
            #chama a mensagem
            rcvpkt, address = self.socket.recvfrom(1024)
            #recebe a mensagem, seu numero de sequencia e estado
            message, seqnumb, state = functions.rdt_rcv(rcvpkt.decode())
            #vê se a mensagem não ta corrompida
            if state == 'ACK':
                #checa se o numero de sequencia da mensagem recebida é diferente da ultima, se for coloca a mensagem na fila
                if seqnumb != self.lastack[address]:
                    self.messages.put((message,address,seqnumb))
                    self.lastack[address] = seqnumb
            else:
                pkt = functions.rdt_send('NAK', seqnumb)
                self.sndpkt(pkt, address)

    #def usado dentro do broadcasting para enviar a mensagem para todos os clientes
    def send_to_all(self, message):
        #para cada cliente na lista de clientes ele envia a mensagem codificada
        for client in self.clients:
            self.seqnumber[client] = (self.seqnumber +1)//2
            self.sndpkt(message, client)


    #função de enviar
    def sndpkt(self, data, client):
        # envia arquivos para o servirdor
        sndpkt = functions.rdt_send(data, self.seqnumber[client])
        self.socket.sendto(sndpkt.encode(), client)
        self.socket.settimeout(1.0)
        #tentar receber o ack
        try:
            infoconf, _, _, state = self.socket.recvfrom(1024)
            #checa se o ack ta ok
            if state == 'ACK':
                #caso a mensagem enviada esteja corrompido
                if infoconf[1].decode == 'NAK':
                    self.sndpkt(data, client)
                #caso seja um ACK
                else:
                    pass
            #caso o ack esteja corrompido, reenvia
            else:
                self.sndpkt(data, client)
        #caso seja
        except self.socket.timeout:
            self.sndpkt(data, client)

    def start(self):
        self.messages = queue.Queue() #cria fila de mensagens
        thread1 = threading.Thread(target=self.receive)
        thread2 = threading.Thread(target=self.broadcast)
        thread1.start()
        thread2.start()

if __name__ == "__main__":
    server = UDPServer("localhost", 50000)
    server.start()