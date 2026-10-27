# MITRE ATT&CK Mapping

## Project 4 — Adversary Simulation & Blue-Team Detection

| Technique | Name | Observed Activity | Evidence |
|---|---|---|---|
| T1046 | Network Service Scanning | Nmap reconnaissance against the Windows endpoint | Nmap scan targeting TCP 5985 |
| T1021.006 | Windows Remote Management | Controlled remote access using Evil-WinRM | WinRM session and `wsmprovhost.exe` telemetry |
| T1105 | Ingress Tool Transfer | Controlled transfer of `soc_lab_test.txt` to Windows | Sysmon Event ID 11 + Wazuh Rule 100002 |

---

## T1046 — Network Service Scanning

### Activity

Kali Linux performed network reconnaissance against:

`192.168.56.10`

The scan included TCP port `5985`, which is associated with WinRM.

### Evidence

The reconnaissance was performed using Nmap.

### Assessment

The activity demonstrates network service discovery against the isolated Windows lab endpoint.

**Confidence: High**

---

## T1021.006 — Windows Remote Management

### Activity

The simulation used Evil-WinRM to establish a remote PowerShell session with the Windows endpoint.

The session successfully authenticated using the dedicated lab account:

`soc_lab`

### Endpoint Evidence

Sysmon Event ID `1` recorded:

`C:\Windows\System32\wsmprovhost.exe`

with command line:

`C:\Windows\system32\wsmprovhost.exe -Embedding`

The Sysmon event identified the activity as:

`T1021.006 — Windows Remote Management`

### Wazuh Detection

Custom Rule:

`100003`

Purpose:

Detect creation of `wsmprovhost.exe`.

### Assessment

The evidence directly supports the use of Windows Remote Management during the controlled simulation.

**Confidence: High**

---

## T1105 — Ingress Tool Transfer

### Activity

A benign test file was hosted on Kali and retrieved by the Windows endpoint.

Source:

`192.168.56.105`

Destination:

`C:\Users\Public\soc_lab_test.txt`

### Endpoint Evidence

Sysmon Event ID `11` recorded the file creation.

The event identified:

- Image: `wsmprovhost.exe`
- User: `WINDOWS10\soc-lab`
- Target File: `C:\Users\Public\soc_lab_test.txt`

### Wazuh Detection

Custom Rule:

`100002`

Purpose:

Detect file creation through `wsmprovhost.exe` in the Public directory.

### Assessment

The controlled scenario demonstrates file transfer into the Windows endpoint.

The Sysmon event provides evidence of the resulting file creation, while the custom Wazuh rule identifies the specific process and destination-path combination.

**Confidence: High**

---

## Techniques Considered but Not Confirmed

### T1059 — Command and Scripting Interpreter

Remote PowerShell commands were executed during the WinRM session.

However, this project focuses its detection coverage on the WinRM access and file-transfer behaviors. No separate custom detection was created for PowerShell execution in this project.

Therefore, it is not included as a primary detection-engineering result.

### T1078 — Valid Accounts

A dedicated lab account was intentionally created for the simulation.

Although the account successfully authenticated, the project does not treat this as evidence of compromised credentials.

Therefore, Valid Accounts is not claimed as an adversary technique demonstrated through credential compromise.

### T1110.001 — Password Guessing

No brute-force or password-guessing activity was performed.

This technique is therefore excluded.

### T1053.005 — Scheduled Task/Job

No scheduled-task persistence was implemented.

This technique is therefore excluded.

---

## Overall ATT&CK Coverage

The validated Project 4 detection chain covers:

**T1046 → T1021.006 → T1105**

This represents:

**Reconnaissance → Remote Access → Controlled File Transfer**

The mapping is based on observed lab activity and collected telemetry rather than assumed attacker behavior.