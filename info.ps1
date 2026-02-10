$out = "info.txt"
if (Test-Path $out) { Remove-Item $out -Force }
if (Test-Path "done.txt") { Remove-Item "done.txt" -Force }

function Format-Size {
    param([long]$bytes)
    if ($bytes -ge 1TB) { "{0:N2} TB" -f ($bytes / 1TB) }
    elseif ($bytes -ge 1GB) { "{0:N2} GB" -f ($bytes / 1GB) }
    elseif ($bytes -ge 1MB) { "{0:N2} MB" -f ($bytes / 1MB) }
    elseif ($bytes -ge 1KB) { "{0:N2} KB" -f ($bytes / 1KB) }
    else { "$bytes B" }
}

Add-Content -Path $out -Value "Timestamp: $(Get-Date -Format o)"
Add-Content -Path $out -Value "User: $env:USERNAME"
Add-Content -Path $out -Value "CurrentDirectory: $(Get-Location)"

# OS and computer
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$bios = Get-CimInstance Win32_BIOS
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== OS & System ==="
Add-Content -Path $out -Value ("Caption: {0}" -f $os.Caption)
Add-Content -Path $out -Value ("Version: {0}" -f $os.Version)
Add-Content -Path $out -Value ("BuildNumber: {0}" -f $os.BuildNumber)
Add-Content -Path $out -Value ("OSArchitecture: {0}" -f $os.OSArchitecture)

function Safe-DmtfToDate {
    param($dmtf)
    if (-not $dmtf -or [string]::IsNullOrWhiteSpace($dmtf)) { return $null }
    try { return [Management.ManagementDateTimeConverter]::ToDateTime($dmtf) }
    catch { return $null }
}

$installDate = Safe-DmtfToDate $os.InstallDate
if ($installDate) { Add-Content -Path $out -Value ("InstallDate: {0}" -f $installDate) } else { Add-Content -Path $out -Value "InstallDate: N/A" }

$lastBootTime = Safe-DmtfToDate $os.LastBootUpTime
if ($lastBootTime) { Add-Content -Path $out -Value ("LastBootUpTime: {0}" -f $lastBootTime) } else { Add-Content -Path $out -Value "LastBootUpTime: N/A" }
Add-Content -Path $out -Value ("Manufacturer: {0}" -f $cs.Manufacturer)
Add-Content -Path $out -Value ("Model: {0}" -f $cs.Model)
Add-Content -Path $out -Value ("SerialNumber (BIOS): {0}" -f $bios.SerialNumber)
Add-Content -Path $out -Value ("TotalPhysicalMemory: {0}" -f (Format-Size $cs.TotalPhysicalMemory))

# CPU
$procs = Get-CimInstance Win32_Processor
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== CPU(s) ==="
foreach ($p in $procs) {
    Add-Content -Path $out -Value ("Name: {0}" -f $p.Name)
    Add-Content -Path $out -Value ("Manufacturer: {0}" -f $p.Manufacturer)
    Add-Content -Path $out -Value ("Cores: {0}, LogicalProcessors: {1}" -f $p.NumberOfCores, $p.NumberOfLogicalProcessors)
    Add-Content -Path $out -Value ("MaxClockSpeedMHz: {0}" -f $p.MaxClockSpeed)
    Add-Content -Path $out -Value ("SocketDesignation: {0}" -f $p.SocketDesignation)
    Add-Content -Path $out -Value ("L2CacheSizeKB: {0}, L3CacheSizeKB: {1}" -f $p.L2CacheSize, $p.L3CacheSize)
}

# GPU
$gpus = Get-CimInstance Win32_VideoController
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== GPU(s) ==="
foreach ($g in $gpus) {
    Add-Content -Path $out -Value ("Name: {0}" -f $g.Name)
    if ($g.AdapterRAM) { Add-Content -Path $out -Value ("AdapterRAM: {0}" -f (Format-Size $g.AdapterRAM)) }
    Add-Content -Path $out -Value ("DriverVersion: {0}" -f $g.DriverVersion)
}

# Disks (Logical)
$disks = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3"
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== Disks (Logical) ==="
foreach ($d in $disks) {
    Add-Content -Path $out -Value ("DeviceID: {0}  FileSystem: {1}" -f $d.DeviceID, $d.FileSystem)
    Add-Content -Path $out -Value ("  Size: {0}  Free: {1}" -f (Format-Size $d.Size), (Format-Size $d.FreeSpace))
}

# Physical disks (optional)
$pd = Get-CimInstance -Namespace root\Microsoft\Windows\Storage MSFT_PhysicalDisk -ErrorAction SilentlyContinue
if ($pd) {
    Add-Content -Path $out -Value ""
    Add-Content -Path $out -Value "=== Physical Disks ==="
    foreach ($p in $pd) {
        Add-Content -Path $out -Value ("FriendlyName: {0}  Size: {1}  MediaType: {2}" -f $p.FriendlyName, (Format-Size $p.Size), $p.MediaType)
    }
}

# Network
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== Network ==="
try {
    $nics = Get-NetIPConfiguration | Where-Object { $_.IPv4Address -or $_.IPv6Address }
    foreach ($n in $nics) {
        Add-Content -Path $out -Value ("Interface: {0}" -f $n.InterfaceAlias)
        foreach ($ip in $n.IPv4Address) { Add-Content -Path $out -Value ("  IPv4: {0}" -f $ip.IPAddress) }
        foreach ($ip in $n.IPv6Address) { Add-Content -Path $out -Value ("  IPv6: {0}" -f $ip.IPAddress) }
        if ($n.DNSServer) {
            $dns = ($n.DNSServer | ForEach-Object { $_.ServerAddresses }) -join ", "
            Add-Content -Path $out -Value ("  DNS: {0}" -f $dns)
        }
        if ($n.IPv4DefaultGateway) { Add-Content -Path $out -Value ("  Gateway: {0}" -f $n.IPv4DefaultGateway.NextHop) }
    }
} catch {
    Add-Content -Path $out -Value "  (Network details not available: $_)"
}

