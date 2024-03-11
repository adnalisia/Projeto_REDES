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
                message, address = self.messages.get()

                if address not in self.clients: #se o endereço não estiver na lista de clientes
                    self.clients.add(address) #adiciona na lista de endereços
                    print(f'Conexão estabelecida com {address}')
                    pkt = functions.rdt_send('SYNACK', 0)
                    self.sndpkt(pkt.encode(), address)

                try:
                    decoded_message = message.decode() #decodifica mensagem
                    #se cliente estiver se conectando com servidor
                    if decoded_message.startswith("hi, meu nome eh "):
                        nickname = decoded_message[16:]
                        #adiciona nickname ao dicionário de nicknames com a chave sendo o address
                        self.nicknames[address] = nickname
                        self.send_to_all(decoded_message)
                        self.sndpkt('ACK', address)
                        #envia para o cliente seu ip e porta (do cliente)
                        self.sndpkt(f"{address[0]}/{address[1]}", address)
                    else:
                        if decoded_message == "bye":
                            nickname = self.nicknames.get(address) #recupera nickname que está no dicionário com base no address
                            print(f'{nickname} saiu do servidor.') #print no terminal do servidor
                            self.send_to_all(f'{nickname} saiu do chat!') #envia mensagem para todos os clientes informando que cliente saiu
                            self.removeclient(address)
                            self.sndpkt('FINACK', address)
                        else: #se for uma mensagem normal para enviar
                            #envia a mensagem para todos
                            self.send_to_all(decoded_message)
                except:
                    pass

    #função para receber mensagens
    def receive(self):
        while True:
            message, address = self.rcvpkt()
            self.messages.put((message, address))
    
    def rcvpkt(self):
        #chama a mensagem
        rcvpkt, address = self.socket.recvfrom(1024)
        #recebe a mensagem, seu numero de sequencia e estado
        message, seqnumb, state = functions.rdt_rcv(rcvpkt.decode())
        #vê se a mensagem não ta corrompida
        if state == 'ACK':
            #checa se o numero de sequencia da mensagem recebida é diferente da ultima, se for coloca a mensagem na fila
            if seqnumb != self.seqnumber.get(address):
                self.seqnumber[address] = seqnumb
                self.sndpkt('ACK')
                return message, address
            else:
                self.rcvpkt()
        else:
            self.sndpkt('NAK', address)
    
    #metodo para remover o cliente de todas as listas
    def removeclient(self, address):
        self.clients.remove(address) #remove cliente da lista de clientes (deveria remover do dicionário tbm, mas não remove)
        del self.seqnumber[address] #remove o cliente da lista de seqnumbers
        del self.nicknames[address] #remove o apelido do cliente
        del self.lastack[address] #remove o cliente da lista de acks


    #def usado dentro do broadcasting para enviar a mensagem para todos os clientes
    def send_to_all(self, message):
        #para cada cliente na lista de clientes ele envia a mensagem codificada
        for client in self.clients:
            self.seqnumber[client] = (self.seqnumber.get(client) +1)//2
            self.sndpkt(message, client)


    #função de enviar
    def sndpkt(self, data, client):
        # envia arquivos para o servirdor
        sndpkt = functions.rdt_send(data, self.seqnumber.get(client))
        self.socket.sendto(sndpkt.encode(), client)
        self.socket.settimeout(1.0)
        #tentar receber o ack
        try:
            seqnumb = self.waitack(data, client)
            self.lastack[client] = seqnumb
        #caso seja
        except socket.timeout:
            self.sndpkt(data, client)
    
    def waitack(self, data, client):
        info, _= self.socket.recvfrom(1024)
        infoconf, seqnumb, state = functions.rdt_rcv(info.decode())
        #checa se o ack ta ok
        if state == 'ACK':
            #checa se o numero de sequencia da o ack recebido é diferente do ultimo ack recebido, se não for muda e segue o baile
            if seqnumb != self.lastack.get(client):
                #caso a mensagem enviada esteja corrompido
                if infoconf[1].decode() == 'NAK':
                    self.sndpkt(data, client)
                #caso seja um ACK
                else:
                    return seqnumb
            #caso seja um ack de outro pacote ele volta a esperar o ack
            else:
                self.waitack(data,client)
        #caso o ack esteja corrompido, reenvia
        else:
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