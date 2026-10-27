# Attack Simulation

## Overview

This project simulates a controlled remote-access scenario in an isolated cybersecurity lab. The objective was to reproduce a realistic sequence of reconnaissance, remote access, remote discovery, and controlled file transfer from a Kali Linux system against a Windows 10 endpoint, while monitoring the resulting activity with Sysmon and Wazuh.

The simulation was performed entirely within the lab environment using intentionally configured infrastructure and a dedicated lab account.

No public systems, production infrastructure, malware, ransomware, or real-world targets were involved.

---

## Lab Architecture

```text
Kali Linux
192.168.56.105
      |
      | Host-only network
      |
      v
Windows 10
192.168.56.10
      |
      | Sysmon + Wazuh Agent
      |
      v
Ubuntu Wazuh Server
192.168.56.20
```

### Systems

| System | Role | IP Address |
|---|---|---|
| Kali Linux | Red-team simulation host | `192.168.56.105` |
| Windows 10 | Target endpoint | `192.168.56.10` |
| Ubuntu Server | Wazuh server | `192.168.56.20` |

The Windows endpoint was monitored using Sysmon and the Wazuh Agent. Wazuh was used for centralized telemetry collection, investigation, and custom detection.

---

## Simulation Objectives

The simulation focused on the following behaviors:

1. Identify the Windows endpoint and exposed services.
2. Identify the WinRM service.
3. Establish controlled remote access through WinRM.
4. Perform basic remote host discovery.
5. Transfer a benign test file to the Windows endpoint.
6. Observe the resulting Windows and Sysmon telemetry.
7. Verify that Wazuh receives the telemetry.
8. Validate custom detections for the observed behaviors.

---

## Phase 1 — Network Reconnaissance

The simulation began with Nmap reconnaissance against the Windows endpoint.

```bash
nmap -Pn -sV -p 5985 192.168.56.10
```

The scan identified TCP port `5985` as open:

```text
5985/tcp open http Microsoft HTTPAPI httpd 2.0
Service Info: OS: Windows
```

TCP port 5985 is associated with HTTP-based Windows Remote Management (WinRM).

### MITRE ATT&CK

**T1046 — Network Service Scanning**

The reconnaissance phase demonstrated service discovery against the isolated Windows endpoint.

---

## Phase 2 — Controlled WinRM Remote Access

A dedicated lab account named `soc_lab` was created specifically for the simulation.

WinRM was intentionally enabled on the Windows endpoint and configured with an HTTP listener on TCP port 5985.

Remote access was established from Kali using Evil-WinRM:

```bash
evil-winrm -i 192.168.56.10 -u soc_lab
```

The session successfully connected to the Windows endpoint.

The remote PowerShell session was represented by the Windows process:

```text
wsmprovhost.exe
```

This process was subsequently observed through Sysmon Event ID 1 and forwarded to Wazuh.

### MITRE ATT&CK

**T1021.006 — Windows Remote Management**

The activity demonstrates controlled remote access through WinRM in an intentionally configured laboratory environment.

This should not be interpreted as exploitation of a Windows vulnerability.

---

## Phase 3 — Remote Discovery

After establishing the WinRM session, basic host and session information was collected:

```powershell
whoami
hostname
Get-Location
Get-ChildItem
```

The commands confirmed the authenticated lab user, Windows hostname, current working directory, and directory contents.

The activity was limited to basic discovery and did not involve credential theft, privilege escalation, or persistence.

---

## Phase 4 — Controlled File Transfer

A benign test file was created on the Kali system:

```bash
echo "Project 4 controlled file transfer test" > ~/soc_lab_test.txt
```

A temporary HTTP server was started on Kali:

```bash
cd ~
python3 -m http.server 8000 --bind 192.168.56.105
```

From the Windows WinRM session, the file was downloaded into the Windows Public directory:

```powershell
Invoke-WebRequest -Uri "http://192.168.56.105:8000/soc_lab_test.txt" -OutFile "C:\Users\Public\soc_lab_test.txt"
```

The resulting file was verified on Windows:

```powershell
Get-Item "C:\Users\Public\soc_lab_test.txt"
```

This was a controlled transfer of a benign test file.

### MITRE ATT&CK

**T1105 — Ingress Tool Transfer**

The activity was mapped to T1105 because the simulation involved transferring a file from the Kali system to the Windows endpoint.

---

## Phase 5 — Windows Security Telemetry

