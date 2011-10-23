# Shreyans Bhansali and Jenny Kortina <http://treatchewie.com>
import sys
import serial

def main(usbmodem_number):
    # run the code already on the arduino
    serial.Serial('/dev/tty.usbmodem%s' % usbmodem_number, 9600)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        try:
            main(int(sys.argv[1]))
        except:
            pass

