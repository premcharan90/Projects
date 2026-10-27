# Project 4 — Adversary Simulation & Blue-Team Detection

## Overview

This project demonstrates a controlled adversary simulation and blue-team detection workflow within an isolated SOC laboratory.

The simulation uses Kali Linux to perform network reconnaissance and establish controlled remote access to a Windows 10 endpoint through Windows Remote Management (WinRM). Remote discovery and a benign file-transfer activity are then performed to generate endpoint telemetry.

Windows Security logs and Sysmon events are collected by Wazuh, investigated, mapped to MITRE ATT&CK techniques, and used to develop and validate custom Wazuh detection rules.

The project focuses on understanding how adversary behavior translates into observable endpoint telemetry and how that telemetry can be converted into actionable SOC detections.

> **Important:** This project does not demonstrate exploitation of a software vulnerability. WinRM and a dedicated laboratory account were intentionally configured to enable the controlled simulation.

---

## Objectives

- Perform controlled network reconnaissance.
- Demonstrate remote access through WinRM.
- Generate Windows Security and Sysmon telemetry.
- Investigate remote authentication and process activity.
- Simulate a benign file-transfer scenario.
- Develop custom Wazuh detection rules.
- Map observed behaviors to MITRE ATT&CK.
- Analyze detection limitations and false positives.
- Document the complete SOC investigation workflow.

---

## Lab Architecture

```text
                         Isolated SOC Lab

┌─────────────────────┐
│     Kali Linux      │
│   192.168.56.105    │
│                     │
│  Nmap               │
│  Evil-WinRM         │
│  Python HTTP Server │
└──────────┬──────────┘
           │
           │ Host-Only Network
           │
           ▼
┌─────────────────────────────┐
│         Windows 10          │
│      192.168.56.10          │
│                             │
│  WinRM                      │
│  Wazuh Agent                │
│  Sysmon                     │
│  Windows Security Logs      │
└─────────────┬───────────────┘
              │
              │ Security + Sysmon
              │ Telemetry
              ▼
┌─────────────────────────────┐
│       Ubuntu / Wazuh        │
│      192.168.56.20          │
│                             │
│  Wazuh Manager              │
│  Wazuh Indexer              │
│  Wazuh Dashboard            │
└─────────────────────────────┘
```

---

## Attack Simulation Flow

```text
Nmap Reconnaissance
        ↓
WinRM Service Discovery
        ↓
Evil-WinRM Remote Session
        ↓
Windows Security Event 4624
        ↓
wsmprovhost.exe Process Creation
        ↓
Remote Discovery
        ↓
Controlled File Transfer
        ↓
Sysmon Event ID 11
        ↓
Wazuh Detection
        ↓
Blue-Team Investigation
        ↓
MITRE ATT&CK Mapping
```

---

## Environment

| Component | Details |
|---|---|
| Simulation Host | Kali Linux |
| Windows Endpoint | Windows 10 |
| SIEM | Wazuh |
| Endpoint Telemetry | Sysmon |
| Authentication Telemetry | Windows Security Logs |
| Remote Access | WinRM / Evil-WinRM |
| Network | Isolated Host-Only Network |
| Kali IP | `192.168.56.105` |
| Windows IP | `192.168.56.10` |
| Wazuh IP | `192.168.56.20` |

---

# Simulation

## 1. Network Reconnaissance

Nmap was used from Kali Linux to identify the WinRM service on the Windows endpoint.

Target:

```text
192.168.56.10
```

TCP port:

```text
5985/tcp
```

This activity represents:

**MITRE ATT&CK T1046 — Network Service Scanning**

---

## 2. WinRM Remote Access

A dedicated temporary laboratory account was used to establish a WinRM session with the Windows endpoint.

Evil-WinRM was used for the controlled remote session.

The session successfully reached:

```text
C:\Users\soc_lab\Documents
```

The following discovery commands were executed:

```powershell
whoami
hostname
Get-Location
Get-ChildItem
```

This activity represents:

**MITRE ATT&CK T1021.006 — Windows Remote Management**

---

## 3. Controlled File Transfer

A benign test file was hosted from Kali using a temporary Python HTTP server.

The Windows endpoint retrieved the file using `Invoke-WebRequest`.

Destination:

```text
C:\Users\Public\soc_lab_test.txt
```

The resulting file creation was recorded by Sysmon.

This controlled behavior was mapped to:

**MITRE ATT&CK T1105 — Ingress Tool Transfer**

---

# Blue-Team Investigation

## Windows Security Event 4624

The remote authentication generated Windows Security Event ID `4624`.

Observed characteristics included:

- Logon Type: `3`
- Account: `soc-lab`
- Source IP: `192.168.56.105`
- Authentication: `NTLM`
- Logon Process: `NtLmSsp`

Wazuh generated Rule `92652` for the successful remote logon.

The Wazuh rule referenced possible Pass-the-Hash activity. However, the available telemetry only confirms a successful NTLM network logon.

**Pass-the-Hash was not confirmed.**

---

## Sysmon Event ID 1 — Process Creation

Sysmon recorded the creation of:

```text
C:\Windows\System32\wsmprovhost.exe
```

Relevant process context:

```text
User:
WINDOWS10\soc-lab

Command Line:
C:\Windows\system32\wsmprovhost.exe -Embedding

Parent:
C:\Windows\System32\svchost.exe

Parent User:
NT AUTHORITY\SYSTEM

Integrity Level:
High
```

This provided endpoint evidence of the WinRM provider process.

---

## Sysmon Event ID 11 — File Creation

