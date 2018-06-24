import bluetooth
import binascii

bd_addr = "98:D3:31:F4:01:58"
port = 1
sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
sock.connect((bd_addr, port))

SYNC = 0xAA

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




def parseDataRows(Payload):
        pass


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
