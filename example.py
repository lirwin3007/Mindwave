import bluetooth
import struct

bd_addr = "98:D3:31:F4:01:58"
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr, port))

SYNC = 0xAA
EXCODE = 0x55
CODES = [{"LEVEL":0,"CODE":0x02,"DESCRIPTOR":"POOR_SIGNAL"},
         {"LEVEL":0,"CODE":0x03,"DESCRIPTOR":"HEART_RATE"},
         {"LEVEL":0,"CODE":0x04,"DESCRIPTOR":"ATTENTION"},
         {"LEVEL":0,"CODE":0x05,"DESCRIPTOR":"MEDITATION"},
         {"LEVEL":0,"CODE":0x06,"DESCRIPTOR":"8BIT_RAW"},
         {"LEVEL":0,"CODE":0x07,"DESCRIPTOR":"RAW_MARKER"},
         {"LEVEL":0,"CODE":0x80,"DESCRIPTOR":"RAW_WAVE_VALUE"},
         {"LEVEL":0,"CODE":0x81,"DESCRIPTOR":"EEG_POWER"},
         {"LEVEL":0,"CODE":0x83,"DESCRIPTOR":"ASIC_EEG_POWER"},
         {"LEVEL":0,"CODE":0x86,"DESCRIPTOR":"RRINTERVAL"}]

def parseData(Code, Value):
        Descriptor = "UNKNOWN"
        value = 0
        for CODE in CODES:
                if CODE["CODE"] == Code:
                        Descriptor = CODE["DESCRIPTOR"]
        if Code < 0x80:
                value = int.from_bytes(Value[0], byteorder='big')
        else:
                if Descriptor == "RAW_WAVE_VALUE":
                        byteValue = (Value[0] << 8) | Value[1]
                        value = int.from_bytes(byteValue, byteorder='big')
                elif Descriptor == "EEG_POWER":
                        byteArray = []
                        for counter in range(0,len(Value),4):
                                total = int.from_bytes(Value[counter + 0] << 24, byteorder='big')
                                total += int.from_bytes(Value[counter + 1] << 16, byteorder='big')
                                total += int.from_bytes(Value[counter + 2] << 8, byteorder='big')
                                total += int.from_bytes(Value[counter + 3], byteorder='big')
                                byteArray = 1
                                
                        value = {"DELTA":struct.unpack('>f', Value[0:5]),
                                 "THETA":struct.unpack('>f', (Value[4] << 24) | (Value[5] << 16) | (Value[6] << 8) | (Value[7])),
                                 "LOW-ALPHA":struct.unpack('>f', (Value[8] << 24) | (Value[9] << 16) | (Value[10] << 8) | (Value[11])),
                                 "HIGH-ALPHA":struct.unpack('>f', (Value[12] << 24) | (Value[13] << 16) | (Value[14] << 8) | (Value[15])),
                                 "LOW-BETA":struct.unpack('>f', (Value[16] << 24) | (Value[17] << 16) | (Value[18] << 8) | (Value[19])),
                                 "HIGH-BETA":struct.unpack('>f', (Value[20] << 24) | (Value[21] << 16) | (Value[22] << 8) | (Value[23])),
                                 "LOW-GAMMA":struct.unpack('>f', (Value[24] << 24) | (Value[25] << 16) | (Value[26] << 8) | (Value[27])),
                                 "MID-GAMMA":struct.unpack('>f', (Value[28] << 24) | (Value[29] << 16) | (Value[30] << 8) | (Value[31]))}
                elif Descriptor == "ASIC_EEG_POWER":
                        #for counter in range(0,len(Value)):
                        #        Value[counter] = int.from_bytes(Value[counter], byteorder='big')
                        value = {"DELTA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(0,3)])),
                                 "THETA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(3,6)])),
                                 "LOW-ALPHA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(6,9)])),
                                 "HIGH-ALPHA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(9,12)])),
                                 "LOW-BETA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(12,15)])),
                                 "HIGH-BETA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(15,18)])),
                                 "LOW-GAMMA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(18,21)])),
                                 "MID-GAMMA":struct.unpack('>I', bytearray([0] + [int.from_bytes(Value[counter], byteorder='big') for counter in range(21,24)]))}
        return Descriptor,value

def parseDataRows(Payload):
        Data = {}
        while len(Payload) > 0:
                ExcodeCount = 0
                currentByte = Payload[0]
                currentInt = int.from_bytes(currentByte, byteorder='big')
                while currentInt == EXCODE:
                        ExcodeCount += 1
                        del Payload[0]
                        currentByte = Payload[0]
                        currentInt = int.from_bytes(currentByte, byteorder='big')
                currentByte = Payload[0]
                currentInt = int.from_bytes(currentByte, byteorder='big')
                Code = currentInt
                del Payload[0]
                VLength = 1
                if Code > 0x80:
                        currentByte = Payload[0]
                        currentInt = int.from_bytes(currentByte, byteorder='big')
                        VLength = currentInt
                        del Payload[0]
                Value = []
                for counter in range(0,VLength):
                        Value.append(Payload[0])
                        del Payload[0]
                Descriptor, Value = parseData(Code, Value)
                if Descriptor != "UNKNOWN":
                        Data[Descriptor] = Value
        print(str(Data["POOR_SIGNAL"]) + "     Attention:" + str(Data["ATTENTION"]) + "     Meditation:" + str(Data["MEDITATION"]))
        

while True:
        nextByte = sock.recv(1)
        nextInt = int.from_bytes(nextByte, byteorder='big')
        if nextInt == SYNC:
                nextByte = sock.recv(1)
                nextInt = int.from_bytes(nextByte, byteorder='big')
                if nextInt == SYNC:
                        PLength = SYNC
                        while PLength == SYNC:
                                nextByte = sock.recv(1)
                                PLength = int.from_bytes(nextByte, byteorder='big')
                        if PLength <= 170:
                                Payload = []
                                checksum = 0
                                for counter in range(0,PLength):
                                        nextByte = sock.recv(1)
                                        Payload.append(nextByte)
                                        nextInt = int.from_bytes(nextByte, byteorder='big')
                                        checksum += nextInt
                                checksum = checksum & 0xFF
                                checksum = ~checksum & 0xFF
                                nextByte = sock.recv(1)
                                nextInt = int.from_bytes(nextByte, byteorder='big')
                                if checksum == nextInt:
                                        parseDataRows(Payload)
                                else:
                                        print("Checksum verification failed! Disregarding packet")







packet = ""
end = False
foundmed = False
foundatt = False
counter = 0
plength = 10

while True:
        while not end:
                packet = packet+binascii.hexlify(sock.recv(1024)).decode('utf-8')
                if packet[-2:] == "aa":
                        end = True
        try:
                plength =int(packet[2:4], 16)
        except:
                print("")
        print(packet)
        for x in range(0, plength+2):
                counter = counter + 1
                if packet[counter:counter+2] == "04":
                        foundmed == True
                if counter > 100:
                        foundmed = True
        try:
                #print("attention"+packet[62:64])
                pass
        except:
                print("")
        #print(packet)
        #print(plength)
        #print("-----------------")
        foundmed = False
        packet = ""
        end = False
        counter = 0
