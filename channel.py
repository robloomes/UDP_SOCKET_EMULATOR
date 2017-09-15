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

SEED = 1 #change for debugging and/or production runs
MAGIC_NO = 0x497E
MAX_BUFF_SIZE = 2**16
MIN_PORT_NUM = 1024
MAX_PORT_NUM = 64000 


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
    
    #All four channel sockets are created and binded
    chan_send_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_send_in.bind(('localhost', chan_send_in_port))
    chan_send_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_send_out.bind(('localhost', chan_send_out_port))
    chan_receive_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_receive_out.bind(('localhost', chan_receive_out_port))
    chan_receive_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_receive_in.bind(('localhost', chan_receive_in_port))
    
    #Connects the channel outogoing sockets to their default recievers
    chan_send_out.connect(('', sender_in_port))
    chan_receive_out.connect(('', receiver_in_port))
    
    #Enters the loop
    channel_helper(chan_send_in, chan_send_out, chan_receive_in, 
         chan_receive_out, p_rate)
    
        
def channel_helper(chan_send_in, chan_send_out, chan_receive_in, 
         chan_receive_out, p_rate):
    """Begins an infinite loop where the Channel sockets can
    await packet input from it's incoming sockets"""
    
    channel_send = 0
    channel_receive = 0
    
    while True:
        expecting, _, _ = select.select([chan_send_in, chan_receive_in], [], [])
        for socket in expecting:
            raw_packet = socket.recv(MAX_BUFF_SIZE)
            packet = pickle.loads(raw_packet)
        
        if (random.random() < 0.1): #implements bit errors 
            packet.data_len += random.uniform(0, 10)                  
        if (random.random() < p_rate) or (packet.magic_no != MAGIC_NO): 
            continue
        if socket == chan_send_in:
            try:
                chan_receive_out.send(pickle.dumps(packet)) 
                channel_send += 1
                print('Channel --> Receiver packet no.{} sent.'.format(channel_send))
            except ConnectionRefusedError:
                print("Channel Program terminated: connection dropped")
                return          
        elif socket == chan_receive_in:
            try:
                chan_send_out.send(pickle.dumps(packet)) #send the packet
                channel_receive += 1
                print('Channel --> Sender packet no.{} sent.'.format(channel_receive))
            except ConnectionRefusedError:
                print("Channel Program terminated: connection dropped")
                return
            
    #break down the program        
    chan_send_in.close()
    chan_send_out.close()
    chan_receive_in.close()
    exit(0)    
         
          
def main(argv):
    random.seed(SEED)
    try:
        chan_send_in = int(argv[1])
        chan_send_out = int(argv[2])
        chan_receive_in = int(argv[3])
        chan_receive_out = int(argv[4])
        sender_in = int(argv[5])
        receiver_in = int(argv[6])
        p_rate = int(argv[7])
    except (IndexError):
        print('Invalid parameters, please provide 7 arguments for processing.')
        return   
    port_list = [chan_send_in, chan_send_out, chan_receive_in, chan_receive_out,
                 sender_in, receiver_in]
    for port in port_list:
        if port < MIN_PORT_NUM or port > MAX_PORT_NUM:
            print('Port numbers must be in the range between 1,024 and 64,000.')
            return    
    
    channel(chan_send_in, chan_send_out, chan_receive_in,
            chan_receive_out, sender_in, receiver_in,
            p_rate)   
       
    
if __name__ == '__main__':
    main(sys.argv)

