## Detection Objective

This project demonstrates the process of developing and validating a platform-independent Sigma detection rule based on Windows process-creation telemetry.

The detection focuses on the behavior of `cmd.exe` being spawned directly by `powershell.exe`.

### Detection Logic

The Sigma rule identifies the following parent-child process relationship:

```text
powershell.exe
      ↓
cmd.exe
```

The rule uses two conditions:

- `Image|endswith: '\cmd.exe'`
- `ParentImage|endswith: '\powershell.exe'`

Both conditions must be satisfied for the rule logic to match.

## Testing

### Positive Test

A controlled test was performed from PowerShell:

```powershell
cmd.exe /c whoami
```

The resulting Sysmon Event ID 1 (Process Create) was inspected and showed:

- `Image` → `cmd.exe`
- `ParentImage` → `powershell.exe`

The observed event therefore matches the conditions defined in the Sigma rule.

### Negative Test

A separate controlled test was performed by launching `cmd.exe` directly from the Windows desktop environment and executing:

```cmd
whoami
```

The resulting Sysmon Event ID 1 showed:

- `Image` → `cmd.exe`
- `ParentImage` → `explorer.exe`

This event does not satisfy the Sigma rule because the parent process is not `powershell.exe`.

These positive and negative tests demonstrate that the detection logic specifically focuses on the PowerShell-to-Command-Shell parent-child relationship rather than simply detecting the execution of `cmd.exe`.

## Sigma Rule Validation

The Sigma rule was validated using Sigma CLI.

Validation completed successfully without syntax errors.

The rule was not deployed as an active Sigma detection in Wazuh. The testing performed in this project evaluates the rule definition against observed Sysmon telemetry rather than claiming that Sigma generated a Wazuh alert.

## MITRE ATT&CK Mapping

**T1059.003 — Windows Command Shell**

The rule is mapped to the Windows Command Shell sub-technique of Command and Scripting Interpreter because the detection specifically identifies execution of `cmd.exe`.

## False Positive Considerations

PowerShell spawning `cmd.exe` can happen during legitimate administrative activity.

This means the detection could also match some normal activity in a real company environment.

The detection could be made more specific by considering additional information such as the command being executed or the user who started the process..