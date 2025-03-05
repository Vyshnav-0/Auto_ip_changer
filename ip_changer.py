#!/usr/bin/env python3
import subprocess
import time
import requests
import sys
import os
import random
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich import print as rprint

# Initialize rich console
console = Console()

def get_current_ip():
    try:
        # Try multiple IP checking services
        services = [
            'https://api.ipify.org?format=json',
            'https://api.myip.com',
            'https://ip.seeip.org/json'
        ]
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    return response.json()['ip']
            except:
                continue
        return "Could not get IP"
    except:
        return "Could not get IP"

def get_ovpn_files():
    # Get all .ovpn files from the OpenVPN servers folder
    ovpn_folder = "openvpn"  # Change this to your folder path if different
    try:
        ovpn_files = [f for f in os.listdir(ovpn_folder) if f.endswith('.ovpn')]
        return [os.path.join(ovpn_folder, f) for f in ovpn_files]
    except Exception as e:
        console.print(f"[red]Error reading OpenVPN folder: {e}[/red]")
        return []

def create_auth_file():
    # Create a temporary auth file with credentials
    auth_file = "vpn_auth.txt"
    with open(auth_file, "w") as f:
        f.write("vpnbook\n")  # username
        f.write("afsz8r7\n")  # password
    return auth_file

def verify_vpn_connection():
    # Check if we're connected to VPN by looking for tun0 interface
    try:
        result = subprocess.run(["ip", "addr", "show", "tun0"], 
                              capture_output=True, 
                              text=True)
        return result.returncode == 0
    except:
        return False

def create_status_table(current_ip, new_ip, server_name):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Current IP", str(current_ip))
    table.add_row("New IP", str(new_ip))
    table.add_row("Connected Server", server_name)
    table.add_row("VPN Status", "[green]Connected[/green]" if verify_vpn_connection() else "[red]Disconnected[/red]")
    
    return table

def change_ip():
    try:
        # Get current IP before change
        current_ip = get_current_ip()
        console.print(Panel(f"[yellow]Current IP:[/yellow] [green]{current_ip}[/green]", title="Initial Status"))

        # Get list of available OpenVPN configurations
        ovpn_files = get_ovpn_files()
        if not ovpn_files:
            console.print("[red]No OpenVPN configuration files found![/red]")
            return False

        # Randomly select a VPN server
        selected_server = random.choice(ovpn_files)
        server_name = os.path.basename(selected_server)
        console.print(Panel(f"[yellow]Selected Server:[/yellow] [green]{server_name}[/green]", title="Server Selection"))

        # Create auth file
        auth_file = create_auth_file()
        
        # Kill any existing OpenVPN processes
        subprocess.run(["sudo", "killall", "openvpn"], stderr=subprocess.DEVNULL)
        time.sleep(3)

        # Start new OpenVPN connection with auth file
        process = subprocess.Popen([
            "sudo", "openvpn",
            "--config", selected_server,
            "--auth-user-pass", auth_file,
            "--verb", "3"
        ])
        
        # Wait for connection to establish with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Establishing VPN connection...", total=10)
            for attempt in range(10):
                if verify_vpn_connection():
                    progress.update(task, completed=10)
                    console.print("[green]VPN connection established![/green]")
                    break
                progress.update(task, advance=1)
                time.sleep(2)
        
        # Additional wait to ensure connection is stable
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Stabilizing connection...", total=5)
            for i in range(5):
                progress.update(task, advance=1)
                time.sleep(1)
        
        # Get new IP
        new_ip = get_current_ip()
        
        # Display status table
        console.print(create_status_table(current_ip, new_ip, server_name))
        
        # Clean up auth file
        try:
            os.remove(auth_file)
        except:
            pass
            
        return True
    except Exception as e:
        console.print(f"[red]Error changing IP: {e}[/red]")
        return False

def main():
    # Clear screen and show welcome message
    console.clear()
    console.print(Panel.fit(
        "[bold blue]IP Changer for Kali Linux[/bold blue]\n"
        "[yellow]Automatically changes your IP address every 5 seconds[/yellow]\n"
        "[red]Press Ctrl+C to stop[/red]",
        title="Welcome",
        border_style="blue"
    ))
    
    try:
        while True:
            if change_ip():
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeElapsedColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("[cyan]Waiting before next change...", total=5)
                    for i in range(5):
                        progress.update(task, advance=1)
                        time.sleep(1)
            else:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeElapsedColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("[red]Failed to change IP. Retrying...", total=5)
                    for i in range(5):
                        progress.update(task, advance=1)
                        time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[red]Stopping IP Changer...[/red]")
        subprocess.run(["sudo", "killall", "openvpn"], stderr=subprocess.DEVNULL)
        try:
            os.remove("vpn_auth.txt")
        except:
            pass
        console.print("[green]Cleanup complete. Goodbye![/green]")
        sys.exit(0)

if __name__ == "__main__":
    main() 