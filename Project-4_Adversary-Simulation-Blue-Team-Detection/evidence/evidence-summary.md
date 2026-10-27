# Evidence Summary

## Project 4 — Adversary Simulation & Blue-Team Detection

This directory documents the technical evidence collected during the controlled adversary simulation.

The evidence was generated within the isolated SOC lab consisting of:

- Kali Linux — `192.168.56.105`
- Windows 10 endpoint — `192.168.56.10`
- Wazuh server — `192.168.56.20`

No public systems or external targets were involved.

---

## 1. Network Reconnaissance Evidence

### Activity

Nmap was used from Kali Linux to identify the WinRM service on the Windows endpoint.

### Target

`192.168.56.10`

### Relevant Port

`5985/tcp` — WinRM HTTP

### Purpose

The scan established whether the service required for the controlled remote-access simulation was reachable.

### ATT&CK Mapping

**T1046 — Network Service Scanning**

---

## 2. WinRM Access Evidence

### Activity

A dedicated temporary lab account named `soc_lab` was used to establish a remote WinRM session through Evil-WinRM.

### Remote Session

The session reached:

`C:\Users\soc_lab\Documents`

### Discovery Commands

The following commands were executed:

- `whoami`
- `hostname`
- `Get-Location`
- `Get-ChildItem`

### Observed Results

The remote session identified:

- User: `Windows10\soc_lab`
- Host: `Windows10`
- Working directory: `C:\Users\soc_lab\Documents`

### ATT&CK Mapping

**T1021.006 — Windows Remote Management**

---

## 3. Windows Security Event 4624 Evidence

A successful Windows network logon generated Security Event ID `4624`.

### Relevant Fields

| Field | Observed Value |
|---|---|
| Event ID | 4624 |
| Logon Type | 3 |
| Account | `soc-lab` |
| Source IP | `192.168.56.105` |
| Authentication | NTLM |
| Logon Process | `NtLmSsp` |
| Channel | Security |
| Target | `Windows10` |

### Wazuh

Wazuh generated Rule `92652` for the successful remote logon.

The rule description mentioned possible Pass-the-Hash activity.

### Assessment

The evidence confirms a successful NTLM network logon from the Kali host.

It does **not** independently prove that a stolen password hash was used.

Therefore, the project does not classify this event as confirmed Pass-the-Hash activity.

---

## 4. Sysmon Process Creation Evidence

Sysmon Event ID `1` recorded the creation of:

`C:\Windows\System32\wsmprovhost.exe`

### Relevant Fields

| Field | Observed Value |
|---|---|
| Event ID | 1 |
| Image | `C:\Windows\System32\wsmprovhost.exe` |
| User | `WINDOWS10\soc-lab` |
| Command Line | `C:\Windows\system32\wsmprovhost.exe -Embedding` |
| Parent Image | `C:\Windows\System32\svchost.exe` |
| Parent User | `NT AUTHORITY\SYSTEM` |
| Integrity Level | High |

The Sysmon event contained the metadata:

`technique_id=T1021.006,technique_name=Windows Remote Management`

### Wazuh Detection

Custom Rule:

`100003`

Purpose:

Detect creation of the WinRM provider process `wsmprovhost.exe`.

### ATT&CK Mapping

**T1021.006 — Windows Remote Management**

---

## 5. Controlled File Transfer Evidence

A benign test file was created on Kali:

`soc_lab_test.txt`

The file was hosted through a temporary Python HTTP server.

The Windows endpoint retrieved the file using `Invoke-WebRequest`.

### Destination

`C:\Users\Public\soc_lab_test.txt`

### Sysmon Evidence

Sysmon Event ID `11` recorded the resulting file creation.

Relevant fields included:

| Field | Observed Value |
|---|---|
| Event ID | 11 |
| Target File | `C:\Users\Public\soc_lab_test.txt` |
| User | `WINDOWS10\soc-lab` |
| Image | `C:\Windows\system32\wsmprovhost.exe` |
| Process ID | `3864` |
| Event Record ID | `31865` |

### Wazuh Detection

Custom Rule:

`100002`

Purpose:

Detect file creation through `wsmprovhost.exe` in the Public directory.

### ATT&CK Mapping

**T1105 — Ingress Tool Transfer**

The mapping represents the controlled file-transfer behavior demonstrated by the simulation. Sysmon itself records the resulting file creation event.

---

## 6. Detection Evidence

Two custom Wazuh rules were successfully validated.

### Rule 100002

**Detection:** WinRM provider creates a file in the Public directory.

**Parent Rule:** `61613`

**Telemetry:** Sysmon Event ID 11

**MITRE:** T1105

---

### Rule 100003

**Detection:** WinRM provider process creation.

**Parent Rule:** `61603`

**Telemetry:** Sysmon Event ID 1

**MITRE:** T1021.006

---

## 7. Evidence Chain

The collected evidence demonstrates the following sequence:

```text
Nmap reconnaissance
        ↓
WinRM service identified
        ↓
Evil-WinRM remote session
        ↓
Windows Event ID 4624
        ↓
wsmprovhost.exe process creation
        ↓
Remote discovery
        ↓
Controlled file transfer
        ↓
Sysmon Event ID 11
        ↓
Wazuh custom detection
        ↓
MITRE ATT&CK mapping
```

---

## 8. Evidence Integrity

All activity was performed against the intentionally configured Windows 10 laboratory endpoint.

The test file used during the transfer was benign and created specifically for the simulation.

No malware, ransomware, credential theft, public targets, or destructive activity was used.

The evidence is therefore representative of a controlled SOC training scenario rather than a real-world compromise.