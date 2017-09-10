"""
   COSC 264 Sockets assignment (2017)
   Student Name: Robert Loomes
   Usercode: rwl29
"""
import os
import select
import socket
import sys
from contextlib import closing


"""
2 port numbers for Sin and Sout
1 port number Cs,in
file name
"""
BLOCK_SIZE = int(os.environ.get('SENDER_BLOCK_SIZE', '512'))
TIMEOUT = float(os.environ.get('SENDER_TIMEOUT', '1'))

def loop(file_in, sock_in, sock_out):
    v_next = 0
    exit_flag = False
    
    while not exit_flag:
        data = file_in.read(BLOCK_SIZE)
        dataLen = len(data)
        
        if dataLen > 0:
            packetBuffer = Packet(PacketType.data, v_next, data_len, data)
        else:
            if dataLen == 0:
                packetBuffer = Packet(PacketType.data, v_next, data)
                exitFlag = True
        
        exit_flag = not data
        processing = True
        while processing:
            try:
                sock_out.send(packetBuffer.to_bytes())
            except ConnectionRefusedError:
                print('Connection lost with sender')
                return
            ready, _, _ = select.select([sock_in], [], [], TIMEOUT)
            
            if not ready:
                continue
            
            rcvd = sock_in.recv(2**16) #may change due to different number needed
            
            try:
                exploded = Packet.from_bytes(rcvd)

            except ValueError:
                continue
            if exploded.maginco != 0x497E:
                continue
            if exploded.type_ != PacketType.ack:
                continue
            if exploded.dataLen != 0:
                continue
            if exploded.seqno != v_next:
                continue
                
            v_next = 1 - v_next
            processing = False
                                        
                        
                        
def main(argv):
    try:
        s_in = parse_port(argv[1])
        s_out = parse_port(argv[2])
        c_s_in = parse_port(argv[3])
        file_name = argv[4]
    except (IndexError, ValueError):
        return 'Usage: {} S_IN S_OUT C_S_IN FILE_NAME'.format(sys.argv[0])
    with open(file_name, 'rb') as file_in, \
            closing(socket.socket(type=socket.SOCK_DGRAM)) as sock_in, \
            closing(socket.socket(type=socket.SOCK_DGRAM)) as sock_out:
        sock_in.bind(('localhost', s_in))
        sock_out.bind(('localhost', s_out))
        sock_out.connect(('localhost', c_s_in))
        loop(file_in, sock_in, sock_out)
