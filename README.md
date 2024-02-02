# Projeto de Rede de Computadores

### Descrição do Projeto

Implementação de comunicação UDP utilizando a biblioteca Socket na linguagem Python, com troca de arquivos em formato de texto (.txt) em pacotes de até
1024 bytes (buffer_size) em um chat de sala única, ou seja, apesar da troca inicial entre os usuários ser em arquivos .txt, elas são exibidas em
linha de comando no terminal de cada um dos clientes conectados à sala.

### Como rodar o programa

1. É necessário ter o Python instalado no computador. Para isso, acesse o _https://www.python.org/downloads/_ e clique na versão mais atualizada do python
2. Baixe a pasta com os arquivos .py contidos neste repósitório. **É ESSENCIAL QUE TODOS OS ARQUIVOS ESTEJAM NA MESMA PASTA**
3. Abra em um compilador a pasta com os arquivos.
4. Inicie **primeiro** o arquivo com nome server.py.
5. Abra um novo terminal para iniciar o arquivo client.py.

**OBS: para criar uma sala com mais de um usuário, siga o passo 4 e abra dois ou mais terminais iniciando o arquivo client.py em cada terminal criado.**

### Bibliotecas utilizadas
- **socket**
-Permite com que cada computador possa realizar diversas operações de comunicação, sem que uma interfira na outra.
- **threading**
-Permite a criação, inicialização e gerenciamento de threads dentro do programa.
- **datetime**
-Permite a utilização e manipulação da hora e data do computador.
- **pathlib**
-Permite a verificação do tamanho em bytes do arquivo.
- **random**
-Permite a criação de números aleátorios.