The successful WinRM connection generated Windows Security Event ID 4624 telemetry.

The observed event included:

- Logon Type: `3`
- Account: `soc_lab`
- Source IP: `192.168.56.105`
- Authentication: `NTLM`
- Logon Process: `NtLmSsp`

Wazuh generated an alert for the remote logon.

The Wazuh alert description included wording referring to a possible Pass-the-Hash attack. However, the underlying telemetry only established that a successful NTLM network logon occurred.

Therefore, this project does **not** claim that Pass-the-Hash was confirmed.

---

## Phase 6 — Sysmon Process Creation Telemetry

The WinRM session resulted in a Sysmon Event ID 1 process-creation event for:

```text
C:\Windows\System32\wsmprovhost.exe
```

The observed process included:

```text
User: WINDOWS10\soc-lab
CommandLine: C:\Windows\system32\wsmprovhost.exe -Embedding
ParentImage: C:\Windows\System32\svchost.exe
ParentUser: NT AUTHORITY\SYSTEM
IntegrityLevel: High
```

The Sysmon telemetry identified the activity with:

```text
T1021.006 — Windows Remote Management
```

The same telemetry was subsequently observed in Wazuh.

---

## Phase 7 — Sysmon File Creation Telemetry

The controlled file transfer resulted in a Sysmon Event ID 11 file-creation event.

The observed file was:

```text
C:\Users\Public\soc_lab_test.txt
```

The event included:

```text
Image: C:\Windows\system32\wsmprovhost.exe
User: WINDOWS10\soc-lab
```

This demonstrated the telemetry chain from the controlled transfer to Windows file creation and Sysmon logging.

---

## Phase 8 — Wazuh Detection Engineering

Two custom Wazuh detections were created and validated using the observed telemetry.

### Rule 100002 — Controlled File Transfer

The rule identifies Sysmon file-creation telemetry where:

- The process is `wsmprovhost.exe`
- The target file is created under `C:\Users\Public\`

The rule was mapped to:

**T1105 — Ingress Tool Transfer**

The rule was successfully triggered during the controlled file-transfer test.

---

### Rule 100003 — WinRM Process Creation

The second detection identifies Sysmon Event ID 1 telemetry where the created process is:

```text
wsmprovhost.exe
```

The rule inherits from the Wazuh Sysmon Event ID 1 rule and was mapped to:

**T1021.006 — Windows Remote Management**

The rule was successfully triggered during a new WinRM connection.

---

## Simulation Outcome

The complete controlled activity demonstrated the following detection chain:

```text
Kali Linux
    |
    | Nmap reconnaissance
    v
Windows 10
    |
    | WinRM authentication
    v
wsmprovhost.exe
    |
    | Sysmon Event ID 1
    v
Wazuh
    |
    | Custom Rule 100003
    v
T1021.006 Detection
```

And for the controlled transfer:

```text
Kali Linux
    |
    | HTTP file transfer
    v
Windows 10
    |
    | File creation
    v
Sysmon Event ID 11
    |
    v
Wazuh
    |
    | Custom Rule 100002
    v
T1105 Detection
```

The simulation successfully demonstrated how controlled remote-access activity can generate endpoint telemetry and how that telemetry can be used to develop and validate SOC detections.

---

## Safety and Scope

This simulation was conducted in an isolated lab environment.

The project intentionally excluded:

- Real-world targets
- Public infrastructure
- Malware
- Ransomware
- Credential theft
- Credential dumping
- Unnecessary persistence
- Destructive actions
- Unverified exploitation claims

The `soc_lab` account was created specifically for the laboratory exercise.

All transferred files were benign test files.

---

## Limitations

The project demonstrates detection engineering against a controlled laboratory scenario. The detections should not be considered complete enterprise-grade detection logic.

In a production environment, additional context could be incorporated, including:

- Source IP reputation
- User identity and role
- Process command line
- Parent-child process relationships
- Destination host context
- Authentication type
- Frequency and timing of events
- Administrative activity baselines
- Known management systems and automation accounts

The Wazuh remote-logon alert mentioning possible Pass-the-Hash was treated as an investigation lead rather than proof of credential abuse because the available telemetry did not establish that a stolen credential hash was used.

---

## Result

The simulation successfully connected adversary-style activity with defensive telemetry and detection engineering:

**Reconnaissance → Remote Access → Discovery → File Transfer → Endpoint Telemetry → Wazuh Investigation → Custom Detection → MITRE ATT&CK Mapping**