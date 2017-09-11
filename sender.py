"""
   COSC 264 Sockets assignment (2017)
   Student Name: Robert Loomes, Jake Simpson
   Usercode: rwl29, jsi76
"""
import os
import select
import socket
import sys
import pickle
from contextlib import closing

from packet import create_packet


"""
2 port numbers for Sin and Sout
1 port number Cs,in
file name
"""

BLOCK_SIZE = int(os.environ.get('SENDER_BLOCK_SIZE', '512'))
TIMEOUT = float(os.environ.get('SENDER_TIMEOUT', '1'))

def sender_function(file_in, sock_in, sock_out):
    """function that has an outer and inner loop. Outer loop prepares a packet
    for packetBuffer. Inner loop sends out the packet buffer then waits and 
    checks the response packet"""
    v_next = 0 
    exit_flag = False
    packet_count = 0
    
    while not exit_flag:
        data = file_in.read(BLOCK_SIZE)
        data_len = len(data)
        
        if data_len > 0:
            packetBuffer = create_packet(TYPE_DATA, v_next, data_len, data)
        else:
            if data_len == 0:
                packetBuffer = create_packet(TYPE_DATA, v_next, data_len)
                exitFlag = True
        
        processing = True
        while processing:
            try:
                pickled = pickle.dumps(packetBuffer)
                sock_out.send(pickled)
                packet_count += 1
            except ConnectionRefusedError:
                print('Connection lost with sender')
                return
            
            ready, _, _ = select.select([sock_in], [], [], TIMEOUT)
            
            if not ready:
                continue
            
            rcvd = sock_in.recv(2**16) #may change due to different number needed
            
            try:
                rcvd_pickle = pickle.load(rcvd)
                trial = create_packet(rcvd)

            except ValueError:
                continue
            if trial.magic_no != 0x497E:
                continue
            if trial.packet_type != TYPE_ACK:
                continue
            if trial.dataLen != 0:
                continue
            if trial.seqno != v_next:
                continue
                
            v_next = 1 - v_next
            processing = False
    
        if exit_flag != True:
            continue
        else:
            print("Number of packets sent in total = {}".format(packet_count))
            exit(0)
                                        
                        
                        
def main(argv):
    """main function for sender program that opens ports for sending"""
    try:
        s_in = int(argv[1])
        s_out = int(argv[2])
        c_s_in = int(argv[3])
        file_name = argv[4]
    except (IndexError, ValueError):
        return 'Usage: {} S_IN S_OUT C_S_IN FILE_NAME'.format(sys.argv[0])
    port_list = [receiver_in, receiver_out, chan_receive_in]
    for port in port_list:
        if port < 1024 or port > 64000:
            print('Port numbers must be in the range between 1,024 and 64,000.')
            return    
    with open(file_name, 'rb') as file_in, \
            closing(socket.socket(type=socket.SOCK_DGRAM)) as sock_in, \
            closing(socket.socket(type=socket.SOCK_DGRAM)) as sock_out:
        sock_in.bind(('localhost', s_in))
        sock_out.bind(('localhost', s_out))
        sock_out.connect(('localhost', c_s_in))
        sender_function(file_in, sock_in, sock_out)
