# IP Changer for Kali Linux

A Python script that automatically changes your IP address every 3 seconds using OpenVPN servers.

## Features

- Automatically changes IP address every 3 seconds
- Uses OpenVPN servers for secure connections
- Supports multiple VPN protocols (UDP53, UDP25000, TCP80, TCP443)
- Random server selection for better anonymity
- Automatic cleanup of temporary files
- Easy to use

## Prerequisites

- Kali Linux
- Python 3.x
- OpenVPN
- Root privileges (sudo access)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd ip-changer
```

2. Install OpenVPN if not already installed:
```bash
sudo apt-get update
sudo apt-get install openvpn
```

3. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

4. Place your OpenVPN configuration files (`.ovpn` files) in the `openvpn` folder:
   - UDP53 profiles
   - UDP25000 profiles
   - TCP80 profiles
   - TCP443 profiles

## Usage

1. Run the script with sudo privileges:
```bash
sudo python3 ip_changer.py
```

2. The script will:
   - Show your current IP address
   - Connect to a random VPN server
   - Display your new IP address
   - Wait 3 seconds before changing again

3. To stop the script, press `Ctrl+C`

## VPN Credentials

The script uses the following credentials:
- Username: vpnbook
- Password: afsz8r7

## Troubleshooting

If you encounter any issues:

1. Make sure you have root privileges (sudo access)
2. Verify that OpenVPN is properly installed
3. Check that your `.ovpn` files are in the correct folder
4. Ensure you have an active internet connection
5. Check if the VPN credentials are still valid

## Security Notes

- The script creates a temporary authentication file that is automatically deleted after use
- All VPN connections are encrypted
- The script uses secure HTTPS to check your IP address
- No credentials are stored permanently

## Disclaimer

This tool is for educational purposes only. Make sure to comply with your local laws and regulations regarding VPN usage and IP address changes.

## License

This project is open source and available under the MIT License. 