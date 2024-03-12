import socket
import threading
import queue
import functions

class UDPServer:

    def __init__(self, host, port):
        self.host = host # ip do servidor
        self.port = port # porta do servidor
        self.clients = set() # lista de endereços dos clientes
        self.nicknames = {} # lista dos apelidos dos clientes
        self.seqnumberlist = {} # lista dos ultimos seqnumber recebidos
        self.seqnumber = 0 # ultimo seq number enviado
        self.ackok = False # flag para pacote recebido ser um ack
        self.ackflag = False # flag para pacote recebido ser ack/nak
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # cria o socket do server
        self.socket.bind((self.host, self.port)) # binda o endereço com o socket
        print('Aguardando conexão de um cliente')
    
    # função para transmitir mensagens
    def broadcast(self):
        while True:
            try:
                #pega a próxima mensagem a ser envida na fila
                message = self.messages.get() 
                #envia a mensagem para todos
                self.send_to_all(message)
            except:
                pass

    # função para receber mensagens        
    def receive(self):
        while True:
            try:
                # chama a mensagem
                rcvpkt, address = self.socket.recvfrom(1024)
                # recebe a mensagem, seu numero de sequencia e estado
                message, seqnumb, state = functions.open_pkt(rcvpkt.decode())
                # caso a mensagem recebida seja um ACK
                if message == 'ACK':
                    if state == 'ACK':
                        # coloca que a ultima mensagem recebida foi ack
                        self.ackok = True
                        # muda a flag de ack pra avisar que recebeu o ack/nak
                        self.ackflag = True
                # caso a mensagem recebida seja um nak
                elif message == 'NAK':
                    if state == 'ACK':
                        # coloca que a ultima mensagem recebida não foi ack
                        self.ackok = False
                        # muda a flag de ack pra avisar que recebeu o ack/nak
                        self.ackflag = True
                else:
                    # se a mensagem for validada
                    if state == 'ACK':
                        # se a ultima mensagem recebida for diferente da atual
                        if seqnumb != self.seqnumberlist.get(address):
                            self.seqnumberlist[address] = seqnumb # atualiza o seqnumber
                            if message == "bye": # se a mensagem for bye
                                nickname = self.nicknames.get(address) # recupera nickname que está no dicionário com base no address
                                print(f'{nickname} saiu do servidor.') # print no terminal do servidor
                                self.messages.put(f'{nickname} saiu do chat!') # envia mensagem para todos os clientes informando que cliente saiu
                                self.removeclient(address) # remove o cliente de todas as listas
                                self.sndack('FINACK', address, seqnumb) # envia um finack para encerrar a conexão
                            elif message.startswith("hi, meu nome eh "): # se for a mensagem de conexão
                                self.clients.add(address) # adiciona na lista de endereços
                                print(f'Conexão estabelecida com {address}')
                                self.sndack('SYNACK', address, seqnumb) # envia o synack
                                nickname =  message[16:] # estipula o nickname
                                self.nicknames[address] = nickname # adiciona nickname ao dicionário de nicknames com a chave sendo o address
                                self.messages.put(f'{nickname} entrou no chat!') # coloca a mensagem de que fulano entrou no chat na fila
                            else: # se for qualquer outra mensagem
                                self.messages.put(message) # coloca a mensagem na fila                
                                self.sndack('ACK', address, seqnumb) # envia o ack da mensagem
                                print(f'Mensagem recebida de {address}. ACK enviado.')
                    else: # se a mensagem tiver corrompida
                        self.sndack('NAK', address, seqnumb) # manda um nak
                        print(f'Mensagem recebida de {address} corrompida. NAK enviado.')
            except:
                pass
                    
    
    # metodo para remover o cliente de todas as listas
    def removeclient(self, address):
        self.clients.remove(address) # remove cliente da lista de clientes
        del self.seqnumberlist[address] # remove o cliente da lista de seqnumbers
        del self.nicknames[address] # remove o apelido do cliente


    # def usado dentro do broadcasting para enviar a mensagem para todos os clientes
    def send_to_all(self, message):
        self.seqnumber = (self.seqnumber+1)%2
        # para cada cliente na lista de clientes ele envia a mensagem codificada
        for client in self.clients:
            self.sndpkt(message, client, self.seqnumber)

    # função de enviar
    def sndpkt(self, data, client, seqnumber):
        # coloca as flags como falsas
        self.ackflag = False
        self.ackok = False
        # cria o pacote
        sndpkt = functions.make_pkt(data, seqnumber)
        # envia o pacote pro cliente
        self.socket.sendto(sndpkt.encode(), client)
        print(f'Pacote enviado para {client}!')
        # inicia o time
        self.socket.settimeout(1.0)
        # tentar receber o ack
        try:
            # chama a função ack
            flag = self.waitack()
            # se for um NAK
            if not flag:
                # reenvia o pacote
                self.sndpkt(data, client, seqnumber)
                print(f'Erro! Pacote enviado para {client} corrompido, enviando pacote novamente.')
            else:
                # tudo certo, pacote recebido
                print(f'Pacote recebido por {client} com sucesso!')
        # caso não receba dentro do tempo
        except socket.timeout:
            self.sndpkt(data, client, seqnumber)
            print(f'Erro! Timeout, enviando pacote para {client} novamente.')
    
    # função de esperar o ack
    def waitack(self):
        # espera o recebimento de um ack
        while not self.ackflag:
            self.ackflag = False
        # se receber e for NAK
        if self.ackok:
            return True
        # se receber e for ACK
        else:
            return False
    
    # envia o ack
    def sndack(self, data, address, seqnumb):
        # envia ack para o cliente
        sndpkt = functions.make_pkt(data, seqnumb)
        self.socket.sendto(sndpkt.encode(), address)

    # começa a thread de receber mensagens e de enviar mensagens
    def start(self):
        self.messages = queue.Queue() #cria fila de mensagens
        thread1 = threading.Thread(target=self.receive)
        thread2 = threading.Thread(target=self.broadcast)
        thread2.start()
        thread1.start()

# começa o servidor
if __name__ == "__main__":
    server = UDPServer("localhost", 50000)
    server.start()