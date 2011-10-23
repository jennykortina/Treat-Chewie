# Shreyans Bhansali and Jenny Kortina <http://treatchewie.com>
import sys
sys.path.append("../")
import serial
import treatchewie_settings

def run_arduino(arduino_board_location):
    # run the code already on the arduino
    if not arduino_board_location:
        arduino_board_location = treatchewie_settings.ARDUINO_BOARD_LOCATION
    serial.Serial(arduino_board_location, 9600)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run_arduino(sys.argv[1])
