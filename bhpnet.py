import sys
import socket
import getopt
import threading
import subprocess

import os

# define algumas variaveis globais
listen              = False
command             = False
upload              = False
execute             = ""
target              = ""
upload_destination  = ""
port                = 0


def usage():
    print("BHP Net Tool\r\n")
    print("Usage: bhpnet.py -t target_host -p port\n")
    print("""-l --listen                  - listen on [host]:[port] for
                                incoming connections""")
    print("""-e --execute=file_to_run     - execute the given file upon
                                receiving a connection""")
    print("""-c --command                 - initialize a command shell""")
    print("""-u --upload=destination      - upon receiving connection upload a
                                file and write to [destination]\r\n""")
    print("Examples: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e \"cat /etc/passwd\"")
    print("echo 'ABCDFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def client_sender(buffer):
    print("func client_sender() ", target)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # conecta-se ao nosso host-alvo
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode())
        
        while True:
            # agora espera receber dados de volta
            recv_len = 1
            response = b""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
            
                if recv_len < 4096:
                    break

            print(response)

            # espera mais dados de entrada
            buffer = input("")
            buffer += "\n"

            # envia os dados
            client.send(buffer.encode())
    
    except Exception as err:
        print("[*] Exception Exiting.")
        print(err)

        # encerra a conexao
        client.close()


def server_loop():
    global target
    global port
    print("func server_loop() ", target, port)

    # se nao houver nenhum alvo definido, ouviremos todas as interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # dispara uma thread para cuidar de nosso novo client
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    # remove a quebra de linha
    command = command.strip().decode('UTF-8')
    command = str(command)

    # executa o comando e obtem os dados de saida
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except Exception as err:
        print("Failed to execute command.\r\n")
        print('ERRO ', err)

    # envia os dados de saida de volta ao client
    return output


def client_handler(client_socket):
    global upload
    global execute
    global command
    print("func client_handler() ", target)

    # verifica se e upload
    if len(upload_destination):
        print("if upload_destination <---")

        # le todos os bytes e grava em nosso destino
        file_buffer = ""

        # permanece lendo os dados ate que nao haja mais nenhum disponivel
        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

            # agora tentaremos gravar esses bytes
            try:
                file_descriptor = open(upload_destination, "wb")
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                # confirma que gravou o arquivo
                client_socket.send(b"Successfully saved file to %s\r\n" % upload_destination)
            except Exception as err:
                client_socket.send(b"Failed to save file to %s\r\n" % upload_destination)
                print(err)

    # verifica se e comando
    if len(execute):
        # executa o comando
        output = run_command(execute.encode())

        client_socket.send(output)
    
    # entra em outro laco se um shell de comandos foi solicitado
    if command:
        while True:
            # mostra um prompt simples
            client_socket.send(b"<BHP:#> ")

            # agora ficaremos recebendo dados ate vermos um linefeed (tecla enter)

            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # envia de volta a saida do comando
            response = run_command(cmd_buffer)

            # envia de volta a resposta
            client_socket.send(response)


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()
    
    # le as opcoes de linha de comando
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu")
    except getopt.GetoptError as err:
        print(err)
        usage()

    for o,a in opts:
        if o in ["-h", "--help"]:
            usage()
        elif o in ["-l", "--listen"]:
            listen = True
        elif o in ["-e", "--execute"]:
            execute = a
        elif o in ["-c", "--command"]:
            command = True
        elif o in ["-u", "--upload"]:
            upload_destination = a
        elif o in ["-t", "--target"]:
            target = a
        elif o in ["-p", "--port"]:
            port = int(a)
        else:
            assert False, "Unhandled Option"
        
    # iremos ouvir ou simplesmente enviar dados de stdin?
    if not listen and len(target) and port > 0:
        # le o buffer da linha de comando
        # isso causara um bloqueio, portanto envie um CTRL-D ou CTRL-Z no WINDOWS, se nao estiver
        # enviando dados de entrada para stdin
        buffer = sys.stdin.read() # sys.stdin.read()

        # send data off
        client_sender(buffer)

    # iremos ouvir a porta e, potencialmente,
    # faremos upload de dados, executaremos comandos e deixaremos um shell
    # de acordo com as opcoes de linha de comando anteriores
    if listen:
        server_loop()


main()