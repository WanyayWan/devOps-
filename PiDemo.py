from threading import Thread
from hal import hal_keypad as keypad
from hal import hal_lcd as LCD
from hal import hal_ir_sensor as IR
from hal import hal_led as led_ctrl
from hal import hal_usonic as usonic
from hal import hal_servo as servo
from hal import hal_adc as potentio
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview as picam2
import time
from telegram import Bot

#door_assigned values
open_door_adc = 256
open_door_angle = 180

closed_door_adc = 0
closed_door_angle = 0

BOT_TOKEN = "7723998968:AAFc4QK-qRaIxCfqeqLYRs1OLuF-2z_OOiM"
CHAT_ID = "5819192033"

# Initialize LCD
lcd = LCD.lcd()
lcd.lcd_clear()

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN)

# Function to send Telegram message
def send_telegram_message(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"Telegram message sent: {message}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def map_adc_to_angle(adc_value):
    return int((adc_value / 1023) * 180)

#Call back function invoked when any key on keypad is pressed
def key_pressed(key):

    lcd.lcd_clear()
    lcd.lcd_display_string("LED Control", 1)

    if key ==1:
        lcd.lcd_display_string("Blink LED",2)
        print("press_1")
        led_ctrl.led_control_init()
       
    elif key ==0:
        lcd.lcd_display_string("OFF LED",1)
        led_ctrl.set_delay(0)
     



def main():

    # Initialize LCD
    lcd = LCD.lcd()
    lcd.lcd_clear()
    
    servo.init()
    potentio.init()

    # Display something on LCD
    lcd.lcd_display_string("LED Control ", 1)
    lcd.lcd_display_string("0: Off 1:Blink", 2)

    # Initialize the HAL keypad driver
    keypad.init(key_pressed)

    # Start the keypad scanning which will run forever in an infinite while(True) loop in a new Thread "keypad_thread"
    keypad_thread = Thread(target=keypad.get_key)
    keypad_thread.start()

    while(True):
    #testing IR sensor
        IR.init()
        usonic.init()
        distance = usonic.get_distance()
        if distance < 15:
            print("Object detected!")
            
            
            if IR.get_ir_sensor_state():
                    print("it is getting near!")
                    time.sleep(1)
                    lcd.lcd_display_string("Intrusion Alert!", 2)

                    # Ensure the door is closed
                    servo.set_servo_position(closed_door_angle)
                    print("Door set to closed position.")

                    # Check ADC value
                    adc_value = potentio.get_adc_value(0)
                    if adc_value != closed_door_adc:
                        lcd.lcd_display_string("Intruder Alert!", 1)
                        print("Someone is holding the door!")

                    # Send Telegram alert
                    send_telegram_message("Alert: Someone is holding the door!")
            else:
                    print("Chill out, its OK.")
                    time.sleep(1)
        else:
                print("Object not detected!")
                time.sleep(1)




# Main entry point
if __name__ == "__main__":
    main()