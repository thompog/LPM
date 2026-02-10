import os
import sys
import platform
import subprocess
import time
import getpass

# Enable UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Color codes for terminal output (ASCII-safe)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_python_version():
    """Check if Python version meets minimum requirements"""
    min_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print(f"\n{Colors.FAIL}ERROR: Python version requirement not met!{Colors.ENDC}")
        print(f"   Required: Python 3.7 or later")
        print(f"   Current: Python {current_version[0]}.{current_version[1]}")
        print(f"\n   Please upgrade Python from: https://www.python.org/downloads/")
        return False
    return True

def check_module(module_name, pip_name=None):
    """Check if a required module is installed"""
    if pip_name is None:
        pip_name = module_name
    
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def install_missing_modules():
    """Attempt to install missing modules"""
    required_modules = {
        'psutil': 'psutil',
        'cpuinfo': 'py-cpuinfo'
    }
    
    missing = []
    for module, pip_name in required_modules.items():
        if not check_module(module, pip_name):
            missing.append((module, pip_name))
    
    if not missing:
        return True

    print(f"\n{Colors.WARNING}WARNING: Missing required Python modules:{Colors.ENDC}")
    for module, pip_name in missing:
        print(f"   - {pip_name}")

    print(f"\n{Colors.OKBLUE}Attempting to install missing modules...{Colors.ENDC}")

    def try_install(pip_args, timeout=120):
        try:
            result = subprocess.run(pip_args, capture_output=True, timeout=timeout)
            return result.returncode == 0, result
        except Exception as e:
            return False, e

    try:
        for module, pip_name in missing:
            print(f"   Installing {pip_name}...", end=" ", flush=True)
            pip_cmd = [sys.executable, "-m", "pip", "install", pip_name, "--disable-pip-version-check"]
            ok, res = try_install(pip_cmd)
            if not ok:
                # Retry with --user
                pip_cmd_user = pip_cmd + ["--user"]
                ok2, res2 = try_install(pip_cmd_user)
                if ok2:
                    print(f"{Colors.OKGREEN}OK (user){Colors.ENDC}")
                    continue
                # Try upgrading pip then retry
                up_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--disable-pip-version-check"]
                _ok_up, _res_up = try_install(up_cmd)
                ok3, res3 = try_install(pip_cmd)
                if ok3:
                    print(f"{Colors.OKGREEN}OK{Colors.ENDC}")
                    continue
                # Final fallback: show stderr or exception
                print(f"{Colors.FAIL}FAILED{Colors.ENDC}")
                if hasattr(res, 'stderr'):
                    error_msg = res.stderr.decode('utf-8', errors='ignore')
                    if error_msg:
                        print(f"   Error: {error_msg[:300]}")
                else:
                    print(f"   Error: {res}")
                return False
            else:
                print(f"{Colors.OKGREEN}OK{Colors.ENDC}")
        
        return True
    except Exception as e:
        print(f"{Colors.FAIL}ERROR: {e}{Colors.ENDC}")
        return False

