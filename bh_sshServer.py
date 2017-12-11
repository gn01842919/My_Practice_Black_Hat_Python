import socket
import paramiko
import threading
import sys

host_key = paramiko.RSAKey(filename='/root/test_rsa.key')

class Server (paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(selfself, username, password):
        if (username == 'aaron') and (password == 'arera88'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

if len(sys.argv[1:]) != 2:
    print "Usage: ./proxy.py [host] [port]"
    print "Example: ./proxy.py 0.0.0.0 22"
    sys.exit(0)


host = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock.bind((host, ssh_port))
    sock.listen(100)
    print "[+] Listening for connection ...."
    client, addr = sock.accept()
except Exception, e:
    print '[-] Listen failed :'+str(e)
    sys.exit(1)
print '[+] Got a connection!'

try:
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()

    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException as x:
        print '[-] SSH negotiation failed.'

    chan = bhSession.accept(20)
    print '[+] Authenticated!'
    print chan.recv(1024)
    chan.send('Welcome to bh_ssh!')

    while True:
        try:
            command = raw_input("Enter command:").strip('\n')
            chan.send(command)

            if command != 'exit':
                print chan.recv(1024) + '\n'

            else:
                print 'exiting....'
                bhSession.close()
                raise Exception ('exit')

        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:

    print '[-] Caught exception: ' +str(e)
    try:
        bhSession.close()
    except:
        pass

    sys.exit(1)






