"""
   COSC 264 Sockets assignment (2017)
   Packet
   Student Name: Robert Loomes, Jake Simpson
   Usercode: rwl29, jsi76
"""

TYPE_DATA = 0
TYPE_ACK = 1

class Packet:
    """Creates the packet to be sent via the 
    Sender/Channel/Reciever connections"""
    
    def __init__(self, packet_type, seqno, data_len, init_data_len, data):
        
        self.magic_no = 0x497E
        self.packet_type = packet_type 
        self.seqno = seqno 
        self.data_len = data_len
        self.init_data_len = init_data_len
        self.data = data
            
    def seqno_check(self):
        if (self.seqno !=  0) and (self.seqno != 1):
            raise ValueError('Seqence number must be restricted to values 0 or 1')
            
    def data_len_check(self):
        if self.data_len < 0 or self.data_len > 512:
            raise ValueError('Data length exeeds 512 bytes (maximum data value)')
            
    def print_packet(self):
        print('Packet seqno: {}'.format(self.seqno))
        print('Packet length: {}'.format(self.data_len))

            
def create_packet(packet_type, seqno, data_len, init_data_len, data):
    """Creates Packet class and calls it's helper functions
    to creck parameter validity"""
    
    packet = Packet(packet_type, seqno, data_len, init_data_len, data)
    packet.seqno_check()
    packet.data_len_check()
    
    return packet
    

                
        

    
        
        
        
        