from threading import Thread
from hal import hal_keypad as keypad
from hal import hal_lcd as LCD
from hal import hal_ir_sensor as IR
from hal import hal_led as led_ctrl
from hal import hal_usonic as usonic
from hal import hal_servo as servo
from hal import hal_adc as potentio
from picamera2 import Picamera2
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

# Admin access variables
ADMIN_PASSCODE = "1234"  # Replace with a secure passcode
admin_logged_in = False  # Flag to track admin access
entered_passcode = ""    # Buffer to store passcode input

def admin_lcd_output():
    lcd.lcd_display_string("Enter Admin Code:", 1)
    lcd.lcd_display_string("*" * len(entered_passcode), 2)  # Mask input with asterisks

# Function to handle admin login
def handle_admin_login(key):
    global entered_passcode, admin_logged_in

    # Add the key to the entered passcode
    entered_passcode += str(key)
    lcd.lcd_clear()
    admin_lcd_output()

    # Check if the passcode is complete
    if len(entered_passcode) == len(ADMIN_PASSCODE):
        if entered_passcode == ADMIN_PASSCODE:
            admin_logged_in = True
            lcd.lcd_clear()
            lcd.lcd_display_string("Access Granted", 1)
            lcd.lcd_display_string("Press # to log out", 2)
            print("Admin access granted.")
            send_telegram_message("Admin logged in successfully.")
            if key_pressed=='#':
                admin_logged_in = False
                lcd.lcd_clear()
                admin_lcd_output()
        else:
            lcd.lcd_clear()
            lcd.lcd_display_string("Access Denied", 1)
            print("Admin access denied.")
            send_telegram_message("Failed admin login attempt.")
        entered_passcode = ""  # Reset passcode buffer

# Modify the key_pressed function to loop back to admin login on logout
def key_pressed(key):
    global admin_logged_in

    if not admin_logged_in:
        # If admin is not logged in, check for admin login
        handle_admin_login(key)
        return

    # Admin functionalities start here
    if key == "#":
        # Log out the admin
        admin_logged_in = False
        lcd.lcd_clear()
        lcd.lcd_display_string("Logged Out", 1)
        time.sleep(2)
        admin_lcd_output()  # Redirect to admin login
        return

    # Admin-specific functionality can be added here
    lcd.lcd_clear()
    lcd.lcd_display_string("Admin Logged In", 1)
    lcd.lcd_display_string("Press # to log out", 2)


# Function to send Telegram message
def send_telegram_message(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"Telegram message sent: {message}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def map_adc_to_angle(adc_value):
    return int((adc_value / 1023) * 180)


def main():

    # Initialize LCD
    lcd = LCD.lcd()
    lcd.lcd_clear()
    
    servo.init()
    potentio.init()

    # Display initial message on LCD
    lcd.lcd_display_string("Admin Login", 1)

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