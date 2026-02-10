# LPM - Local Performance Monitor

A comprehensive Windows system information collector and reporting tool built with Python and PowerShell.

> **Latest Version:** Enhanced with secure credentials, section filtering, and improved formatting

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![Windows](https://img.shields.io/badge/windows-10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

### Core Collection
- **OS & System Information** - Windows version, manufacturer, serial number
- **CPU Details** - Processor name, cores, clock speed, cache
- **GPU Information** - Graphics card, memory, driver version
- **Disk Information** - Logical drives, physical disks, capacity, free space
- **Network Configuration** - IP addresses, DNS, gateways, interface status
- **Running Processes** - Total count and details
- **Installed Programs** - Software inventory with automatic deduplication
- **Services** - Windows services with state and start mode
- **System Hotfixes** - Recent Windows updates
- **Network Connectivity** - Ping test results with latency

### Export Formats
- **JSON** - Structured data for APIs and dashboards
- **CSV** - Tabular format for spreadsheet analysis
- **XML** - Validated output for legacy systems

### Security Features
- **Secure Credentials** - Interactive prompts with hidden input (no CLI exposure)
- **Data Sanitization** - Automatic cleanup of invalid characters
- **Selective Export** - Control exactly which sections are included

### UX Enhancements
- **Smart Summaries** - Large datasets summarized in terminal
- **Percentages** - Disk/memory usage shown as percentages
- **Section Filtering** - Export only relevant information
- **Clear Output** - Organized, easy-to-read formatting

---

## Installation

### Option 1: MSI Installer (Recommended)
Download `LPM installer.msi` from [Releases](https://github.com/thompog/LPM/releases) and run it.

The installer will:
- Install LPM to your local application folder
- Install required Python modules
- Create desktop shortcut
- Set up per-user configuration

### Option 2: Manual Installation
1. **Requirements:**
   - Python 3.7 or later
   - pip (Python package manager)

2. **Clone/Download:**
   ```bash
   git clone https://github.com/thompog/LPM.git
   cd LPM
   ```

3. **Install Dependencies:**
   ```bash
   pip install psutil py-cpuinfo
   ```

4. **Run:**
   ```bash
   python LPM.py --run-collector
   ```

---

## Quick Start

### Basic Usage
```bash
# Collect and display system information
python LPM.py --run-collector

# Export to JSON
python LPM.py --json-out system_report.json

# Export to all formats
python LPM.py --json-out report.json --csv-out report.csv --xml-out report.xml
```

### Secure Upload
```bash
# Prompt for credentials securely (best practice)
python LPM.py --upload https://api.example.com --prompt-creds

# Interactive session:
# > Auth type (bearer/basic) [bearer]: bearer
# > Bearer token: ████████████████ (hidden input)
```

### Selective Export
```bash
# Export only CPU and GPU information
python LPM.py --sections "CPU,GPU" --json-out hardware.json

# Export disk information to CSV
python LPM.py --sections "Disk" --csv-out storage.csv

# Multiple sections
python LPM.py --sections "OS & System,CPU,Memory,Network" --json-out filtered.json
```

---

## Available Sections

Use these names with `--sections` flag:

```
General              # Timestamp, user, directory
OS & System          # Windows version, specs
CPU(s)               # Processor details
GPU(s)               # Graphics information
Disks (Logical)      # Drive letters, capacity
Physical Disks       # Physical drives
Network              # IP, DNS configuration
Network Adapters     # Interface status
System Uptime        # Boot time, uptime
Processes            # Running processes
Installed Hotfixes   # System updates
Installed Programs   # Software inventory (up to 200)
Services             # Windows services
Ping Test            # Network connectivity
```

Example: `--sections "CPU,Memory,Network"`

---

## Command-Line Options

```bash
python LPM.py [OPTIONS]

Options:
  --run-collector              Run system collector first
  --wait SECONDS               Seconds to wait for collector (default: 30)
  --json-out PATH              Export to JSON file
  --csv-out PATH               Export to CSV file
  --xml-out PATH               Export to XML file
  --upload URL                 POST results to HTTP endpoint
  --prompt-creds               Prompt for upload credentials (SECURE)
  --upload-bearer TOKEN        Bearer token auth (exposed - use --prompt-creds instead)
  --upload-user USER           Basic auth username (exposed - use --prompt-creds instead)
  --upload-pass PASS           Basic auth password (exposed - use --prompt-creds instead)
  --sections LIST              Filter sections (comma-separated)
  --help                       Show help message
```

---

## Example Workflows

### System Audit Report
```bash
python LPM.py --run-collector \
  --sections "OS & System,CPU,GPU,Memory,Disk" \
  --json-out audit_$(date +%Y%m%d).json
```

### Network Inventory
```bash
python LPM.py --sections "Network,Network Adapters" \
  --csv-out network_inventory.csv
```

### Software Compliance Check
```bash
python LPM.py --sections "Installed Programs" \
  --csv-out software_list.csv
```

### Secure Server Health Upload
```bash
python LPM.py --run-collector \
  --upload https://monitoring-api.company.com/health \
  --prompt-creds \
  --wait 30
```

### Full System Report (All Formats)
```bash
python LPM.py --run-collector \
  --json-out full_report.json \
  --csv-out full_report.csv \
  --xml-out full_report.xml
```

---

## Documentation

- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Common commands and examples
- **[Enhancements Guide](docs/ENHANCEMENTS.md)** - Detailed feature documentation
- **[Changelog](docs/CHANGELOG.md)** - Complete change history
- **[Setup Guide](docs/SETUP_README.txt)** - Installation help
- **[Quick Start](docs/QUICK_START.txt)** - Getting started guide

---

## Security

### Credential Handling
**DO NOT use:**
```bash
python LPM.py --upload URL --upload-bearer my_secret_token
# Token visible in: process list, command history, logs
```

**DO use:**
```bash
python LPM.py --upload URL --prompt-creds
# Credentials hidden, only in memory, never exposed
```

### Data Protection
- XML exports are sanitized (null-byte protection)
- Program names cleaned of special characters
- No sensitive data logged to disk
- Selective export for privacy control

---

## Building from Source

### Requirements
- Windows 10+
- Python 3.7+
- WiX Toolset 3.14+ (for MSI building)

### Build MSI Installer
```powershell
cd installer
powershell -ExecutionPolicy Bypass -File Build-MSI.ps1
```

Output: `LPM installer.msi` (45 KB)

See [installer/README.md](installer/README.md) for detailed build instructions.

---

## Output Examples

### Console Output
```
═══ Summary ═══
  Disk:
    Total: 2822.25 GB
    Used:  2365.81 GB (83.8%)
    Free:  456.44 GB
  Memory:
    Total: 15.82 GB
    Used:  7.67 GB (48.5%)
    Free:  8.15 GB
  Network:
    Ping Avg: 16.4 ms
```

### JSON Structure
```json
{
  "sections": {
    "OS & System": [...],
    "CPU(s)": [...],
    "GPU(s)": [...]
  },
  "summary": {
    "disk_total_bytes": 3022863138816,
    "disk_used_bytes": 2540236988416,
    "memory_total_bytes": 17006456832,
    "ping_avg_ms": 16.4
  }
}
```

### CSV Format
```
section,entry
OS & System,Caption: Microsoft Windows 11 Home
OS & System,Version: 10.0.26200
CPU(s),Name: 13th Gen Intel(R) Core(TM) i5-13600KF
CPU(s),Cores: 14, LogicalProcessors: 20
```

---

## Latest Enhancements (v1.0+)

- **Secure Credential Prompts** - Interactive input with hidden credentials
- **Section Filtering** - Export only needed sections
- **XML Sanitization** - Fixed null-byte errors, clean exports
- **Smart Data Limiting** - Large datasets summarized in terminal
- **Enhanced Formatting** - Percentages, better organization, clearer output

---

## Troubleshooting

### Python Not Found
Ensure Python 3.7+ is installed and in your PATH:
```bash
python --version
```

### Module Import Errors
Install missing modules:
```bash
pip install psutil py-cpuinfo
```

### WiX Not Found (Building)
Download WiX Toolset from:
https://github.com/wixtoolset/wix3/releases

### XML Parse Errors
All modern exports are sanitized. If you encounter errors:
```bash
python verify_exports.py
```

---

## Support

- Check [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) for common issues
- See [docs/ENHANCEMENTS.md](docs/ENHANCEMENTS.md) for feature details
- Review [CHANGELOG.md](docs/CHANGELOG.md) for recent changes

---

## License

MIT License - See LICENSE file for details

---

## Getting Started

1. **Download** the MSI installer from [Releases](https://github.com/YourUsername/LPM/releases)
2. **Run** the installer
3. **Open** Command Prompt or PowerShell
4. **Try:** `python LPM.py --run-collector`
5. **Explore** the output and examples above

---

## Version History

| Version | Release Date | Highlights |
|---------|--------------|-----------|
| 1.0+ | Feb 2026 | Secure prompts, section filtering, XML fix, enhanced formatting |
| 0.9 | Previous | Initial release with basic collection and exports |

---

**Made with for Windows system administrators and auditors**

*Ready to collect. Secure to share. Easy to analyze.*



