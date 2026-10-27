# Project 4 — Adversary Simulation & Blue-Team Detection

## Investigation Report

**Environment:** Isolated SOC Lab  
**Simulation Host:** Kali Linux — `192.168.56.105`  
**Monitored Endpoint:** Windows 10 — `192.168.56.10`  
**SIEM:** Wazuh — `192.168.56.20`

---

## 1. Executive Summary

This project simulated a controlled remote-access scenario against an intentionally configured Windows 10 laboratory endpoint.

The simulation began with network reconnaissance from Kali Linux, followed by remote access through Windows Remote Management (WinRM) using a dedicated laboratory account.

After establishing the remote session, basic host discovery was performed and a benign test file was transferred to the Windows endpoint.

Windows Security logs and Sysmon telemetry were collected by Wazuh. The resulting telemetry was investigated and used to develop and validate custom Wazuh detections.

The primary behaviors demonstrated were:

- Network service scanning
- Windows Remote Management
- Remote host discovery
- Controlled file transfer
- Endpoint process creation
- File creation telemetry
- SIEM-based detection engineering

The activity was performed entirely within the isolated SOC laboratory.

---

## 2. Scope

The investigation covered activity between:

**Kali Linux → Windows 10 → Wazuh**

### Systems

| System | IP Address | Role |
|---|---|---|
| Kali Linux | `192.168.56.105` | Simulation host |
| Windows 10 | `192.168.56.10` | Monitored endpoint |
| Ubuntu/Wazuh | `192.168.56.20` | SIEM and monitoring |

### Technologies

- Kali Linux
- Nmap
- Evil-WinRM
- Windows 10
- WinRM
- Sysmon
- Windows Security Event Logs
- Wazuh

---

## 3. Simulation Objective

The objective was to demonstrate how a SOC team could detect and investigate remote administrative activity using endpoint telemetry.

The simulation was designed to produce observable security telemetry rather than perform destructive actions.

The investigation focused on identifying:

1. Network reconnaissance
2. Remote authentication
3. WinRM process activity
4. Remote discovery
5. Controlled file transfer
6. Corresponding Sysmon telemetry
7. Wazuh detections

---

## 4. Attack Simulation Timeline

### Phase 1 — Reconnaissance

Nmap was used from Kali Linux to scan the Windows endpoint.

Target:

`192.168.56.10`

TCP port `5985` was specifically checked because it is associated with WinRM over HTTP.

**ATT&CK:** T1046 — Network Service Scanning

---

### Phase 2 — Remote Access

A dedicated temporary laboratory account, `soc_lab`, was configured on the Windows endpoint.

WinRM was intentionally enabled for the simulation.

Evil-WinRM was then used to establish the remote session.

The session successfully reached:

`C:\Users\soc_lab\Documents`

**ATT&CK:** T1021.006 — Windows Remote Management

---

### Phase 3 — Remote Discovery

The following commands were executed inside the remote session:

```powershell
whoami
hostname
Get-Location
Get-ChildItem
```

Observed results identified:

- User: `Windows10\soc_lab`
- Host: `Windows10`
- Location: `C:\Users\soc_lab\Documents`

This activity demonstrated basic post-access discovery within the controlled endpoint.

---

### Phase 4 — Authentication Telemetry

The remote authentication generated Windows Security Event ID `4624`.

Relevant characteristics included:

- Logon Type: `3`
- Account: `soc-lab`
- Source IP: `192.168.56.105`
- Authentication: `NTLM`
- Logon Process: `NtLmSsp`

Wazuh generated Rule `92652`.

The Wazuh rule description referenced possible Pass-the-Hash activity.

However, the available evidence only proves a successful NTLM network logon.

**Pass-the-Hash was not confirmed.**

---

### Phase 5 — WinRM Process Creation

Sysmon Event ID `1` recorded:

`C:\Windows\System32\wsmprovhost.exe`

Observed process context:

- User: `WINDOWS10\soc-lab`
- Command Line: `C:\Windows\system32\wsmprovhost.exe -Embedding`
- Parent: `C:\Windows\System32\svchost.exe`
- Parent User: `NT AUTHORITY\SYSTEM`
- Integrity Level: `High`

This provided endpoint evidence of the WinRM provider process.

A custom Wazuh detection was created:

**Rule 100003 — Project 4: WinRM provider process created - wsmprovhost.exe**

**ATT&CK:** T1021.006

---

### Phase 6 — Controlled File Transfer

A benign file named:

`soc_lab_test.txt`

was hosted from Kali using a temporary Python HTTP server.

The Windows endpoint retrieved the file using:

```powershell
Invoke-WebRequest
```

The file was written to:

`C:\Users\Public\soc_lab_test.txt`

---

### Phase 7 — File Creation Telemetry

Sysmon Event ID `11` recorded the resulting file creation.

Relevant fields included:

- Target File: `C:\Users\Public\soc_lab_test.txt`
- User: `WINDOWS10\soc-lab`
- Image: `C:\Windows\system32\wsmprovhost.exe`
- Process ID: `3864`
- Event Record ID: `31865`

