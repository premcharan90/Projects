# Telemetry Observations

## 1. Windows Security Telemetry

### Event ID 4624

The remote WinRM authentication generated a successful Windows logon event.

Observed characteristics:

- Logon Type `3`
- NTLM authentication
- Source IP `192.168.56.105`
- Account `soc-lab`

This provided authentication evidence connecting the Kali host to the Windows endpoint.

---

## 2. Sysmon Event ID 1

The WinRM session resulted in the creation of:

`wsmprovhost.exe`

Observed process context:

```text
Image:
C:\Windows\System32\wsmprovhost.exe

Command Line:
C:\Windows\system32\wsmprovhost.exe -Embedding

Parent:
C:\Windows\System32\svchost.exe

User:
WINDOWS10\soc-lab
```

This telemetry provided endpoint-level evidence of the WinRM provider process.

---

## 3. Sysmon Event ID 11

The controlled file transfer resulted in a file creation event.

Observed target:

`C:\Users\Public\soc_lab_test.txt`

The process responsible for the file creation was:

`wsmprovhost.exe`

This connected the remote WinRM activity with the resulting file creation.

---

## 4. Wazuh Correlation

The raw Sysmon telemetry was received by Wazuh.

Custom Wazuh rules were then used to convert specific telemetry patterns into higher-level detections.

### File Transfer Detection

Rule `100002` matched:

```text
Sysmon Event ID 11
+
Image = wsmprovhost.exe
+
Target path under C:\Users\Public\
```

Result:

**Wazuh alert generated successfully.**

---

### WinRM Process Detection

Rule `100003` matched:

```text
Sysmon Event ID 1
+
Image = wsmprovhost.exe
```

Result:

**Wazuh alert generated successfully.**

---

## 5. Detection Chain

The telemetry demonstrates how different Windows logging sources can support a single investigation:

```text
Windows Security
    ↓
Successful remote authentication

Sysmon Event ID 1
    ↓
WinRM provider process

Sysmon Event ID 11
    ↓
File creation

Wazuh
    ↓
Custom detection

MITRE ATT&CK
    ↓
T1021.006 / T1105
```

---

## 6. Key Investigation Finding

The most useful correlation was the relationship between:

- Source IP `192.168.56.105`
- Account `soc-lab`
- WinRM authentication
- `wsmprovhost.exe`
- File creation in `C:\Users\Public\`

Together, these events provide a coherent timeline of the controlled remote-access and file-transfer activity.

No individual event should be interpreted beyond what its telemetry supports.

---

## 7. Detection Limitations

The detections are designed for this controlled lab and should not be considered production-ready without additional tuning.

Potential legitimate activity includes:

- Administrative WinRM sessions
- Remote management automation
- Legitimate file creation through administrative processes

Potential tuning fields include:

- Source IP
- User
- Command line
- Destination path
- Known management systems
- Process relationships
- Event frequency

Combining multiple telemetry conditions can improve confidence and reduce false positives.

---

## 8. Final Assessment

The collected telemetry successfully supports the investigation of the controlled simulation.

The strongest evidence consists of:

1. Windows Event ID 4624 for the successful network logon.
2. Sysmon Event ID 1 for `wsmprovhost.exe`.
3. Sysmon Event ID 11 for the controlled file creation.
4. Wazuh Rule `100002` for the file-transfer detection.
5. Wazuh Rule `100003` for the WinRM process detection.

These observations provide sufficient evidence to document the simulated behavior without claiming exploitation, credential theft, or confirmed Pass-the-Hash activity.