#socket channel
import socket
import random
#channel(1024, 1025,1026,1027,1028,1030,0)
def channel(chan_send_in_port, chan_send_out_port, chan_receive_in_port,
            chan_receive_out_port, sender_in_port, receiver_in_port,
            packet_loss_port):
    """"""
    #check P packet loss, if dropped, go back to start of loop
    #connect()
    
    #all four channel sockets are created
    chan_send_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_send_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_receive_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chan_receive_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    chan_send_in.bind(('localhost', chan_send_in_port))
    chan_send_out.bind(('localhost', chan_send_out_port))
    chan_receive_out.bind(('localhost', chan_receive_out_port))
    chan_receive_in.bind(('localhost', chan_receive_in_port))
    
    #connects the channel outoging sockets to their default recievers
    chan_send_out.connect(('localhost', sender_in_port))
    chan_receive_out.connect(('localhost', receiver_in_port))
    print("helpme")
    
    #TODO select() cs,in  cr,in
    #create loop which runs indefinitely
    #pseudo_random number based on P
    
    
    
