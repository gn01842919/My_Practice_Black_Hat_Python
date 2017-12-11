"""

This program (BHP server) listens on the given target and port indicated by the argumnets as shown in usage().

A connected client can be in "shell (command) mode", "upload mode", and "default mode".

The shell mode accepts shell commands as input, executes them, and return the executing results to the client.

The upload will store the content of the send data (which should be the data of the client's standard input) to the given file path and then closes the connection.

The default mode will simply display what the client sends (which should be its standard input).

"""
import sys
import socket
import getopt
import threading
import subprocess

show_info = False 
target = "" #show some unnecessary informaion
port = 9999 #default, no reason...


def usage():
    print "BHP Net Tool (Server)"
    print "Usage: bhpserver.py -t target_host -p port [-s]"
    print "-s --show       ==> Show detail debugging information"
    print "Example:"
    print "bhpserver.py -t 192.168.0.1 -p 5555"
    print "bhpserver.py -p 9999"
    sys.exit(0)



def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(10)
        if(show_info):
            print "[*] Server starts listening (%s:%d)..."%(target,port)
    except :
        print "[*] Failed to bind %s:%d"%(target, port)
    
    
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        if(show_info):
            print "[*] Client %s is in connection..."%str(addr)

        client_thread.start()


def run_command(command):
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "<BHPNET:#>command not found\r\n"

    return output



def client_handler(client_socket):
    
    try:
        
        argstring = client_socket.recv(1024)
        #argstring = argstring.rstrip()
        
    except:
        print "[*] Exception in receiving arguments.\nExiting..."
        client_socket.close()
        return
        
    
    if argstring == "shell": #Can't be "is" !!  "is" compares the id, "==" compares the value
        
        if(show_info):
            print "[*] Client is in shell mode"
        
        client_socket.send("<BHPNet:#>")
        while True:
            
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            
            if cmd_buffer == "$$bhpserver=>exit\n":
                if(show_info):
                    print "[*] Server Exiting..."
                client_socket.send("[*] Closing BHP server...")
                client_socket.close()
                import thread
                thread.interrupt_main()
                #if keyboard interrupt fails to terminate it
                import os
                os._exit(0)
                #sys.exit(0)
            
            if cmd_buffer == "$$bhpclient=>exit\n":
                print "[-] Client is exiting..."
                client_socket.close()
                break
            
            
            response = run_command(cmd_buffer)
            response += "<BHPNet:#>"
            client_socket.send(response)
            
    elif argstring[:6] == "upload":
        
        if(show_info):
            print "[*] Client is in upload mode"
        
        upload_destination = argstring[6:]
        
        if(show_info):
            print "[*] upload destination: %s"%upload_destination
        #receivng the file
        
        client_socket.send("OK")
    
        
        #print "[*] ============================"
        file_buffer = ""
         
        while True:
            
            data = client_socket.recv(1024)
            file_buffer += data
            
            if len(data) < 1024:
                break
                
        #print file_buffer
                
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
            if(show_info):
                print "[*] Successfully saved file to %s\r\n" % upload_destination
            
            client_socket.send("[*] Successfully saved file to %s\r\n" % upload_destination)
        
        except:
            if(show_info):
                print "[*] Failed to save file to %s\r\n" % upload_destination
            
            client_socket.send("[*] Failed to save file to %s\r\n" % upload_destination)
        
        client_socket.close()
        print "[*] Client is exiting..."

    else:
        
        if(show_info):
            print "[*] Client is in default mode"
        
        #client_socket.send("<BHPNet:#>")
        while True:
            
            output = ""
            while True:
                
                data = client_socket.recv(4096)
                output += data
                
                if len(data) < 4096:
                    break
                    
            if(show_info):
                print "[*] The received data is shown below:\n"
            
            print output
            client_socket.send("\n[*] The data is received by the server.\n")
                
def main():
    global port
    global target
    global show_info

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:p:s", ["help", "target", "port", "show"])

    except getopt.GetoptError as err:
        print
        print str(err)
        print
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-s", "--show"):
            show_info = True
        else:
            assert False, "some opts are not handled"
            
    server_loop()


main()