def validate_dependencies():
    """Validate all dependencies before running"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== LPM System Information Tool ==={Colors.ENDC}\n")
    
    # Check Python version
    print(f"{Colors.OKBLUE}Checking Python version...{Colors.ENDC}", end=" ", flush=True)
    if not check_python_version():
        return False
    print(f"{Colors.OKGREEN}OK{Colors.ENDC}")
    print(f"   Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check required modules
    required_modules = {
        'psutil': 'psutil',
        'cpuinfo': 'py-cpuinfo',
        'shutil': 'shutil (built-in)'
    }
    
    print(f"\n{Colors.OKBLUE}Checking required modules...{Colors.ENDC}")
    all_present = True
    for module, display_name in required_modules.items():
        has_module = check_module(module)
        status = "[OK]" if has_module else "[MISSING]"
        color = Colors.OKGREEN if has_module else Colors.FAIL
        print(f"   {color}{status}{Colors.ENDC} {display_name}")
        if not has_module and module != 'shutil':
            all_present = False
    
    # If modules missing, try to install
    if not all_present:
        if not install_missing_modules():
            print(f"\n{Colors.FAIL}ERROR: Failed to install required modules!{Colors.ENDC}")
            print(f"\nTo manually install, run:")
            print(f"   python -m pip install psutil py-cpuinfo")
            print(f"\nOr visit: https://www.python.org/downloads/")
            return False
        print(f"\n{Colors.OKGREEN}OK: All modules installed successfully!{Colors.ENDC}")
    else:
        print(f"\n{Colors.OKGREEN}OK: All dependencies present!{Colors.ENDC}")
    
    return True

# Import modules with error handling
try:
    import psutil
    import cpuinfo
    import shutil
    import time
    import json
    import argparse
    import csv
    import re
    import xml.etree.ElementTree as ET
    import urllib.request
    import urllib.error
except ImportError as e:
    print(f"{Colors.FAIL}ERROR: Unable to import required modules!{Colors.ENDC}")
    print(f"   {e}")
    sys.exit(1)

def get_system_info():
    try:
        print(f"\n{Colors.BOLD}=== System Information ==={Colors.ENDC}")
        print(f"System: {platform.system()}")
        print(f"Node Name: {platform.node()}")
        print(f"Release: {platform.release()}")
        print(f"Version: {platform.version()}")
        print(f"Machine: {platform.machine()}")
        print(f"Processor: {platform.processor() or cpuinfo.get_cpu_info()['brand_raw']}")
        cpu = cpuinfo.get_cpu_info()
        print(f"\n{Colors.BOLD}=== CPU Information ==={Colors.ENDC}")
        print(f"CPU Brand: {cpu.get('brand_raw', 'Unknown')}")
        print(f"Architecture: {cpu.get('arch', 'Unknown')}")
        print(f"Cores (Physical): {psutil.cpu_count(logical=False)}")
        print(f"Cores (Logical): {psutil.cpu_count(logical=True)}")
        print(f"Max Frequency: {psutil.cpu_freq().max:.2f} MHz")
        mem = psutil.virtual_memory()
        print(f"\n{Colors.BOLD}=== Memory Information ==={Colors.ENDC}")
        print(f"Total: {mem.total / (1024**3):.2f} GB")
        print(f"Available: {mem.available / (1024**3):.2f} GB")
        total, used, free = shutil.disk_usage("/")
        print(f"\n{Colors.BOLD}=== Disk Information ==={Colors.ENDC}")
        print(f"Total: {total / (1024**3):.2f} GB")
        print(f"Used: {used / (1024**3):.2f} GB")
        print(f"Free: {free / (1024**3):.2f} GB")
        
    except Exception as e:
        print(f"{Colors.FAIL}Error retrieving system info: {e}{Colors.ENDC}")

if __name__ == "__main__":
    # Validate all dependencies first
    if not validate_dependencies():
        print(f"\n{Colors.FAIL}Cannot proceed without dependencies.{Colors.ENDC}\n")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-collector', dest='run_collector', action='store_true', help='Run the PowerShell collector before parsing')
    parser.add_argument('--wait', dest='wait_seconds', type=int, default=30, help='Seconds to wait for collector to finish')
    parser.add_argument('--json-out', dest='json_out', nargs='?', const='info.json', help='Write parsed info + summary to JSON')
    parser.add_argument('--csv-out', dest='csv_out', nargs='?', const='info.csv', help='Write parsed info to CSV')
    parser.add_argument('--xml-out', dest='xml_out', nargs='?', const='info.xml', help='Write parsed info to XML')
    parser.add_argument('--upload', dest='upload_url', help='POST JSON report to this URL')
    parser.add_argument('--upload-user', dest='upload_user', help='Username for basic auth upload')
    parser.add_argument('--upload-pass', dest='upload_pass', help='Password for basic auth upload')
    parser.add_argument('--upload-bearer', dest='upload_bearer', help='Bearer token for upload')
    parser.add_argument('--prompt-creds', dest='prompt_creds', action='store_true', help='Prompt for upload credentials interactively')
    parser.add_argument('--sections', dest='sections', help='Comma-separated list of sections to include (e.g., "OS & System,CPU,Network")')
    args = parser.parse_args()

    def prompt_upload_creds():
        """Prompt user for upload authentication credentials."""
        print(f"\n{Colors.OKBLUE}Upload Authentication{Colors.ENDC}")
        auth_type = input(f"{Colors.BOLD}Auth type (bearer/basic) [bearer]: {Colors.ENDC}").strip().lower() or 'bearer'
        if auth_type == 'bearer':
            token = getpass.getpass(f"{Colors.BOLD}Bearer token: {Colors.ENDC}")
            return ('bearer', token)
        else:
            user = input(f"{Colors.BOLD}Username: {Colors.ENDC}").strip()
            pwd = getpass.getpass(f"{Colors.BOLD}Password: {Colors.ENDC}")
            return ('basic', (user, pwd))

    def should_include_section(section_name, filter_list):
        """Check if section should be included based on filter."""
        if not filter_list:
            return True
        return any(f.strip().lower() in section_name.lower() for f in filter_list)

    def run_collector_cmd():
        """Invoke info.ps1 via PowerShell (or fallback to info.bat)."""
        ps1 = os.path.join(os.getcwd(), 'info.ps1')
        bat = os.path.join(os.getcwd(), 'info.bat')
        ps = shutil.which('powershell') or shutil.which('pwsh')
        if ps and os.path.exists(ps1):
            try:
                subprocess.run([ps, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1], check=True, timeout=300)
                return True
            except Exception:
                pass
        if os.path.exists(bat):
            try:
                subprocess.run([bat], check=True, shell=True, timeout=300)
                return True
            except Exception:
                pass
        return False

    # Handle credential prompts
    if args.prompt_creds and args.upload_url:
        auth_type, creds = prompt_upload_creds()
        if auth_type == 'bearer':
            args.upload_bearer = creds
        else:
            args.upload_user, args.upload_pass = creds

    # Parse section filter
    section_filter = [s.strip() for s in args.sections.split(',')] if args.sections else None

    # Optionally run collector
    if args.run_collector:
        print(f"{Colors.OKBLUE}Running collector...{Colors.ENDC}")
        ok = run_collector_cmd()
        if not ok:
            print(f"{Colors.WARNING}Collector run failed; will continue to parse any existing info.txt{Colors.ENDC}")

    # Check for info.txt from batch file. Wait up to `wait_seconds` seconds.
    wait_seconds = args.wait_seconds
    start_time = time.time()
    info_raw = None
    while time.time() - start_time < wait_seconds:
        if os.path.exists("done.txt"):
            try:
                with open("info.txt", "r", encoding='utf-8', errors='ignore') as f:
                    info_raw = f.read()
            except FileNotFoundError:
                info_raw = None
            break
        time.sleep(0.5)
    else:
        print(f"\n{Colors.WARNING}Batch script not completed within {wait_seconds} seconds; continuing.{Colors.ENDC}")

    # Parse the info file into structured sections for nicer display and optional JSON export
    def parse_info(text):
        sections = {}
        if not text:
            return sections
        current = 'General'
        sections[current] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            # Remove leftover literal backslash-n markers if present
            if line.startswith('\\n'):
                line = line[2:].strip()
            if line.startswith('===') and line.endswith('==='):
                title = line.strip('= ').strip()
                current = title
                sections[current] = []
                continue
            if line == '':
                continue
            sections.setdefault(current, []).append(line)
        return sections
    if info_raw:
        sections = parse_info(info_raw)
        print(f"\n{Colors.BOLD}=== Batch Script Information ==={Colors.ENDC}")
        # Print sections in order, filter if needed
        for sec, lines in sections.items():
            if not should_include_section(sec, section_filter):
                continue
            print(f"\n{Colors.BOLD}{sec}:{Colors.ENDC}")
            # Special handling for large sections: limit installed programs
            if 'Installed Programs' in sec and len(lines) > 50:
                print(f"  {Colors.WARNING}[Showing first 50 of {len(lines)} installed programs]{Colors.ENDC}")
                for ln in lines[:50]:
                    print(f"  {ln}")
                print(f"  {Colors.OKCYAN}... ({len(lines) - 50} more) - See exports for full list{Colors.ENDC}")
            elif 'Services' in sec and len(lines) > 100:
                print(f"  {Colors.WARNING}[Showing first 100 of {len(lines)} services]{Colors.ENDC}")
                for ln in lines[:100]:
                    print(f"  {ln}")
                print(f"  {Colors.OKCYAN}... ({len(lines) - 100} more) - See exports for full list{Colors.ENDC}")
            else:
                for ln in lines:
                    print(f"  {ln}")

        # Helper: parse sizes like "1.77 TB" into bytes
        def parse_size_to_bytes(s):
            if not s:
                return 0
            m = re.search(r"([0-9,.]+)\s*(KB|MB|GB|TB|B)", s, re.I)
            if not m:
                return 0
            val = float(m.group(1).replace(',',''))
            unit = m.group(2).upper()
            mul = {'B':1, 'KB':1024, 'MB':1024**2, 'GB':1024**3, 'TB':1024**4}
            return int(val * mul.get(unit,1))

        # Numeric summaries
        summary = {}
        # Disk totals from parsed "Disks (Logical)"
        disk_lines = sections.get('Disks (Logical)', [])
        total_bytes = 0
        free_bytes = 0
        i = 0
        while i < len(disk_lines):
            ln = disk_lines[i]
            # Some entries span two lines (DeviceID line then Size line)
            if 'Size:' in ln and 'Free:' in ln:
                msize = re.search(r"Size:\s*([0-9.,]+\s*(?:KB|MB|GB|TB|B))", ln, re.I)
                mfree = re.search(r"Free:\s*([0-9.,]+\s*(?:KB|MB|GB|TB|B))", ln, re.I)
                if msize:
                    total_bytes += parse_size_to_bytes(msize.group(1))
                if mfree:
                    free_bytes += parse_size_to_bytes(mfree.group(1))
            else:
                # next line might contain size/free
                if i+1 < len(disk_lines):
                    ln2 = disk_lines[i+1]
                    if 'Size:' in ln2 and 'Free:' in ln2:
                        msize = re.search(r"Size:\s*([0-9.,]+\s*(?:KB|MB|GB|TB|B))", ln2, re.I)
                        mfree = re.search(r"Free:\s*([0-9.,]+\s*(?:KB|MB|GB|TB|B))", ln2, re.I)
                        if msize:
                            total_bytes += parse_size_to_bytes(msize.group(1))
                        if mfree:
                            free_bytes += parse_size_to_bytes(mfree.group(1))
                        i += 1
            i += 1
        summary['disk_total_bytes'] = total_bytes
        summary['disk_free_bytes'] = free_bytes
        summary['disk_used_bytes'] = max(0, total_bytes - free_bytes)

        # Ping average from "Ping Test" section
        ping_vals = []
        for ln in sections.get('Ping Test', []):
            m = re.search(r"time=([0-9]+)ms", ln)
            if m:
                ping_vals.append(int(m.group(1)))
            m2 = re.search(r"Average:\s*([0-9.,]+)ms", ln, re.I)
            if m2:
                try:
                    ping_vals.append(int(float(m2.group(1))))
                except Exception:
                    pass
        summary['ping_avg_ms'] = (sum(ping_vals) / len(ping_vals)) if ping_vals else None

        # Memory via psutil for accurate values
        try:
            vm = psutil.virtual_memory()
            summary['mem_total_bytes'] = vm.total
            summary['mem_available_bytes'] = vm.available
            summary['mem_used_bytes'] = vm.total - vm.available
        except Exception:
            summary['mem_total_bytes'] = None

        # Print numeric summary with improved formatting
        print(f"\n{Colors.BOLD}═══ Summary ═══{Colors.ENDC}")
        if summary['disk_total_bytes']:
            used_pct = (summary['disk_used_bytes'] / summary['disk_total_bytes']) * 100 if summary['disk_total_bytes'] > 0 else 0
            print(f"  {Colors.BOLD}Disk:{Colors.ENDC}")
            print(f"    Total: {summary['disk_total_bytes'] / (1024**3):.2f} GB")
            print(f"    Used:  {summary['disk_used_bytes'] / (1024**3):.2f} GB ({used_pct:.1f}%)")
            print(f"    Free:  {summary['disk_free_bytes'] / (1024**3):.2f} GB")
        if summary.get('mem_total_bytes'):
            mem_pct = (summary['mem_used_bytes'] / summary['mem_total_bytes']) * 100 if summary['mem_total_bytes'] > 0 else 0
            print(f"  {Colors.BOLD}Memory:{Colors.ENDC}")
            print(f"    Total: {summary['mem_total_bytes'] / (1024**3):.2f} GB")
            print(f"    Used:  {summary['mem_used_bytes'] / (1024**3):.2f} GB ({mem_pct:.1f}%)")
            print(f"    Free:  {summary['mem_available_bytes'] / (1024**3):.2f} GB")
        if summary.get('ping_avg_ms') is not None:
            print(f"  {Colors.BOLD}Network:{Colors.ENDC}")
            print(f"    Ping Avg: {summary['ping_avg_ms']:.1f} ms")

        # JSON export (with section filtering if specified)
        if args.json_out:
            try:
                filtered_secs = {k: v for k, v in sections.items() if should_include_section(k, section_filter)}
                with open(args.json_out, 'w', encoding='utf-8') as jf:
                    json.dump({'sections': filtered_secs, 'summary': summary}, jf, indent=2, ensure_ascii=False)
                print(f"{Colors.OKGREEN}Wrote JSON export to {args.json_out}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}Failed to write JSON: {e}{Colors.ENDC}")

        # CSV export (section, entry) with filtering
        if args.csv_out:
            try:
                with open(args.csv_out, 'w', newline='', encoding='utf-8') as cf:
                    writer = csv.writer(cf)
                    writer.writerow(['section', 'entry'])
                    for sec, lines in sections.items():
                        if not should_include_section(sec, section_filter):
                            continue
                        for ln in lines:
                            writer.writerow([sec, ln])
                print(f"{Colors.OKGREEN}Wrote CSV export to {args.csv_out}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}Failed to write CSV: {e}{Colors.ENDC}")

        # XML export (sanitize content to remove null bytes)
        if args.xml_out:
            try:
                def sanitize_xml_text(text):
                    """Remove null bytes and other invalid XML characters."""
                    if not text:
                        return ''
                    # Remove null bytes and other control characters (except tab, newline, carriage return)
                    return ''.join(c for c in text if c >= ' ' or c in '\t\n\r')
                
                root = ET.Element('report')
                secs = ET.SubElement(root, 'sections')
                for sec, lines in sections.items():
                    if not should_include_section(sec, section_filter):
                        continue
                    s = ET.SubElement(secs, 'section', name=sanitize_xml_text(sec))
                    for ln in lines:
                        e = ET.SubElement(s, 'entry')
                        e.text = sanitize_xml_text(ln)
                summ = ET.SubElement(root, 'summary')
                for k,v in summary.items():
                    kv = ET.SubElement(summ, 'metric', name=sanitize_xml_text(str(k)))
                    kv.text = sanitize_xml_text(str(v))
                tree = ET.ElementTree(root)
                tree.write(args.xml_out, encoding='utf-8', xml_declaration=True)
                print(f"{Colors.OKGREEN}Wrote XML export to {args.xml_out}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}Failed to write XML: {e}{Colors.ENDC}")

        # Upload
        if args.upload_url:
            try:
                filtered_secs = {k: v for k, v in sections.items() if should_include_section(k, section_filter)}
                payload = json.dumps({'sections': filtered_secs, 'summary': summary}).encode('utf-8')
                headers = {'Content-Type':'application/json'}
                # Add auth header if provided
                if getattr(args, 'upload_bearer', None):
                    headers['Authorization'] = f"Bearer {args.upload_bearer}"
                elif getattr(args, 'upload_user', None) and getattr(args, 'upload_pass', None):
                    import base64
                    creds = f"{args.upload_user}:{args.upload_pass}".encode('utf-8')
                    headers['Authorization'] = 'Basic ' + base64.b64encode(creds).decode('ascii')
                req = urllib.request.Request(args.upload_url, data=payload, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    code = resp.getcode()
                print(f"{Colors.OKGREEN}Upload succeeded, HTTP {code}{Colors.ENDC}")
            except urllib.error.HTTPError as he:
                print(f"{Colors.FAIL}Upload failed: HTTP {he.code}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}Upload error: {e}{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}No batch info available.{Colors.ENDC}")
    
    # Display system information
    get_system_info()
    print(f"\n{Colors.OKGREEN}✓ Information retrieval complete!{Colors.ENDC}\n")
    input("Press Enter to exit...")