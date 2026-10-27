# Simulation Commands

This document records the primary commands used during the controlled Project 4 adversary simulation.

All commands were executed within the isolated SOC laboratory environment.

---

## 1. Network Reconnaissance

### Nmap — WinRM Service Discovery

Executed from Kali Linux:

```bash
nmap -Pn -sV -p 5985 192.168.56.10
```

Purpose:

- Identify whether TCP port 5985 was reachable.
- Identify the service exposed on the port.
- Confirm the presence of Windows Remote Management (WinRM).

Observed service:

```text
5985/tcp open http Microsoft HTTPAPI httpd 2.0
Service Info: OS: Windows
```

---

## 2. WinRM Remote Access

### Evil-WinRM

Executed from Kali Linux:

```bash
evil-winrm -i 192.168.56.10 -u soc_lab
```

Purpose:

- Establish a controlled remote PowerShell session to the Windows endpoint.
- Validate that the intentionally configured WinRM service was accessible using the dedicated lab account.

No credentials are stored in this repository.

---

## 3. Remote Discovery

Executed within the WinRM session:

### Identify the Current User

```powershell
whoami
```

### Identify the Windows Host

```powershell
hostname
```

### Identify the Current Working Directory

```powershell
Get-Location
```

### List Directory Contents

```powershell
Get-ChildItem
```

These commands were limited to basic host and session discovery.

---

## 4. Controlled File Transfer

### Create the Test File on Kali

Executed on Kali:

```bash
echo "Project 4 controlled file transfer test" > ~/soc_lab_test.txt
```

The file contained only benign test text.

### Start a Temporary HTTP Server

Executed on Kali:

```bash
cd ~
python3 -m http.server 8000 --bind 192.168.56.105
```

The HTTP server was used only to provide the controlled test file to the Windows endpoint.

### Download the Test File on Windows

Executed inside the WinRM session:

```powershell
Invoke-WebRequest -Uri "http://192.168.56.105:8000/soc_lab_test.txt" -OutFile "C:\Users\Public\soc_lab_test.txt"
```

### Verify the File

```powershell
Get-Item "C:\Users\Public\soc_lab_test.txt"
```

This operation generated Sysmon Event ID 11 file-creation telemetry.

---

## 5. Remote Session Exit

After completing the controlled activity:

```powershell
exit
```

This terminated the Evil-WinRM session.

---

## 6. Wazuh Detection Validation

### Validate Wazuh Rule Configuration

The Wazuh analysis engine was used to validate the custom rule configuration:

```bash
sudo /var/ossec/bin/wazuh-analysisd -t
```

The configuration was validated before restarting the Wazuh Manager.

### Restart Wazuh Manager

```bash
sudo systemctl restart wazuh-manager
```

### Verify Wazuh Manager

```bash
sudo systemctl status wazuh-manager --no-pager
```

The manager was verified to be running before detection testing.

---

## 7. Custom Detection Rules

Two custom Wazuh rules were created and validated during the project.

### Rule 100002

Purpose:

Detect the controlled file-creation behavior associated with the WinRM provider process in the Windows Public directory.

Key conditions:

```text
Parent Rule: 61613
Process: wsmprovhost.exe
Target path: C:\Users\Public\
MITRE ATT&CK: T1105
```

### Rule 100003

Purpose:

Detect WinRM provider process creation.

Key conditions:

```text
Parent Rule: 61603
Process: wsmprovhost.exe
MITRE ATT&CK: T1021.006
```

Both rules successfully generated Wazuh alerts during controlled validation.

---

## 8. Telemetry Investigation

The simulation was investigated using:

- Windows Security Event Logs
- Sysmon Operational logs
- Wazuh Archives
- Wazuh Alerts

Relevant telemetry included:

```text
Windows Security Event ID 4624
Sysmon Event ID 1
Sysmon Event ID 11
```

These events provided the evidence used to validate the remote-access and controlled file-transfer detections.

---

## 9. Lab Network Addresses

The simulation used the following isolated host-only network addresses:

```text
Kali Linux       192.168.56.105
Windows 10       192.168.56.10
Ubuntu Wazuh     192.168.56.20
```

These addresses belong to the project's isolated laboratory network.

---

## 10. Operational Notes

The following activities were intentionally excluded from the simulation:

- Credential dumping
- Password theft
- Malware deployment
- Ransomware
- Destructive actions
- Public-target scanning
- Unnecessary persistence
- Exploitation of an actual software vulnerability

The purpose of the exercise was to demonstrate controlled adversary simulation, endpoint telemetry analysis, and SOC detection engineering rather than offensive exploitation.