#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
//Take just the DEBUG line out when your are done debugging and leave debug.h
#define DEBUG
#include "debug.h"

//enable and disable are set up in the make file,
#define ENABLE "./configPinsTXISR"
#define DISABLE "./configPinsTXISRDone"

#define FLAG_FILE "./out.txt" //change this later for the real program
#define FORMAT_FILE "./temp.txt" //this is the file that dallan will creat
#define UART_PORT "/dev/serial0" //this is serial port name, make sure this is correct for the final code

//this is our time delay
#define DELAY_tx 120

//this sets control of the settings for our serial port
struct termios options;

void setUpUart();

//returns ms since the epoch
long millis()
{
    return time(NULL) * 1000;
}


/*******************************************************************************************
 * sudo code: Main
 * this first tries to open the file it is trying to send
 * then it tries to take control of the serial ports
 * then it tries to open the serial port
 * then it reads each line of the file and sends it one at a time
 *      NOTE: the program will wait x number of millaseconds inbetween each line it sends
 *            depending on what the radio needs
 * After it has sent everything it opens the flags file and records the time of the last
 *      sent record
 * It then closes the serial port
 * it then returns control back to linuxs
 * Program then exits
 *******************************************************************************************/
void main(int argc,char* argv[])
{
    /////TODO/////
    /*
    *debug the time check on transmissionWindow 
    *debug the wait after each transmission 
    *Write the time to the flags file
    *Add in any set up commucation to the radio
    * TEST, UART, and the bash commands
    */
    int startTime = millis();
    int currentTime = millis();
    int startTimeTX = 0;
    int currentTimeTX = 0; 
    int dataType = argv[1];
    int transmissionWindow = 0;

    FILE *txFile;
    if (!(txFile = fopen(FORMAT_FILE,"r")))
    {
        //if we fail exit
        DEBUG_P(Failed to open file)
        exit(1);
    }

    FILE *recordFile;
    if (!(recordFile = fopen(FLAG_FILE,"r+")))
    {
        //if we fail exit
        DEBUG_P(Failed to open the flags file)
        exit(1);
    }

    //this is where we will store the last transmission
    //5 data types, the type and the last sent time, 10 chars of time so 4 by 7;
    int flags[5][11];
    //pop the data types
    for (int i =0; i < 5; )
    {
        char temp = fgetc(recordFile);
        if(temp != ' ') 
        {
            flags[i][0] = temp;
            i++;
        }
    }

    for (int i =0; i < 5; i++)
    {
        char temp = fgetc(recordFile);
        //this populatest The flags array
        for(int k = 0; temp != ' '; k++)
        {
            flags[i][k] = temp;
            temp = fgetc(recordFile);
        }

    }
    //config linuxs to give us the pins
    int enable = system(ENABLE);
    //if we fail reboot
    if(enable == -1) 
    {
        DEBUG_P(Failed to connect to tx pin)
        exit(1);
    }

    //open the serial ports
    int txPort = open(UART_PORT, O_RDWR | O_NOCTTY ); 
    if (txPort == -1)
    {
        printf ("Error no is : %d\n", errno);
        printf("Error opening serial port\n");
        exit(1);
    }
    //set up the uart 
    setUpUart();

    //write to the radio
    write(txPort, "ES+W23003321", 13);

    //read in all the lines of a file
    char ch = fgetc(txFile);
    PRINT_DEBUG_c(ch)
    //set up array for tx, the max is 128, so we better not exceed that anyways so using an array of 128 is fine.
    char line[128] = {0};
    char timeStamp[10];
    //get tx time
    fscanf(txFile, "%d", &transmissionWindow);
    PRINT_DEBUG(transmissionWindow)
    fgetc(txFile);

    DEBUG_P(Printing file>>>)
    while(ch != EOF)
    {
        DEBUG_P(\nSending>>>)
        //this checks the transmission window
        currentTime = millis();
        if((currentTime - startTime) < transmissionWindow) 
        {
            for(int g = 1; g < 11; g++)
            {
                flags[dataType][g] = timeStamp[g];
            }
            //pop the types
            for(int y = 0; y < 5; y++)
            {
               fputc(flags[y][0], recordFile);
            }
            fputc('\n', recordFile);
            //wrtie time stamps
            for(int i = 0; i < 5; i++)
            {
                for(int g = 0; g < 11; g++)
                {
                    fputc(flags[dataType][g], recordFile);
                }
                fputc(' ', recordFile);
            }
            break;
        }

        
        PRINT_DEBUG(currentTime - startTime)

        PRINT_DEBUG_CHAR('\n')
        //get the size of each line in the file
        int charCount = 0;

        //this will be our timp stamp array,

        
        int end = 0;
        int charTimeCount = 1;
        for (int i = 0; i < 128; i++)
        {
            line[i] = '0';
        }
        while(ch != 10 && ch != '@')
        {
            //this collects the time stamp
            if(!end && ch != EOF)
            {
                timeStamp[charTimeCount - 2] = ch;
            }
            else if (ch == 58)
            {
                end = 1;
            }
            //save all the data in that line
            line[charCount++] = ch;
            PRINT_DEBUG(charCount)
            Sif(ch != EOF) ch = fgetc(txFile);
        }
        //transmit the data
        #ifdef DEBUG
            for(int i = 0; i < charCount; i++)
            {
                PRINT_DEBUG_CHAR(line[i]) 
            }
            PRINT_DEBUG_CHAR('\n')
        #endif
        //this line of code sends things out on the tx line
        //start the transmition time
        startTimeTX = millis();
        write(txPort, line, charCount);
        //delay the right amount of time for the radio
        while((currentTimeTX - startTimeTX) < DELAY_tx) currentTimeTX = millis();
        PRINT_DEBUG(currentTimeTX)
        PRINT_DEBUG(startTimeTX)
        PRINT_DEBUG(currentTime)
        PRINT_DEBUG(startTime)
        currentTime = millis();

        if(ch == 10 && ch != EOF)
        {
            ch = fgetc(txFile);
        }


        //save the last sent time
        if(ch == EOF)
        {
            for(int g = 1; g < 11; g++)
            {
                flags[dataType][g] = timeStamp[g];
            }
            //pop the types
            for(int y = 0; y < 5; y++)
            {
               fputc(flags[y][0], recordFile);
            }
            fputc('\n', recordFile);
            //wrtie time stamps
            for(int i = 0; i < 5; i++)
            {
                for(int g = 0; g < 11; g++)
                {
                    fputc(flags[dataType][g], recordFile);
                }
                fputc(' ', recordFile);
            }
            break;
        }
    } 

    //give control of the port back to linuxs
    int disable = system(DISABLE);
    //if we fail reboot
    if(disable == -1) 
    {
        DEBUG_P(Failed to release tx uart pin)
        exit(1);
    } 
}

/*******************************************************************************************
 * setUpUart
 * this func sets up the uart commincation for us so everything works nicely
 *******************************************************************************************/
void setUpUart()
{
    //set the baud rate, it is the number with a b infornt of it ex 115200 -> B115200
    cfsetspeed(&options, B115200);

    //set up the number of data bits
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
}

