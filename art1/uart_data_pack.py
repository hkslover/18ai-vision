import struct

# data_type ,_data
# 0        有框目标板点坐标信息：tuple
# 1        日志信息：str

def pack_data(data_type,_data):
    data = bytearray()
    if(data_type == 0):
        for point in _data:
            data += struct.pack('!BB', point[0], point[1])
        data_len = len(data) + 1  # 1 byte for type
        header = bytearray([0xAA, data_len, 0x00])
        checksum = 0 ^ 0x00 #这里的0x00是串口协议的type
        for byte in data:
            checksum ^= byte
        footer = bytearray([checksum, 0x55])
        return header + data + footer
    elif(data_type == 1):
        data += _data.encode("utf-8")
        data_len = len(data) + 1  # 1 byte for type
        header = bytearray([0xAA, data_len, 0x01])
        checksum = 0 ^ 0x01
        for byte in data:
            checksum ^= byte
        footer = bytearray([checksum, 0x55])
        return header + data + footer
    elif(data_type == 2):
        # 识别种类数据打包
        data_len = 1 + 1  # 1 byte for type
        header = bytearray([0xAA, data_len, 0x02])
        checksum = 0 ^ 0x02
        checksum ^= _data
        footer = bytearray([checksum, 0x55])
        return header + struct.pack('!B',_data) + footer
    elif(data_type == 3):
        # 控制指令，用于拍摄完图片后通知车抓取
        # data = 01 抓取走人
        data_len = len(_data) + 1  # 1 byte for type
        header = bytearray([0xAA, data_len, 0x03])
        checksum = 0 ^ 0x03
        for byte in data:
            checksum ^= byte
        footer = bytearray([checksum, 0x55])
        return header + data + footer
