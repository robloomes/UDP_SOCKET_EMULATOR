"""
   COSC 264 Sockets assignment (2017)
   Channel Socket
   Student Name: Robert Loomes, Jake Simpson
   Usercode: rwl29, jsi76
"""
import socket
import random
import select
import sys
import pickle


MAGIC_NO = 0x497E
MAX_BUFF_SIZE = 64000 

#channel(1024, 1025,1026,1027,1028,1030,0)
def channel(chan_send_in_port, chan_send_out_port, chan_receive_in_port,
            chan_receive_out_port, sender_in_port, receiver_in_port,
            p_rate):
    """ Reads parameters from command line: four port numbers for channel sockets,
        one port number for sender socket, one port number for reciever socket,
        packet loss rate (0 >= P < 1)
        After creation, the channel program creates and binds all four of it's 
        sockets, and then enters an infinite loop where it will await input from
        it's sockets
    """
    
    #All four channel sockets are created
    chan_send_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_send_in.bind(('localhost', chan_send_in_port))
    chan_send_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_send_out.bind(('localhost', chan_send_out_port))
    chan_receive_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_receive_out.bind(('localhost', chan_receive_out_port))
    chan_receive_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_receive_in.bind(('localhost', chan_receive_in_port))
    
    
    #Binds all 4 sockets
    
    
    
    
    
    #Connects the channel outogoing sockets to their default recievers
    chan_send_out.connect(('localhost', sender_in_port))
    chan_receive_out.connect(('localhost', receiver_in_port))
    
    #Enters the loop
    channel_helper(chan_send_in, chan_send_out, chan_receive_in, 
         chan_receive_out, p_rate)
    
        
def channel_helper(chan_send_in, chan_send_out, chan_receive_in, 
         chan_receive_out, p_rate):
    """Begins an infinite loop where the Channel sockets can
    await packet input from it's incoming sockets"""
    
    while True:
        expecting, _, _ = select.select([chan_send_in, chan_receive_in], [], [])
        for socket in expecting:
            raw_packet = socket.recv(MAX_BUFF_SIZE)
            
            packet = pickle.loads(raw_packet)
        
            
        if (random.random() < p_rate) or (packet.magic_no != MAGIC_NO): #TODO define packet_no
            continue
        elif socket == chan_send_in:
            try:
                chan_receive_out.send(raw_packet)          
            except ConnectionRefusedError:
                print("Channel Program terminated: connection dropped")
                return
            else:
                print(packet)
 
        elif socket == chan_receive_in:
            try:
                chan_send_out.send(raw_packet) #send the packet
            except ConnectionRefusedError:
                print("Channel Program terminated: connection dropped")
            else:
                print(packet)
                  
def main():
    channel(10002,10003,9998,10005,10000,10006,0)
    
    
if __name__ == '__main__':
    #sys.exit(main(sys.argv))
    main()

