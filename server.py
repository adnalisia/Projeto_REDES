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
        self.acktrue = False
        self.ackflag = False
        self.ack = threading.Condition()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        print('Aguardando conexão de um cliente')
    
    def broadcast(self):
        
            while not self.messages.empty():
                #desempacota a tupla que contém mensagem e endereço que está na fila de mensagem
                message, address, seqnumb = self.messages.get() #decodifica mensagem
                try:#se for uma mensagem normal para enviar
                    #envia o ack
                    self.sndack('ACK', address, seqnumb)  
                    #envia a mensagem para todos
                    self.send_to_all(message, seqnumb)
                except:
                    pass
            

    
    def receive(self):
        while True:
            #chama a mensagem
            rcvpkt, address = self.socket.recvfrom(1024)
            #recebe a mensagem, seu numero de sequencia e estado
            message, seqnumb, state = functions.open_pkt(rcvpkt.decode())
            #caso a mensagem recebida seja um ACK
            if message == 'ACK':
                if state == 'ACK':
                    with self.ack:
                        #coloca que a ultima mensagem recebida foi validada
                        self.acktrue = True
                        #muda a flag de ack pra avisar que recebeu o ack
                        self.ackflag = True
                        #avisa ao waitack pra continuar
                        self.ack.notify()
            #caso a mensagem recebida seja um nak
            elif message == 'NAK':
                if state == 'ACK':
                    with self.ack:
                        #coloca que a ultima mensagem recebida não foi validada
                        self.acktrue = False
                        #muda a flag de ack pra avisar que recebeu o ack
                        self.ackflag = True
                        #avisa ao waitack pra continuar
                        self.ack.notify()
            else:
                if state == 'ACK':
                    if seqnumb != self.seqnumber[address].get():
                        self.seqnumber[address] = seqnumb
                        if message == "bye":
                            nickname = self.nicknames.get(address) #recupera nickname que está no dicionário com base no address
                            print(f'{nickname} saiu do servidor.') #print no terminal do servidor
                            self.send_to_all(f'{nickname} saiu do chat!') #envia mensagem para todos os clientes informando que cliente saiu
                            self.removeclient(address)
                            self.sndack('FINACK', address, seqnumb)
                        elif message == "connect":
                            self.clients.add(address) #adiciona na lista de endereços
                            print(f'Conexão estabelecida com {address}')
                            self.sndack('SYNACK', address, seqnumb)
                        elif message.startswith("hi, meu nome eh "):
                            nickname =  message[16:]
                            #adiciona nickname ao dicionário de nicknames com a chave sendo o address
                            self.nicknames[address] = nickname
                            self.send_to_all(message, seqnumb)
                            self.sndack('ACK', address, seqnumb)
                            client_port = address[1]
                            client_ip = address[2]
                            self.sndpkt(f'IP.PORT,{client_port}/{client_ip}', address, seqnumb)
                        else:
                            self.messages.put(message, address, seqnumb)
                else:
                    self.sndack('NAK', address, seqnumb)
                    
    
    #metodo para remover o cliente de todas as listas
    def removeclient(self, address):
        self.clients.remove(address) #remove cliente da lista de clientes
        del self.seqnumber[address] #remove o cliente da lista de seqnumbers
        del self.nicknames[address] #remove o apelido do cliente


    #def usado dentro do broadcasting para enviar a mensagem para todos os clientes
    def send_to_all(self, message, seqnumber):
        #para cada cliente na lista de clientes ele envia a mensagem codificada
        for client in self.clients:
            self.sndpkt(message, client, seqnumber)


    #função de enviar
    def sndpkt(self, data, client, seqnumber):
        self.ackflag = False
        # cria o pacote
        sndpkt = functions.make_pkt(data, seqnumber)
        #envia o pacote pro servidor
        self.socket.sendto(sndpkt.encode(), client)
        #inicia o time
        self.socket.settimeout(1.0)
        #tentar receber o ack
        try:
            flag = self.waitack()
            if not flag:
                #reenvia o pacote
                self.sndpkt(data, client, seqnumber)
                print('Erro! Pacote enviado corrompido, enviando pacote novamente.')
            else:
                #tudo certo, pacote recebido
                print('Pacote recebido pelo cliente com sucesso!')
        #caso não receba dentro do tempo
        except socket.timeout:
            self.sndpkt(data, client, seqnumber)
            print('Erro! Timeout, enviando pacote novamente.')
    
    #função de esperar o ack
    def waitack(self):
        with self.ack:
            #espera o recebimento de um ack
            while not self.ackflag:
                self.ack.wait()
            #se receber e for NAK
            if not self.acktrue:
                return False
            #se receber e for ACK
            else:
                return True
    
    def sndack(self, data, address, seqnumb):
        # envia arquivos para o servirdor
        sndpkt = functions.make_pkt(data, seqnumb)
        self.socket.sendto(sndpkt.encode(), address)

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