This provided endpoint evidence connecting the WinRM provider process to the resulting file creation.

---

### Phase 8 — Wazuh Detection

A custom Wazuh rule was created to identify the specific telemetry pattern.

**Rule:** `100002`

Conditions:

- Sysmon Event ID `11`
- Image ending in `wsmprovhost.exe`
- Target path under `C:\Users\Public\`

The rule successfully generated a Wazuh alert during the controlled transfer test.

**ATT&CK:** T1105 — Ingress Tool Transfer

---

## 5. Detection Engineering

Two custom Wazuh detections were implemented.

### Detection 1 — WinRM Provider Process

**Rule ID:** `100003`

**Parent Rule:** `61603`

**Telemetry:** Sysmon Event ID `1`

**Detection Logic:**

```text
Sysmon Process Creation
        +
Image = wsmprovhost.exe
        ↓
Wazuh Rule 100003
```

**MITRE ATT&CK:** T1021.006

---

### Detection 2 — WinRM File Creation

**Rule ID:** `100002`

**Parent Rule:** `61613`

**Telemetry:** Sysmon Event ID `11`

**Detection Logic:**

```text
Sysmon File Create
        +
Image = wsmprovhost.exe
        +
Target path = C:\Users\Public\
        ↓
Wazuh Rule 100002
```

**MITRE ATT&CK:** T1105

---

## 6. MITRE ATT&CK Mapping

| Technique | Name | Evidence |
|---|---|---|
| T1046 | Network Service Scanning | Nmap reconnaissance |
| T1021.006 | Windows Remote Management | Evil-WinRM session and `wsmprovhost.exe` |
| T1105 | Ingress Tool Transfer | Controlled file transfer and resulting file creation |

---

## 7. Investigation Findings

### Finding 1 — WinRM Remote Access

The Windows endpoint accepted a remote WinRM connection from the Kali host.

Evidence included:

- Successful Security Event ID `4624`
- Source IP `192.168.56.105`
- NTLM authentication
- `wsmprovhost.exe` process creation

**Assessment:** Confirmed within the controlled laboratory.

---

### Finding 2 — WinRM Provider Process

The remote session resulted in creation of:

`wsmprovhost.exe`

The process telemetry provided strong endpoint evidence of WinRM activity.

**Assessment:** Confirmed.

---

### Finding 3 — Controlled File Transfer

The simulation successfully transferred a benign file from Kali to the Windows endpoint.

The resulting file creation was recorded by Sysmon Event ID `11`.

**Assessment:** Confirmed.

---

### Finding 4 — Detection Validation

Both custom Wazuh rules successfully generated alerts when the corresponding controlled behaviors were reproduced.

**Assessment:** Detection logic successfully validated in the laboratory.

---

## 8. False Positive Considerations

The detections are intentionally focused on the controlled lab scenario and require additional tuning before production deployment.

`wsmprovhost.exe` can legitimately be created during authorized WinRM administration.

Similarly, file creation under `C:\Users\Public\` can occur during legitimate administration, software deployment, or automation.

Potential tuning opportunities include:

- Source IP
- User account
- Command line
- Parent process
- Destination path
- Known administrative hosts
- Event frequency
- Related authentication events

Combining multiple telemetry conditions could increase detection confidence and reduce false positives.

---

## 9. Limitations

This project did not attempt to demonstrate:

- Exploitation of a software vulnerability
- Credential theft
- Password cracking
- Confirmed Pass-the-Hash
- Malware execution
- Ransomware
- Persistence
- Destructive actions
- Activity against public systems

The WinRM service and laboratory account were intentionally configured to enable the controlled simulation.

Therefore, the project demonstrates adversary behavior simulation and blue-team detection rather than a real-world compromise.

---

## 10. Blue-Team Response Perspective

If the observed activity occurred on a production endpoint, an analyst could investigate:

1. Source IP associated with the remote logon.
2. Account responsible for the authentication.
3. Whether WinRM access was expected.
4. `wsmprovhost.exe` process creation.
5. Command-line activity associated with the remote session.
6. Files created during the session.
7. Other events occurring around the same timestamp.
8. Whether the source host is an authorized management system.

If the activity were unauthorized, containment could include isolating the endpoint, disabling or restricting the affected account, reviewing WinRM exposure, and investigating related endpoints.

---

## 11. Conclusion

The Project 4 simulation demonstrated an end-to-end SOC workflow:

```text
Reconnaissance
      ↓
Remote Access
      ↓
Authentication Telemetry
      ↓
Process Telemetry
      ↓
Controlled File Transfer
      ↓
File Creation Telemetry
      ↓
Wazuh Detection
      ↓
Investigation
      ↓
MITRE ATT&CK Mapping
```

The project successfully demonstrated how Windows Security logs and Sysmon telemetry can be collected through Wazuh and converted into actionable detection logic.

The two custom detections provide focused coverage for WinRM provider process creation and controlled file creation through the WinRM provider.

All conclusions in this report are based on activity observed within the isolated SOC laboratory.