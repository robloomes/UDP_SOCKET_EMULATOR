"""
   COSC 264 Sockets assignment (2017)
   Channel Socket
   Student Name: Robert Loomes, Jake Simpson
   Usercode: rwl29, jsi76
"""
 
from contextlib import closing
import socket
import sys
import pickle
from packet import *
import filecmp
import os.path

MAGIC_NO = 0x497E
MIN_PORT_NUM = 1024
MAX_PORT_NUM = 64000 
  
def initialise_receiver(receiver_in_port, receiver_out_port, chan_receive_in_port
                       , file_name, original_file_name):
    """ Takes parameters: two port numbers for the receiver sockets,
        one port number for the channel socket, and the name of the file in 
        which the received file will be stored in.
        After creation, the channel program creates and binds all of it's 
        sockets. It then calls upon receiver_helper() to enter an infinte loop
        where it will wait for incoming packets for writing.
    """    
    
    if os.path.isfile(file_name):
        print ("File name already exists.")
        return
    else:
        file = open(file_name, 'wb') 
    #creates and binds the sockets
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as receiver_in, \
         closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as receiver_out:
        receiver_in.bind(('localhost', receiver_in_port))
        receiver_out.bind(('localhost', receiver_out_port))
        receiver_out.connect(('localhost', chan_receive_in_port))   
        
        receiver_helper(receiver_in, receiver_out, file, file_name, original_file_name)    


      
def receiver_helper(receiver_in, receiver_out, file, file_name, original_file_name):
    """
    Enters the loop where it waits for an incoming packet. If error checks on 
    the received packet are passed the packet data is written to the given out file.
    """
    expected = 0
    packet_ack = 0
    packet_written = 0
    while True:
        packet_pickled = receiver_in.recv(MAX_PORT_NUM)
        try:
            packet = pickle.loads(packet_pickled)
        except ValueError:
            continue
        if packet.packet_type != TYPE_DATA:
            continue
        if packet.data_len > packet.init_data_len: #checks packet for bit errors
            continue
        if packet.seqno != expected:
            ack_pkt = create_packet(TYPE_ACK, packet.seqno, 0, 0, None)
            receiver_out.send(pickle.dumps(ack_pkt))
            packet_ack += 1
            print('Receiver --> Channel ACKNOWLEDGEMENT packet no.{} sent.'.format(packet_ack))
        else:
            ack_pkt = Packet(TYPE_ACK, packet.seqno, 0, 0, None)
            receiver_out.send(pickle.dumps(ack_pkt))
            packet_ack += 1
            print('Receiver --> Channel ACKNOWLEDGEMENT packet no.{} sent.'.format(packet_ack))
            expected = 1 - expected
            if packet.data:
                packet_written += 1
                file.write(packet.data)
                print('Packet no.{} written to file.'.format(packet_written))
            else:
                print("Connection closed")
                file.close()
                if filecmp.cmp(file_name, original_file_name):
                    print("Output file transmitted correctly without error.")
                else:
                    print("Output file is not a match to the original file.")
                break
            
    #break down the program
    file.close()
    receiver_in.close()
    receiver_out.close()
    exit(0)    
    

def main(argv):
    """ Reads parameters from command line for use in other functions. 
    Checks parameters for errors and validity.
    """
    try:
        receiver_in = int(argv[1])
        receiver_out = int(argv[2])
        chan_receive_in = int(argv[3])
        file_name = argv[4]
        original_file_name = argv[5]
    except (IndexError):
        print('Invalid parameters, please provide 5 arguments for processing.')
        return
    port_list = [receiver_in, receiver_out, chan_receive_in]
    for port in port_list:
        if port < MIN_PORT_NUM or port > MAX_PORT_NUM:
            print('Port numbers must be in the range between 1,024 and 64,000.')
            return
       
    #Parameters validated, ready to engage sockets.    
    initialise_receiver(receiver_in, receiver_out, chan_receive_in, file_name, original_file_name)

if __name__ == '__main__':
    main(sys.argv)
