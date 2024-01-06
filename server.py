import socket

#constantes para armazenar IP  e número da porta
HOST = 'localhost'
PORT = 50000

#criação do objeto socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

# servidor em modo de escuta
s.listen()
print('Aguardando conexão de um cliente')

conexao, endereco = s.accept()
print('Conectado em', endereco)

####troca de mensagens###
while True:
    data = conexao.recv(1024)
    if not data: #quando não houver nada na mensagem
        print('Fechando a conexão')
        conexao.close()
        break
    conexao.sendall(data) #envia de volta pro cliente