# Net adapters speeds
$adapters = Get-NetAdapter -ErrorAction SilentlyContinue
if ($adapters) {
    Add-Content -Path $out -Value ""
    Add-Content -Path $out -Value "=== Network Adapters ==="
    foreach ($a in $adapters) {
        Add-Content -Path $out -Value ("Name: {0}  Status: {1}  LinkSpeed: {2}" -f $a.Name, $a.Status, $a.LinkSpeed)
    }
}

# Uptime
$lastBoot = $lastBootTime
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== System Uptime ==="
if ($lastBoot) {
    $uptime = (Get-Date) - $lastBoot
    Add-Content -Path $out -Value ("LastBootUpTime: {0}" -f $lastBoot)
    Add-Content -Path $out -Value ("Uptime: {0}" -f $uptime)
} else {
    Add-Content -Path $out -Value "LastBootUpTime: N/A"
    Add-Content -Path $out -Value "Uptime: N/A"
}

# Processes and load
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== Processes ==="
Add-Content -Path $out -Value ("ProcessCount: {0}" -f (Get-Process | Measure-Object).Count)

# Battery (if any)
$batt = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
if ($batt) {
    Add-Content -Path $out -Value "\n=== Battery ==="
    foreach ($b in $batt) { Add-Content -Path $out -Value ("Status: {0}  EstimatedChargeRemaining: {1}" -f $b.BatteryStatus, $b.EstimatedChargeRemaining) }
}

# Hotfixes
$hotfixes = Get-HotFix -ErrorAction SilentlyContinue
if ($hotfixes) {
    Add-Content -Path $out -Value ""
    Add-Content -Path $out -Value "=== Installed Hotfixes (recent) ==="
    $hotfixes | Select-Object -First 10 | ForEach-Object { Add-Content -Path $out -Value ("{0}  {1}  {2}" -f $_.HotFixID, $_.InstalledOn, $_.Description) }
}

    # Installed Programs (from registry and package providers) - limit output
    Add-Content -Path $out -Value ""
    Add-Content -Path $out -Value "=== Installed Programs ==="
    try {
        $seen = @{}
        $count = 0
        $limit = 200
        $regPaths = @("HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall", "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall")
        foreach ($rp in $regPaths) {
            if (Test-Path $rp) {
                Get-ChildItem $rp | ForEach-Object {
                    if ($count -ge $limit) { return }
                    $p = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
                    if ($p -and $p.DisplayName) {
                        $key = "$($p.DisplayName)|$($p.Publisher)"
                        if (-not $seen.ContainsKey($key)) {
                            $seen[$key] = $true
                            $cleanName = $p.DisplayName -replace '[^\x20-\x7E]', ''
                            $cleanVersion = ($p.DisplayVersion -or '') -replace '[^\x20-\x7E]', ''
                            $cleanPub = ($p.Publisher -or '') -replace '[^\x20-\x7E]', ''
                            Add-Content -Path $out -Value ("{0} | {1} | {2}" -f $cleanName, $cleanVersion, $cleanPub)
                            $count++
                        }
                    }
                }
            }
        }
        if ($count -lt $limit) {
            try {
                Get-Package -ErrorAction SilentlyContinue | Select-Object -First ($limit - $count) | ForEach-Object {
                    $cleanName = $_.Name -replace '[^\x20-\x7E]', ''
                    $cleanVersion = ($_.Version -or '') -replace '[^\x20-\x7E]', ''
                    $cleanProvider = ($_.ProviderName -or '') -replace '[^\x20-\x7E]', ''
                    Add-Content -Path $out -Value ("{0} | {1} | {2}" -f $cleanName, $cleanVersion, $cleanProvider)
                    $count++
                }
            } catch {}
        }
        Add-Content -Path $out -Value "[Collected $count programs]"
    } catch {
        Add-Content -Path $out -Value "Installed programs enumeration failed: $_"
    }

    # Services (name, displayname, state, startmode)
    Add-Content -Path $out -Value ""
    Add-Content -Path $out -Value "=== Services ==="
    try {
        Get-CimInstance Win32_Service | Sort-Object -Property DisplayName | ForEach-Object {
            Add-Content -Path $out -Value ("{0} | {1} | {2} | {3}" -f $_.Name, $_.DisplayName, $_.State, $_.StartMode)
        }
    } catch {
        Add-Content -Path $out -Value "Services enumeration failed: $_"
    }

# Ping test
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== Ping Test ==="
$ping = Test-Connection -ComputerName 8.8.8.8 -Count 4 -ErrorAction SilentlyContinue
if ($ping) {
    $ping | ForEach-Object { Add-Content -Path $out -Value ("Reply from {0}: time={1}ms" -f $_.Address, $_.ResponseTime) }
    Add-Content -Path $out -Value ("Average: {0}ms" -f ($ping | Measure-Object -Property ResponseTime -Average).Average)
} else { Add-Content -Path $out -Value "Ping failed or blocked." }

# Finish
Add-Content -Path $out -Value ""
Add-Content -Path $out -Value "=== End of Report ==="

# Signal completion
"n" | Out-File -FilePath "done.txt" -Encoding ascii

Write-Output "Information collected to $out"
