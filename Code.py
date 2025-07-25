
import socket
import json
import serial
import time

# UDP settings
UDP_IP = "127.0.0.1"  # Local IP
UDP_PORT = 12345  # Port set in OpenBCI GUI

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Arduino serial port settings
try:
    arduino = serial.Serial('COM7', 9600)

    print("Connected to Arduino")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")
    arduino = None

# Global variable to store the last sent value
last_sent_value = None


def process_focus_data(data):
    """Process Focus data and decide whether to send it to Arduino"""
    global last_sent_value

    try:
        # Parse JSON data
        focus_data = json.loads(data)
        focus_value = focus_data.get('data', 0)

        # Decide to send '1' or '0' based on focus_value
        # Here, we assume focus_value > 0.5 means "focused", otherwise "not focused"
        # You can modify this logic based on your actual needs
        new_value = '1' if focus_value == 1 else '0'

        # Only send when the value changes
        if new_value != last_sent_value:
            # Send to Arduino
            if arduino:
                arduino.write(new_value.encode('ascii'))
                print(f"Sent to Arduino: {new_value} (previous: {last_sent_value})")
                last_sent_value = new_value

    except json.JSONDecodeError:
        print("Error decoding JSON data")
    except Exception as e:
        print(f"Error in process_focus_data: {e}")


print("Starting UDP server...")
while True:
    try:
        data, addr = sock.recvfrom(1024)
        decoded_data = data.decode('utf-8').strip()
        print(f"Received: {decoded_data}")

        process_focus_data(decoded_data)

    except KeyboardInterrupt:
        print("\nServer stopped by user")
        break
    except Exception as e:
        print(f"Error in main loop: {e}")
        time.sleep(1)  # Wait for 1 second when an error occurs

# Clean up resources
if arduino:
    arduino.close()
sock.close()
