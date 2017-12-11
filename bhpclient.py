'''

This program (BHP client) can connects to the target (of the specified address and port).

The client can connects to the BHP server in "command (shell) mode", "upload mode", and "default mode" as indicated in usage().

The command mode acts like the command-line shell of the BHP server's machine. The server will accepts the sent commands, and returns the results.

In the upload mode, this program will send the content of the standard input buffer and informs the server to store it to the indicated file name.

In the default mode, this program send the content of the standard input to the server. To pause the typing and send out current stdin buffer, press Control-D.


'''
import sys
import socket
import getopt
import threading
import subprocess


command = False
send_buffer = False
target = ""
upload_destination = ""
port = 0


def usage():
    print "BHP Net Tool (Client)"
    print "Usage: bhpclient.py -t target_host -p port"
    print "-c --command              --> starting command-line shell"
    print "-u --upload=destination   --> uploading the file and show [destination] when connection established"
    print "-d --default              --> simply send contents in the stdin buffer to target"
    print
    print "Note that the arguments may not be used simultaneously."
    print
    print "In command (shell) mode, press Control-C or input \"$$$bhpclient=>exit\" to exit, ",
    print "and input \"$$$bhpserver=>exit\" to close BHP server (closing server with this command is not recommended because it uses \"os._exit()\")"
    print
    print "Examples:"
    print "./bhpclient.py -t 192.168.0.1 --port=5555 -c"
    print "cat local.exe | ./bhpclient.py -t 192.168.0.1 -p 5555 -u=c:\\target.exe"
    print "echo 'Hello' | ./bhpclient.py -t 192.168.11.12 -p 9999"
    print "echo -ne \"GET / HTTP/1.1\\r\\nHost: www.google.com\\r\\n\\r\\n\" | ./bhpclient.py -t www.google.com -p 80"
    print
    
    
    sys.exit(0)

def action():
   
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((target, port))
        print "[-] Successfully connected to %s:%d"%(target,port)
        
    except:
        print "[-] Error connecting to the target (%s:%d)..."%(target,port)
        sys.exit(1)
    
    try:
        if len(upload_destination) > 0:
            print "[-] <upload mode>"
            client.send("upload"+upload_destination)
            
            data = client.recv(8)
            
            stdinbuffer = sys.stdin.read()
            if len(stdinbuffer):
                client.send(stdinbuffer)
            
            print client.recv(128)
        
        elif send_buffer:
            print "[-] <default mode>"
            print "[-] Press CTRL-D to signal EOF..."
            print
            #should send something
            client.send("default")
            stdinbuffer = sys.stdin.read()
            client_sender(client, stdinbuffer)
        
        elif command:
            print "[-] <shell mode>"
            client.send("shell")
            client_sender(client, "")
        else:
            print "[-] Error: Unknown mode"
            client.close()
            
    except socket.error as e:
        #print str(e)
        print "[-] Exception in sending message! \n[-]Exiting..."
        client.close()
        
        
def client_sender(client, stdinbuffer):
    # for shell mode and default mode
    if len(stdinbuffer):
        client.send(stdinbuffer)

    while True:

        recv_len = 1
        response = ""
        while recv_len:

            data = client.recv(4096)
            recv_len = len(data)
            response += data

            if recv_len < 4096:
                break

        print response,#Note there is a comma !
        
        stdinbuffer = ""
        
        while True:
            
            data= sys.stdin.read(4096)
            stdinbuffer += data
            if len(data) < 4096:
                break
        
        #stdinbuffer = raw_input("")
        
        #stdinbuffer += "\n"

        client.send(stdinbuffer)
        
        if stdinbuffer == "$$bhpclient=>exit\n":
            print "[-] Exiting..."
            #client.close()
            return
    
def main():
#    global listen
    global port
    global send_buffer #only send the stdin buffer without doing any other thing. 
                      #Usually the target is not the bhpnet server
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:p:cdu:",
            ["help", "target=", "port=", "command", "default", "upload="])

    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if   o in ("-h", "--help"):
            usage()
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-d", "--default"):
            send_buffer = True
        else:
            assert False, "some opts are not handled"
    
    if len(target) and port > 0:
        
        if not command and len(upload_destination) == 0:
            send_buffer = True
        
        action()
    
    else:
        print "[-] Please specify both the target and the port."
        usage()

main()
