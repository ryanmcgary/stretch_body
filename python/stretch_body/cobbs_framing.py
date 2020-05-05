import time
import struct

#Based on COBS.h from
#https://github.com/bakercp/PacketSerial
#MIT License
#Copyright (c) 2017 Christopher Baker https://christopherbaker.net

class CobbsFraming():
    """
    Encoding for communications
    """
    def __init__(self):
        self.packet_marker=0
        self.timeout=.05

    def sendFramedData(self, data, size, serial):
        crc=self.calc_crc(data,size)
        data[size]=(crc>>8)&0xFF
        data[size+1] = crc & 0xFF
        size=size+2
        encoded_data=self.encode(data,size)
        encoded_data.append(0x00)
        serial.write(encoded_data)

    def receiveFramedData(self,buf, serial):
        t_start = time.time()
        rx_buffer=[]
        while ((time.time() - t_start) < self.timeout):
            if (serial.inWaiting() > 0):
                byte_in = struct.unpack('B', serial.read(1))[0]
                if byte_in == self.packet_marker:
                    crc1, nr=self.decode(buf, rx_buffer,len(rx_buffer))
                    crc2=self.calc_crc(buf, nr)
                    return crc1==crc2, nr
                else:
                    rx_buffer.append(byte_in)
        return 0,0

    def calc_crc(self, buf, nr): #Modbus CRC
        crc = 0xFFFF
        for i in range(nr):
            crc ^= buf[i]
            for i in range(8):
                if ((crc & 1) != 0):
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc



    def encode(self,data,size):
        read_index = 0
        write_index = 1
        code_index = 0
        code = 1
        encode_buffer=[0]*2*size
        while (read_index < size):
            if (data[read_index] == 0):
                encode_buffer[code_index] = code
                code = 1
                code_index = write_index
                write_index=write_index+1
                read_index=read_index+1
            else:
                encode_buffer[write_index]=data[read_index]
                read_index=read_index+1
                write_index=write_index+1
                code=code+1
                if (code == 0xFF):
                    encode_buffer[code_index] = code
                    code = 1
                    code_index = write_index
                    write_index=write_index+1
        encode_buffer[code_index] = code
        return encode_buffer[:write_index]

    def decode(self,decode_buffer, data, size):
        #return crc valid, num bytes in decode buffer
        if size==0:
            return 0,0
        read_index=0
        write_index=0
        code =0
        while read_index < size:
            code = data[read_index]
            if (read_index + code > size and code != 1):
                return 0,0
            read_index=read_index+1
            for i in range(1,code):
                decode_buffer[write_index]=data[read_index]
                read_index=read_index+1
                write_index=write_index+1
            if (code != 0xFF and read_index != size):
                decode_buffer[write_index]=0
                write_index=write_index+1
        crc = (decode_buffer[write_index- 2]<<8)|decode_buffer[write_index-1]
        return crc, write_index-2
