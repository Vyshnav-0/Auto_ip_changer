#!/usr/bin/env python3
import subprocess
import time
import requests
import sys
import os
import random

def get_current_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except:
        return "Could not get IP"

def get_ovpn_files():
    # Get all .ovpn files from the OpenVPN servers folder
    ovpn_folder = "openvpn"  # Change this to your folder path if different
    try:
        ovpn_files = [f for f in os.listdir(ovpn_folder) if f.endswith('.ovpn')]
        return [os.path.join(ovpn_folder, f) for f in ovpn_files]
    except Exception as e:
        print(f"Error reading OpenVPN folder: {e}")
        return []

def create_auth_file():
    # Create a temporary auth file with credentials
    auth_file = "vpn_auth.txt"
    with open(auth_file, "w") as f:
        f.write("vpnbook\n")  # username
        f.write("afsz8r7\n")  # password
    return auth_file

def change_ip():
    try:
        # Get current IP before change
        current_ip = get_current_ip()
        print(f"Current IP: {current_ip}")

        # Get list of available OpenVPN configurations
        ovpn_files = get_ovpn_files()
        if not ovpn_files:
            print("No OpenVPN configuration files found!")
            return False

        # Randomly select a VPN server
        selected_server = random.choice(ovpn_files)
        print(f"Connecting to: {os.path.basename(selected_server)}")

        # Create auth file
        auth_file = create_auth_file()
        
        # Kill any existing OpenVPN processes
        subprocess.run(["sudo", "killall", "openvpn"], stderr=subprocess.DEVNULL)
        time.sleep(2)

        # Start new OpenVPN connection with auth file
        subprocess.Popen([
            "sudo", "openvpn",
            "--config", selected_server,
            "--auth-user-pass", auth_file
        ])
        
        # Wait for connection to establish
        time.sleep(5)
        
        # Get new IP
        new_ip = get_current_ip()
        print(f"New IP: {new_ip}")
        
        # Clean up auth file
        try:
            os.remove(auth_file)
        except:
            pass
            
        return True
    except Exception as e:
        print(f"Error changing IP: {e}")
        return False

def main():
    print("Starting IP Changer...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            if change_ip():
                print("Waiting 3 seconds before next change...")
                time.sleep(3)
            else:
                print("Failed to change IP. Retrying in 3 seconds...")
                time.sleep(3)
    except KeyboardInterrupt:
        print("\nStopping IP Changer...")
        subprocess.run(["sudo", "killall", "openvpn"], stderr=subprocess.DEVNULL)
        # Clean up auth file if it exists
        try:
            os.remove("vpn_auth.txt")
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    main() 