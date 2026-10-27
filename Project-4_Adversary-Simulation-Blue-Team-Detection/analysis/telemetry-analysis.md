# Telemetry Analysis

## 1. Overview

This analysis examines the telemetry generated during the controlled Project 4 adversary simulation.

The activity was performed entirely within the isolated SOC lab using Kali Linux as the simulation host, Windows 10 as the monitored endpoint, and Wazuh as the central monitoring platform.

The analysis focuses on:

- Network reconnaissance
- Successful WinRM authentication
- WinRM provider process creation
- Remote discovery activity
- Controlled file transfer
- Sysmon telemetry
- Wazuh detection and correlation

---

## 2. Network Reconnaissance

The simulation began with Nmap reconnaissance against the Windows endpoint.

Target:

`192.168.56.10`

The scan included TCP port `5985`, which is used by WinRM over HTTP.

The scan identified the WinRM service after it had been intentionally enabled for the simulation.

This activity represents network service discovery and is mapped to:

**MITRE ATT&CK T1046 — Network Service Scanning**

The reconnaissance established that the endpoint exposed the service required for the controlled remote-access phase.

---

## 3. WinRM Remote Access

A dedicated temporary lab account, `soc_lab`, was used to authenticate to the Windows endpoint through Evil-WinRM.

The session successfully reached:

`C:\Users\soc_lab\Documents`

Remote discovery commands were then executed:

- `whoami`
- `hostname`
- `Get-Location`
- `Get-ChildItem`

The activity demonstrates controlled remote access through WinRM.

This is mapped to:

**MITRE ATT&CK T1021.006 — Windows Remote Management**

No vulnerability exploitation was performed. The WinRM service and dedicated lab account were intentionally configured for the simulation.

---

## 4. Windows Security Telemetry

The successful remote authentication generated Windows Security Event ID `4624`.

Important observed fields included:

- Logon Type: `3`
- Account: `soc-lab`
- Source IP: `192.168.56.105`
- Authentication Package: `NTLM`
- Logon Process: `NtLmSsp`
- Channel: `Security`
- Target: `Windows10`

Wazuh generated Rule `92652`, which described the event as a successful remote logon using NTLM and noted the possibility of pass-the-hash activity.

However, the telemetry does **not** prove that a stolen password hash was used.

The evidence supports the conclusion that a successful NTLM network logon occurred from the Kali host.

Therefore, this investigation does not classify the activity as confirmed Pass-the-Hash.

---

## 5. WinRM Provider Process Creation

Sysmon Event ID `1` recorded the creation of:

`C:\Windows\System32\wsmprovhost.exe`

Observed context included:

- User: `WINDOWS10\soc-lab`
- Command Line: `C:\Windows\system32\wsmprovhost.exe -Embedding`
- Parent Image: `C:\Windows\System32\svchost.exe`
- Parent User: `NT AUTHORITY\SYSTEM`
- Integrity Level: `High`

The Sysmon event contained:

`technique_id=T1021.006,technique_name=Windows Remote Management`

The event provides endpoint-level evidence of the WinRM provider process associated with the remote session.

A custom Wazuh rule, `100003`, was created to detect `wsmprovhost.exe` process creation.

The rule successfully generated a Wazuh alert and mapped the activity to:

**T1021.006 — Windows Remote Management**

---

## 6. Controlled File Transfer

A benign test file named:

`soc_lab_test.txt`

was hosted from the Kali machine using a temporary Python HTTP server.

The Windows endpoint retrieved the file using:

`Invoke-WebRequest`

The destination was:

`C:\Users\Public\soc_lab_test.txt`

This created Sysmon Event ID `11` — File Create.

Observed telemetry included:

- Target File: `C:\Users\Public\soc_lab_test.txt`
- User: `WINDOWS10\soc-lab`
- Image: `C:\Windows\system32\wsmprovhost.exe`
- Process ID: `3864`
- Event Record ID: `31865`

This demonstrates the telemetry chain:

Kali HTTP server  
→ WinRM remote session  
→ Windows file retrieval  
→ File creation  
→ Sysmon Event ID 11  
→ Wazuh telemetry  
→ Custom Wazuh detection

The controlled transfer scenario was mapped to:

**MITRE ATT&CK T1105 — Ingress Tool Transfer**

The Sysmon event itself records file creation; the T1105 mapping represents the behavior demonstrated by the controlled simulation.

---

## 7. Custom Wazuh File Transfer Detection

Wazuh Rule `100002` was created to identify a file creation event where:

- The process image is `wsmprovhost.exe`
- The destination is under `C:\Users\Public\`

The rule successfully generated an alert during the controlled transfer test.

The rule was mapped to:

**T1105 — Ingress Tool Transfer**

This demonstrates how existing endpoint telemetry can be converted into a higher-confidence detection using process and file-path conditions.

---

## 8. Detection Engineering Outcome

Two custom Wazuh detections were created and validated:

### Rule 100002

**Purpose:** Detect file creation through the WinRM provider in the Public directory.

Parent rule:

`61613`

Telemetry:

`Sysmon Event ID 11 — File Create`

MITRE mapping:

`T1105`

### Rule 100003

**Purpose:** Detect creation of the WinRM provider process.

Parent rule:

`61603`

Telemetry:

`Sysmon Event ID 1 — Process Creation`

MITRE mapping:

`T1021.006`

Both rules were successfully validated using activity generated inside the lab.

---

## 9. Investigation Assessment

The simulation demonstrated how multiple telemetry sources can be combined to investigate remote activity.

The investigation chain was:

1. Nmap identified the WinRM service.
2. Evil-WinRM established a controlled remote session.
3. Windows Security Event ID 4624 recorded the successful network logon.
4. Sysmon Event ID 1 recorded `wsmprovhost.exe`.
5. Remote discovery commands were executed.
6. A controlled file transfer generated Sysmon Event ID 11.
7. Wazuh correlated the telemetry into custom detections.
8. The resulting activity was mapped to relevant MITRE ATT&CK techniques.

The evidence supports detection of the simulated behavior without claiming exploitation, credential theft, or confirmed Pass-the-Hash activity.

---

## 10. Detection Limitations and Tuning

The custom detections are intentionally designed for the controlled lab and may produce false positives in a production environment.

For example, `wsmprovhost.exe` can legitimately appear during administrative WinRM activity.

Similarly, file creation in `C:\Users\Public\` can occur during legitimate administration or automation.

Potential production tuning could include:

- Source IP
- User account
- Parent process
- Command line
- Known administrative hosts
- Destination path
- Frequency of activity
- Combination of multiple related events

The goal would be to increase detection confidence while reducing legitimate administrative activity being treated as suspicious.

---

## 11. Conclusion

The Project 4 simulation successfully demonstrated a controlled remote-access scenario and the corresponding blue-team investigation workflow.

The strongest evidence came from Windows Security and Sysmon telemetry collected by Wazuh.

The project also demonstrated the transition from raw telemetry to actionable detection logic through custom Wazuh rules and MITRE ATT&CK mapping.