The controlled file-transfer activity generated Sysmon Event ID `11`.

Observed telemetry included:

```text
Target File:
C:\Users\Public\soc_lab_test.txt

User:
WINDOWS10\soc-lab

Image:
C:\Windows\system32\wsmprovhost.exe

Process ID:
3864

Event Record ID:
31865
```

This connected the WinRM provider process with the resulting file creation.

---

# Detection Engineering

Two custom Wazuh rules were developed and successfully validated.

## Rule 100003 — WinRM Provider Process

**Purpose:** Detect creation of `wsmprovhost.exe`.

**Parent Rule:** `61603`

**Telemetry:** Sysmon Event ID `1`

**MITRE ATT&CK:** T1021.006

Detection logic:

```text
Sysmon Event ID 1
        +
Image = wsmprovhost.exe
        ↓
Wazuh Rule 100003
        ↓
T1021.006
```

---

## Rule 100002 — WinRM File Creation

**Purpose:** Detect file creation through the WinRM provider in the Public directory.

**Parent Rule:** `61613`

**Telemetry:** Sysmon Event ID `11`

**MITRE ATT&CK:** T1105

Detection logic:

```text
Sysmon Event ID 11
        +
Image = wsmprovhost.exe
        +
Target path = C:\Users\Public\
        ↓
Wazuh Rule 100002
        ↓
T1105
```

---

# MITRE ATT&CK Mapping

| Technique | Name | Observed Activity |
|---|---|---|
| T1046 | Network Service Scanning | Nmap reconnaissance |
| T1021.006 | Windows Remote Management | Evil-WinRM remote session and `wsmprovhost.exe` |
| T1105 | Ingress Tool Transfer | Controlled file transfer |

---

# Detection Validation

The detection rules were tested by reproducing the corresponding behaviors inside the laboratory.

### Rule 100003

Successfully generated a Wazuh alert when `wsmprovhost.exe` was created during a fresh WinRM session.

### Rule 100002

Successfully generated a Wazuh alert when the controlled file transfer resulted in:

```text
C:\Users\Public\soc_lab_test.txt
```

being created by `wsmprovhost.exe`.

The detections were validated against actual telemetry generated by the lab rather than simulated alert data.

---

# False Positive Considerations

The custom detections are designed around the controlled laboratory scenario and would require additional tuning before production deployment.

Potential legitimate activity includes:

- Authorized WinRM administration
- Remote management automation
- Legitimate file creation through administrative processes
- Software deployment or administrative scripts

Potential tuning fields include:

- Source IP
- User account
- Command line
- Parent process
- Destination path
- Known administrative hosts
- Event frequency
- Related authentication events

Combining multiple telemetry conditions can improve detection confidence and reduce false positives.

---

# Investigation Findings

### Finding 1 — Remote Authentication

A successful NTLM network logon was observed from the Kali host to the Windows endpoint.

**Status:** Confirmed

---

### Finding 2 — WinRM Provider Activity

`wsmprovhost.exe` was created during the remote session.

**Status:** Confirmed

---

### Finding 3 — Controlled File Transfer

The benign test file was transferred to the Windows endpoint and generated Sysmon file-creation telemetry.

**Status:** Confirmed

---

### Finding 4 — Detection Validation

Both custom Wazuh detections successfully generated alerts when their corresponding behaviors were reproduced.

**Status:** Confirmed

---

# Limitations

This project did not perform or claim:

- Exploitation of a software vulnerability
- Credential theft
- Password cracking
- Confirmed Pass-the-Hash
- Malware execution
- Ransomware
- Persistence
- Destructive activity
- Activity against public systems

WinRM and the dedicated laboratory account were intentionally configured for the simulation.

The project therefore demonstrates **controlled adversary simulation and blue-team detection engineering**, not a real-world compromise.

---

# Project Structure

```text
Project-4_Adversary-Simulation-Blue-Team-Detection/
│
├── README.md
│
├── simulation/
│   ├── attack-simulation.md
│   └── commands.md
│
├── detection/
│   ├── winrm_file_transfer_rule.xml
│   └── winrm_process_creation_rule.xml
│
├── analysis/
│   ├── telemetry-analysis.md
│   └── mitre-mapping.md
│
├── evidence/
│   ├── evidence-summary.md
│   └── telemetry-observations.md
│
├── screenshots/
│
└── report/
    └── project4-investigation-report.md
```

---

# Skills Demonstrated

- SOC investigation
- Windows endpoint monitoring
- Sysmon analysis
- Windows Security Event analysis
- Wazuh SIEM
- Detection engineering
- Custom Wazuh rules
- MITRE ATT&CK mapping
- Network reconnaissance
- WinRM investigation
- Remote-access telemetry analysis
- File-transfer detection
- False-positive analysis
- Detection validation
- Security documentation

---

# Key Takeaways

This project demonstrates the complete transition from simulated adversary activity to blue-team detection:

```text
Adversary Behavior
        ↓
Windows Telemetry
        ↓
Sysmon / Security Events
        ↓
Wazuh Collection
        ↓
Detection Logic
        ↓
Alert
        ↓
Investigation
        ↓
MITRE ATT&CK
        ↓
Detection Tuning
```

The main lesson from the project is that effective SOC detection is not based on a single event.

Authentication telemetry, process creation, file creation, source information, and process relationships can be combined to build a stronger understanding of activity occurring on an endpoint.

---

## Disclaimer

This project was conducted in an isolated personal SOC laboratory for cybersecurity learning and detection-engineering practice.

All systems, accounts, and activities were intentionally configured and controlled for the purpose of the simulation.