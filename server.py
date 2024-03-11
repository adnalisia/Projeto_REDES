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
        self.acktrue = False
        self.ackflag = False
        self.ack = threading.Condition()
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
                    self.sndpkt('SYNACK', address) #envia pacote de estabelecimento de conexão

                try:
                    decoded_message = message.decode() #decodifica mensagem
                    #se cliente estiver se conectando com servidor
                    if decoded_message.startswith("hi, meu nome eh "):
                        nickname = decoded_message[16:]
                        #adiciona nickname ao dicionário de nicknames com a chave sendo o address
                        self.nicknames[address] = nickname
                        self.send_to_all(decoded_message)
                        self.sndpkt('ACK', address)
                    else:
                        if decoded_message == "bye":
                            nickname = self.nicknames.get(address) #recupera nickname que está no dicionário com base no address
                            print(f'{nickname} saiu do servidor.') #print no terminal do servidor
                            self.send_to_all(f'{nickname} saiu do chat!') #envia mensagem para todos os clientes informando que cliente saiu
                            self.removeclient(address)
                            self.sndpkt('FINACK', address)
                        #caso a mensagem recebida seja um ACK
                        elif decoded_message == 'ACK':
                            with self.ack:
                                #atualiza o ultimo seqnumb
                                self.lastack[address] = seqnumb
                                #coloca que a ultima mensagem recebida foi validada
                                self.acktrue = True
                                #muda a flag de ack pra avisar que recebeu o ack
                                self.ackflag = True
                                #avisa ao waitack pra continuar
                                self.ack.notify()
                        #caso a mensagem recebida seja um nak
                        elif decoded_message == 'NAK':
                            with self.ack:
                                #coloca que a ultima mensagem recebida não foi validada
                                self.acktrue = False
                                #muda a flag de ack pra avisar que recebeu o ack
                                self.ackflag = True
                                #avisa ao waitack pra continuar
                                self.ack.notify()
                        else: #se for uma mensagem normal para enviar
                            #envia o ack
                            self.sndpkt('ACK', address)                            
                            #atualiza o ultimo seqnumb recebido
                            self.seqnumber[address] = seqnumb
                            #envia a mensagem para todos
                            self.send_to_all(decoded_message)
                except:
                    pass
            

    
    def receive(self):
        while True:
            #chama a mensagem
            rcvpkt, address = self.socket.recvfrom(1024)
            #recebe a mensagem, seu numero de sequencia e estado
            message, seqnumb, state = functions.open_pkt(rcvpkt.decode())
            #vê se a mensagem não ta corrompida
            if state == 'ACK':
                #checa se o numero de sequencia da mensagem recebida é diferente da ultima, se for coloca a mensagem na fila
                if seqnumb != self.seqnumber.get(address):
                    #envia o ack para o cliente
                    self.sndpkt('ACK', address)
                    #retorna as variaveis
                    self.messages.put((message, address, seqnumb))
                #se for o mesmo seqnumb
                else:
                    #só espera pra receber de novo
                    print('Mensagem repetida descartada.')
            #se a mensagem tiver corrompida, envia um NAK para o cliente
            else:
                self.sndpkt('NAK', address)
    
    #metodo para remover o cliente de todas as listas
    def removeclient(self, address):
        self.clients.remove(address) #remove cliente da lista de clientes
        del self.seqnumber[address] #remove o cliente da lista de seqnumbers
        del self.nicknames[address] #remove o apelido do cliente
        del self.lastack[address] #remove o cliente da lista de acks


    #def usado dentro do broadcasting para enviar a mensagem para todos os clientes
    def send_to_all(self, message):
        #para cada cliente na lista de clientes ele envia a mensagem codificada
        for client in self.clients:
            self.sndpkt(message, client)


    #função de enviar
    def sndpkt(self, data, client):
        self.ackflag = False
        #altera o seqnumb da ultima msg enviada
        self.seqnumber[client] = (self.seqnumber.get(client) +1)//2
        # cria o pacote
        sndpkt = functions.make_pkt(data, self.seqnumber.get(client))
        #envia o pacote pro servidor
        self.socket.sendto(sndpkt.encode(), client)
        #inicia o time
        self.socket.settimeout(1.0)
        #tentar receber o ack
        try:
            self.waitack(data, client)
        #caso não receba dentro do tempo
        except socket.timeout:
            self.sndpkt(data, client)
            print('Erro! Timeout, enviando pacote novamente.')
    
    #função de esperar o ack
    def waitack(self, data, client):
        with self.ack:
            #espera o recebimento de um ack
            while not self.ackflag:
                self.ack.wait()
            #se receber e for NAK
            if not self.acktrue:
                #reenvia o pacote
                self.sndpkt(data, client)
                print('Erro! Pacote enviado corrompido, enviando pacote novamente.')
            #se receber e for ACK
            else:
                print('Pacote enviado foi recebido sem erros pelo cliente.')

    def start(self):
        self.messages = queue.Queue() #cria fila de mensagens
        thread1 = threading.Thread(target=self.receive())
        thread2 = threading.Thread(target=self.broadcast())
        thread3 = threading.Thread(target=self.waitack())
        thread1.start()
        thread2.start()
        thread3.start()

if __name__ == "__main__":
    server = UDPServer("localhost", 50000)
    server.start()