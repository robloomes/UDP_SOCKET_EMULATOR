"""
   COSC 264 Sockets assignment (2017)
   Student Name: Robert Loomes, Jake Simpson
   Usercode: rwl29, jsi76
   September 2017
"""
import os
import select
import socket
import sys
import pickle
from contextlib import closing
from packet import *

BUFF_SIZE = 2**16
BLOCK_SIZE = int(os.environ.get('SENDER_BLOCK_SIZE', '512'))
TIMEOUT = float(os.environ.get('SENDER_TIMEOUT', '1'))

def sender_function(file_in, sender_in, sender_out):
    """Function that has an outer and inner loop. Outer loop prepares a packet
    for packetBuffer. Inner loop sends out the packet buffer then waits and 
    checks the response packet."""

    var_next = 0 
    exit_flag = False
    packet_count = 0
    
    while not exit_flag:
        data = file_in.read(BLOCK_SIZE) #reads data from file up to the block size
        data_len = len(data)
        if data_len > 0:
            packetBuffer = create_packet(TYPE_DATA, var_next, data_len, data)
        else:
            if data_len == 0:
                packetBuffer = create_packet(TYPE_DATA, var_next, data_len, None)
                exit_flag = True
        #a data packet is created and ready for sending
        packet_processing = True
        while packet_processing:
            try:
                pickled = pickle.dumps(packetBuffer) #converts data to a bytes object
                sender_out.send(pickled) #packet is sent
                packet_count += 1
            except ConnectionRefusedError:
                print('Connection lost with sender.')
                return
            
            ready, _, _ = select.select([sender_in], [], [], TIMEOUT)
            if not ready:
                continue
            
            rcvd = sender_in.recv(BUFF_SIZE) #may change due to different number needed
            #port is ready to receive any aknowledment packets that may arrive
            try:
                rcvd_pickle = pickle.loads(rcvd) #assumes that any received packets would be in byte format
                trial = rcvd_pickle
            except ValueError:
                continue
                  
            if trial.magic_no != 0x497E:
                continue
            if trial.packet_type != TYPE_ACK:
                continue
            if trial.data_len != 0:
                continue
            if trial.seqno != var_next:
                continue
                
            var_next = 1 - var_next
            packet_processing = False
    
        if exit_flag != True:
            continue
        else:
            print("Number of packets sent in total = {}".format(packet_count))
        break
    
    #break down the program
    file_in.close()
    sender_in.close()
    sender_out.close()
    exit(0)
                                        
                        
                        
def main(argv):
    """Main function for sender program that creates/binds ports for sending.
    Error checks parameters and port numbers."""
    try:
        sender_in = int(argv[1])
        sender_out = int(argv[2])
        chan_send_in = int(argv[3])
        file_name = argv[4]
    except (IndexError, ValueError):
        return 'Usage: {} S_IN S_OUT C_S_IN FILE_NAME'.format(sys.argv[0])
    port_list = [sender_in, sender_out, chan_send_in]
    for port in port_list:
        if port < 1024 or port > 64000:
            print('Port numbers must be in the range between 1,024 and 64,000.')
            return    
    with open(file_name, 'rb') as file_in, \
            closing(socket.socket(type=socket.SOCK_DGRAM)) as sock_in, \
            closing(socket.socket(type=socket.SOCK_DGRAM)) as sock_out:
        sock_in.bind(('localhost', sender_in))
        sock_out.bind(('localhost', sender_out))
        sock_out.connect(('localhost', chan_send_in))
        sender_function(file_in, sock_in, sock_out)
        
if __name__ == '__main__':
    #sys.exit(main(sys.argv))
    main(sys.argv)
