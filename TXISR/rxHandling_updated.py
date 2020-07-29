import io
import sys
import sqlite3
import struct
import subprocess
import calendar
import time


class TXISR:
    
    # List that stores eveything recieved in the transmission
    rxData = ['#']
    
    # Define location of file where the data will be placed while waiting transmission
    outputFile = "test.txt"
    
    # Define file where transmission will be recieved
    # commented out for testing purposes:
    # inputFile = "/dev/tty/AMA0"
    # file for testing purposes:
    inputFile = "C:/Users/Get Away Special/Desktop/Build RX H/transTestAttitude.txt" 
    
    def __init__(self):
    '''
    Constructor. This will drive the process.
    '''
         
        if not path.exists(self.inputFile):
            print("INPUT FILE NOT FOUND")
            sys.exit()
        else:
            self.TX = open(self.inputFile, 'r')
            self.readTX()    
            
        # commandRecieved will figure out how to process based on the command received
        self.commandReceived()

    
    def readTX(self):
    '''
    Read-in and decode transmission. Place decoded transmission in rxData
    '''
        for i in range(5):
            currentData = self.TX.readline()
            # Commented out for testing purposes:
            # currentData = bytes.fromhex(hexMessage).decode('utf-8')
            # testing functionality:
            currentData = int(hexMessage, 0)
            self.rxData.append(currentData)
    
    def commandReceived(self):
    '''
    Decide what to do based on the command recieved
    '''
        if(self.rxData[0] == 0):
            ### TODO PROCESS ALL THE OPTIONS FOR THE DATA TYPES
            if(self.rxData[3] == 0):
                # Process Attitude Data
            else if(self.rxData[3] == 1):
                # Process TT&C Data
            else if(self.rxData[3] == 2):
                # Process Deployment Data
            else if(self.rxData[3] == 3):
                self.drivePic(self.rxData[3])
            else if(self.rxData[3] == 4):
                # Process LQ Picture
            else if(self.rxData[3] == 5):
                # Add window to file 
            return
        else :
            #turn off tx
            if(self.rxData[1] == 0):
                canTX = False
            #take pic
            else if(self.rxData[2] == 1) :
                #photo.Camera()
            #deploy boom
            else if(self.rxData[3] == 1) :
                #boom.boomDeployer()
            else if(self.rxData[4] == 1) :
                #reboot pi, send command to adruino
            else :
                return
    
    def driveDataType (self, dataType):   
        '''
        function if no picture is requested 
        '''
        data = [()]

        ### TODO: Get packets from the files on the system
        data.reverse()
        
        numLines = self.packetize(False, data)
        
    def packetize(self, isPic, *dataList):
        """
        Write to file 
        """
        linesTotal = 0
        
        if isPic == True:
            ### TODO: Decide how to packetize a picture
            ### TODO: Locate the picture data and report to TX function .exe
            pass
        elif isPic == False:
            self.wipeTxFile()
            
            f = open(self.outputFile, 'a')

            linesTotal = 0

            for tup in dataList:
                for value in tup:
                
                    ### STRING METHOD:
                    f.write(str(value))
                    f.write(',')
                     
                    ## BINARY METHOD
                    #ba = bytearray(struct.pack("f", value))
                    #t = ""
                    #for b in ba:
                    #    t = "0x%02x" % b
                    
                    ### HEX NUMBER METHOD: 
                    #hexNum = num_to_hex(value)			   
                    #f.write(hexNum)

                    ### HEX STRING METHOD:
                    #
                    #
                
                f.write('\n')
                linesTotal += 1
            f.write('@')
            f.write('\n')
        f.write(str(linesTotal))
        f.close()
        return linesTotal 

    def wipeTxFile():
        file = open(self.outputFile,"r+")
        file.truncate(0)
        file.close()        
    
### TODO: Add reading in from file-like database
### TODO: Add Command functionality
### TODO: Add processing of camera
### TODO: Process AX25 Packets