import socket
import threading

#constantes para armazenar IP  e número da porta
HOST = 'localhost'
PORT = 50000

#criação do objeto socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))
clients = []
nicknames = []

# servidor em modo de escuta
server.listen()
print('Aguardando conexão de um cliente')


def broadcast(mensagem):
    for client in clients:
        client.sendall(mensagem)


def handle_connections(client):
    while True:
        data = client.recv(1024)
        #envia mensagem para todos os clientes
        broadcast(data)
        if not data:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} saiu da sala!'.encode('utf-8'))
            nicknames.remove(nickname)
            break


###receber conexão dos clientes###
def receive():
    while True:
        client, address = server.accept()
        print(f'conexão estabelecida com {address}')
        client.send('nickname?'.encode('utf-8'))
        nickname = client.recv(1024)
        clients.append(client)
        nicknames.append(nickname)
        print(f'O nome de usuário do cliente é {nickname}'.encode('utf-8'))
        broadcast(f'{nickname} entrou no chat!'.encode('utf-8'))
        client.send('Você está conectado!'.encode('utf-8'))
        ###executar tarefas paralelas
        thread = threading.Thread(target= handle_connections, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()