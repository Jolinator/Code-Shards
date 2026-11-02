param(
    [string]$OutputPath
)

# Collect Windows host details that are useful when tuning low-level code.
# Usage: .\collect_windows.ps1 [output.env]
$ErrorActionPreference = 'Stop'

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $scriptDirectory '.env'
}
$outputDirectory = Split-Path -Parent $OutputPath
if ([string]::IsNullOrWhiteSpace($outputDirectory)) {
    $outputDirectory = (Get-Location).Path
}
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}

function Get-CimInstances {
    param(
        [Parameter(Mandatory = $true)][string]$ClassName,
        [string]$Namespace = 'root/cimv2'
    )
    try {
        return @(Get-CimInstance -Namespace $Namespace -ClassName $ClassName -ErrorAction Stop)
    }
    catch {
        return @()
    }
}

function Get-WindowsCacheLineSizes {
    try {
        if (-not ('CacheTopologySetsNative' -as [type])) {
            Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class CacheTopologySetsNative {
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetLogicalProcessorInformationEx(
        int relationshipType,
        IntPtr buffer,
        ref uint returnedLength);

    public static string[] GetCacheRecords() {
        uint length = 0;
        GetLogicalProcessorInformationEx(2, IntPtr.Zero, ref length);
        if (length == 0) return new string[0];

        IntPtr buffer = Marshal.AllocHGlobal((int)length);
        try {
            if (!GetLogicalProcessorInformationEx(2, buffer, ref length))
                return new string[0];

            int totalLength = (int)length;
            int offset = 0;
            List<string> records = new List<string>();
            while (offset <= totalLength - 8) {
                int relationship = Marshal.ReadInt32(buffer, offset);
                int structureSize = Marshal.ReadInt32(buffer, offset + 4);
                if (structureSize < 8 || structureSize > totalLength - offset)
                    break;

                if (relationship == 2 && structureSize >= 20) {
                    int level = Marshal.ReadByte(buffer, offset + 8);
                    int associativity = Marshal.ReadByte(buffer, offset + 9);
                    int lineSize = (ushort)Marshal.ReadInt16(buffer, offset + 10);
                    uint cacheSize = unchecked((uint)Marshal.ReadInt32(buffer, offset + 12));
                    int type = Marshal.ReadInt32(buffer, offset + 16);
                    records.Add(level + "|" + type + "|" + cacheSize + "|" + lineSize + "|" + associativity);
                }
                offset += structureSize;
            }
            return records.ToArray();
        }
        finally {
            Marshal.FreeHGlobal(buffer);
        }
    }

    public static int[] GetLineSizes() {
        uint length = 0;
        GetLogicalProcessorInformationEx(2, IntPtr.Zero, ref length);
        if (length == 0) return new int[0];

        IntPtr buffer = Marshal.AllocHGlobal((int)length);
        try {
            if (!GetLogicalProcessorInformationEx(2, buffer, ref length))
                return new int[0];

            int totalLength = (int)length;
            int offset = 0;
            List<int> lineSizes = new List<int>();
            while (offset <= totalLength - 8) {
                int relationship = Marshal.ReadInt32(buffer, offset);
                int structureSize = Marshal.ReadInt32(buffer, offset + 4);
                if (structureSize < 8 || structureSize > totalLength - offset)
                    break;

                if (relationship == 2 && structureSize >= 12) {
                    int lineSize = (ushort)Marshal.ReadInt16(buffer, offset + 10);
                    if (lineSize > 0 && !lineSizes.Contains(lineSize))
                        lineSizes.Add(lineSize);
                }
                offset += structureSize;
            }
            lineSizes.Sort();
            return lineSizes.ToArray();
        }
        finally {
            Marshal.FreeHGlobal(buffer);
        }
    }
}
'@ -ErrorAction Stop | Out-Null
        }
        return @([CacheTopologySetsNative]::GetLineSizes())
    }
    catch {
        return @()
    }
}

function Get-WindowsCacheRecords {
    try {
        if (-not ('CacheTopologySetsNative' -as [type])) {
            [void](Get-WindowsCacheLineSizes)
        }
        return @([CacheTopologySetsNative]::GetCacheRecords())
    }
    catch {
        return @()
    }
}

function ConvertTo-EnvString {
    param([AllowNull()][object]$Value)
    if ($null -eq $Value) {
        return ''
    }
    if ($Value -is [System.Array]) {
        $Value = ($Value | ForEach-Object { [string]$_ }) -join ','
    }
    $text = [string]$Value
    $text = $text.Replace('\', '\\').Replace('"', '\"')
    $text = $text.Replace("`r", '\r').Replace("`n", '\n')
    return '"' + $text + '"'
}

function Get-DotNetInstructionFeatures {
    $featureTypes = @(
        'System.Runtime.Intrinsics.X86.Sse',
        'System.Runtime.Intrinsics.X86.Sse2',
        'System.Runtime.Intrinsics.X86.Sse3',
        'System.Runtime.Intrinsics.X86.Ssse3',
        'System.Runtime.Intrinsics.X86.Sse41',
        'System.Runtime.Intrinsics.X86.Sse42',
        'System.Runtime.Intrinsics.X86.Aes',
        'System.Runtime.Intrinsics.X86.Pclmulqdq',
        'System.Runtime.Intrinsics.X86.Popcnt',
        'System.Runtime.Intrinsics.X86.Lzcnt',
        'System.Runtime.Intrinsics.X86.Bmi1',
        'System.Runtime.Intrinsics.X86.Bmi2',
        'System.Runtime.Intrinsics.X86.Fma',
        'System.Runtime.Intrinsics.X86.Avx',
        'System.Runtime.Intrinsics.X86.Avx2',
        'System.Runtime.Intrinsics.X86.Avx512F',
        'System.Runtime.Intrinsics.X86.Avx512BW',
        'System.Runtime.Intrinsics.X86.Avx512CD',
        'System.Runtime.Intrinsics.X86.Avx512DQ',
        'System.Runtime.Intrinsics.X86.Avx512VL',
        'System.Runtime.Intrinsics.Arm.AdvSimd',
        'System.Runtime.Intrinsics.Arm.Aes',
        'System.Runtime.Intrinsics.Arm.Crc32',
        'System.Runtime.Intrinsics.Arm.Sha1',
        'System.Runtime.Intrinsics.Arm.Sha256'
    )
    try {
        [void][System.Reflection.Assembly]::Load('System.Runtime.Intrinsics')
    }
    catch {
        # Older Windows PowerShell/.NET Framework versions do not expose these APIs.
    }
    $assemblies = [AppDomain]::CurrentDomain.GetAssemblies()
    $supported = @()
    foreach ($typeName in $featureTypes) {
        $type = $null
        foreach ($assembly in $assemblies) {
            $type = $assembly.GetType($typeName, $false)
            if ($null -ne $type) { break }
        }
        if ($null -ne $type) {
            try {
                if ([bool]$type.GetProperty('IsSupported').GetValue($null, $null)) {
                    $supported += ($typeName -replace '^System\.Runtime\.Intrinsics\.', '')
                }
            }
            catch {
                # Leave out types without a readable IsSupported property.
            }
        }
    }
    if ($supported.Count -gt 0) {
        return ($supported -join ',')
    }
    return 'unavailable in this PowerShell/.NET runtime'
}

$os = Get-CimInstances 'Win32_OperatingSystem' | Select-Object -First 1
$computer = Get-CimInstances 'Win32_ComputerSystem' | Select-Object -First 1
$processors = @(Get-CimInstances 'Win32_Processor')
$caches = @(Get-CimInstances 'Win32_CacheMemory')
$gpus = @(Get-CimInstances 'Win32_VideoController')
$physicalDisks = @(Get-CimInstances 'MSFT_PhysicalDisk' 'root/Microsoft/Windows/Storage')
$fallbackDisks = @(Get-CimInstances 'Win32_DiskDrive')
$pageFiles = @(Get-CimInstances 'Win32_PageFileUsage')
$memoryCounters = Get-CimInstances 'Win32_PerfFormattedData_PerfOS_Memory' | Select-Object -First 1
$numaNodes = @(Get-CimInstances 'Win32_NumaNode')

$physicalCores = 0
$logicalCores = 0
$maxMhz = @()
$currentMhz = @()
$l2Sizes = @()
$l3Sizes = @()
$processorNames = @()
$vendors = @()
$families = @()
$steppings = @()
$cpuidFamilies = @()
$cpuidModels = @()
$cpuidSteppings = @()
$instructionSets = @()
$virtualizationDetails = @()
foreach ($processor in $processors) {
    $physicalCores += [int]$processor.NumberOfCores
    $logicalCores += [int]$processor.NumberOfLogicalProcessors
    if ($processor.MaxClockSpeed) { $maxMhz += [int]$processor.MaxClockSpeed }
    if ($processor.CurrentClockSpeed) { $currentMhz += [int]$processor.CurrentClockSpeed }
    if ($processor.L2CacheSize) { $l2Sizes += [int]$processor.L2CacheSize }
    if ($processor.L3CacheSize) { $l3Sizes += [int]$processor.L3CacheSize }
    if ($processor.Name) { $processorNames += [string]$processor.Name.Trim() }
    if ($processor.Manufacturer) { $vendors += [string]$processor.Manufacturer.Trim() }
    if ($processor.Family) { $families += [string]$processor.Family }
    if ($processor.Stepping) { $steppings += [string]$processor.Stepping }
    if ([string]$processor.ProcessorId -match '([0-9A-Fa-f]{8})$') {
        try {
            $signature = [Convert]::ToUInt32($Matches[1], 16)
            $baseFamily = [int](($signature -shr 8) -band 0xF)
            $extendedFamily = [int](($signature -shr 20) -band 0xFF)
            $baseModel = [int](($signature -shr 4) -band 0xF)
            $extendedModel = [int](($signature -shr 16) -band 0xF)
            $familyValue = $baseFamily
            if ($baseFamily -eq 0xF) { $familyValue += $extendedFamily }
            $modelValue = $baseModel
            if ($baseFamily -eq 0x6 -or $baseFamily -eq 0xF) { $modelValue = $baseModel -bor ($extendedModel -shl 4) }
            $cpuidFamilies += [string]$familyValue
            $cpuidModels += ('0x{0:X}' -f $modelValue)
            $cpuidSteppings += [string]($signature -band 0xF)
        }
        catch {
            # Keep WMI-reported values if the processor ID is not a CPUID signature.
        }
    }
    if ($processor.InstructionSet) { $instructionSets += @($processor.InstructionSet | ForEach-Object { [string]$_ }) }
    if ($null -ne $processor.VirtualizationFirmwareEnabled) { $virtualizationDetails += "firmware=$($processor.VirtualizationFirmwareEnabled)" }
    if ($null -ne $processor.SecondLevelAddressTranslationExtensions) { $virtualizationDetails += "SLAT=$($processor.SecondLevelAddressTranslationExtensions)" }
    if ($null -ne $processor.VMMonitorModeExtensions) { $virtualizationDetails += "VMM=$($processor.VMMonitorModeExtensions)" }
}

$cacheRows = @()
$cacheWays = [ordered]@{
    L1 = @()
    L2 = @()
    L3 = @()
}
$l1dSizes = @()
$l1iSizes = @()
$l1uSizes = @()
foreach ($cache in $caches | Sort-Object Level, CacheType, DeviceID) {
    $level = switch ([int]$cache.Level) {
        3 { 'L1' }
        4 { 'L2' }
        5 { 'L3' }
        6 { 'L4' }
        default { "Level$($cache.Level)" }
    }
    $kind = switch ([int]$cache.CacheType) {
        3 { 'instruction' }
        4 { 'data' }
        5 { 'unified' }
        default { "type$($cache.CacheType)" }
    }
    $associativity = switch ([int]$cache.Associativity) {
        1 { 'other' }
        2 { 'unknown' }
        3 { 'direct-mapped' }
        4 { '2-way' }
        5 { '4-way' }
        6 { 'fully-associative' }
        7 { '8-way' }
        8 { '16-way' }
        default { '' }
    }
    $size = if ($cache.InstalledSize) { [int]$cache.InstalledSize } elseif ($cache.MaxCacheSize) { [int]$cache.MaxCacheSize } else { 0 }
    $entry = "$level-$kind=$($size)KB"
    if ($cache.LineSize) { $entry += "/$($cache.LineSize)B-line" }
    if ($associativity) { $entry += "/$associativity" }
    $cacheRows += $entry
    if ($cacheWays.Contains($level)) {
        switch ($associativity) {
            'direct-mapped' { $cacheWays[$level] += 1 }
            '2-way' { $cacheWays[$level] += 2 }
            '4-way' { $cacheWays[$level] += 4 }
            '8-way' { $cacheWays[$level] += 8 }
            '16-way' { $cacheWays[$level] += 16 }
            'fully-associative' { $cacheWays[$level] += 'fully-associative' }
        }
    }
    if ($size -gt 0 -and [int]$cache.Level -eq 3) {
        if ([int]$cache.CacheType -eq 4) { $l1dSizes += $size }
        elseif ([int]$cache.CacheType -eq 3) { $l1iSizes += $size }
        elseif ([int]$cache.CacheType -eq 5) { $l1uSizes += $size }
    }
}
$cacheLineSizes = @($caches | Where-Object { $_.LineSize -gt 0 } | Select-Object -ExpandProperty LineSize -Unique | Sort-Object)
$cacheLineSizeSource = 'Win32_CacheMemory.LineSize'
if ($cacheLineSizes.Count -eq 0) {
    $cacheLineSizes = @(Get-WindowsCacheLineSizes | Select-Object -Unique | Sort-Object)
    $cacheLineSizeSource = if ($cacheLineSizes.Count -gt 0) { 'GetLogicalProcessorInformationEx' } else { 'unavailable' }
}
$nativeCacheInfo = [ordered]@{
    L1D = [ordered]@{ Sizes = @(); SetCounts = @(); Ways = @(); InstanceCount = 0 }
    L1I = [ordered]@{ Sizes = @(); SetCounts = @(); Ways = @(); InstanceCount = 0 }
    L1U = [ordered]@{ Sizes = @(); SetCounts = @(); Ways = @(); InstanceCount = 0 }
    L2 = [ordered]@{ Sizes = @(); SetCounts = @(); Ways = @(); InstanceCount = 0 }
    L3 = [ordered]@{ Sizes = @(); SetCounts = @(); Ways = @(); InstanceCount = 0 }
}
$nativeCacheRows = @()
foreach ($record in @(Get-WindowsCacheRecords)) {
    $parts = $record -split '\|'
    if ($parts.Count -ne 5) { continue }
    $levelNumber = [int]$parts[0]
    $typeCode = [int]$parts[1]
    $sizeBytes = [long]$parts[2]
    $lineSize = [int]$parts[3]
    $associativity = [int]$parts[4]
    $cacheKey = switch ("${levelNumber}:$typeCode") {
        '1:2' { 'L1D' }
        '1:1' { 'L1I' }
        '1:0' { 'L1U' }
        '2:0' { 'L2' }
        '2:1' { 'L2' }
        '2:2' { 'L2' }
        '3:0' { 'L3' }
        '3:1' { 'L3' }
        '3:2' { 'L3' }
        default { '' }
    }
    if (-not $cacheKey) { continue }
    $info = $nativeCacheInfo[$cacheKey]
    $sizeKb = [int][Math]::Floor($sizeBytes / 1KB)
    $info.Sizes += $sizeKb
    $info.InstanceCount++
    $levelName = "L$levelNumber"
    $kindName = switch ($typeCode) {
        0 { 'unified' }
        1 { 'instruction' }
        2 { 'data' }
        3 { 'trace' }
        default { 'unknown' }
    }
    $waysText = 'unknown-associativity'
    $setCount = $null
    if ($associativity -eq 255 -and $lineSize -gt 0) {
        $ways = [int]($sizeBytes / $lineSize)
        $setCount = 1
        $waysText = 'fully-associative'
    }
    elseif ($associativity -gt 0 -and $lineSize -gt 0) {
        $ways = $associativity
        $denominator = [long]$lineSize * $ways
        if ($denominator -gt 0 -and ($sizeBytes % $denominator) -eq 0) {
            $setCount = [int]($sizeBytes / $denominator)
        }
        $info.Ways += $ways
        $waysText = "$ways-way"
    }
    if ($null -ne $setCount) { $info.SetCounts += $setCount }
    $row = "$levelName-$kindName=${sizeKb}KB/$waysText"
    if ($null -ne $setCount) { $row += "/$setCount-sets" }
    if ($lineSize -gt 0) { $row += "/${lineSize}B-line" }
    $nativeCacheRows += $row
}
$nativeCacheRows = @($nativeCacheRows | Group-Object | ForEach-Object {
    if ($_.Count -gt 1) { "$($_.Name) x$($_.Count)" } else { $_.Name }
})
$cacheTopology = (@($cacheRows) -join '; ')
if ($nativeCacheRows.Count -gt 0) {
    $cacheTopology = $nativeCacheRows -join '; '
    $l1dSizes = @($nativeCacheInfo.L1D.Sizes | Select-Object -Unique | Sort-Object)
    $l1iSizes = @($nativeCacheInfo.L1I.Sizes | Select-Object -Unique | Sort-Object)
    $l1uSizes = @($nativeCacheInfo.L1U.Sizes | Select-Object -Unique | Sort-Object)
}
$l1dSizes = @($l1dSizes | Select-Object -Unique | Sort-Object)
$l1iSizes = @($l1iSizes | Select-Object -Unique | Sort-Object)
$l1uSizes = @($l1uSizes | Select-Object -Unique | Sort-Object)

$totalMemoryKb = if ($os.TotalVisibleMemorySize) { [string]$os.TotalVisibleMemorySize } else { '' }
$availableMemoryKb = if ($os.FreePhysicalMemory) { [string]$os.FreePhysicalMemory } else { '' }
$virtualMemoryTotalKb = if ($os.TotalVirtualMemorySize) { [string]$os.TotalVirtualMemorySize } else { '' }
$virtualMemoryAvailableKb = if ($os.FreeVirtualMemory) { [string]$os.FreeVirtualMemory } else { '' }
$virtualMemoryCommitLimitKb = if ($memoryCounters.CommitLimit) { [string][Math]::Floor([double]$memoryCounters.CommitLimit / 1KB) } else { '' }
$virtualMemoryCommittedKb = if ($memoryCounters.CommittedBytes) { [string][Math]::Floor([double]$memoryCounters.CommittedBytes / 1KB) } else { '' }
$pageFileAllocatedKb = 0L
$pageFileCurrentUsageKb = 0L
$pageFilePeakUsageKb = 0L
foreach ($pageFile in $pageFiles) {
    $pageFileAllocatedKb += ([long]$pageFile.AllocatedBaseSize * 1024)
    $pageFileCurrentUsageKb += ([long]$pageFile.CurrentUsage * 1024)
    $pageFilePeakUsageKb += ([long]$pageFile.PeakUsage * 1024)
}
if ($pageFileAllocatedKb -eq 0 -and $os.SizeStoredInPagingFiles) {
    $pageFileAllocatedKb = [long]$os.SizeStoredInPagingFiles
}
$pageFileFreeKb = if ($os.FreeSpaceInPagingFiles) { [string]$os.FreeSpaceInPagingFiles } else { '' }

$gpuDetails = @()
foreach ($gpu in $gpus) {
    $gpuDetails += "$($gpu.Name) (driver=$($gpu.DriverVersion))"
}
$ssdDetails = @()
$hddDetails = @()
$otherStorageDetails = @()
foreach ($disk in $physicalDisks) {
    $capacityGb = [Math]::Round(([double]$disk.Size / 1GB), 2)
    $name = if ($disk.FriendlyName) { [string]$disk.FriendlyName } elseif ($disk.Model) { [string]$disk.Model } else { [string]$disk.DeviceId }
    $bus = switch ([int]$disk.BusType) {
        1 { 'SCSI' }
        2 { 'ATAPI' }
        3 { 'ATA' }
        7 { 'USB' }
        9 { 'iSCSI' }
        10 { 'SAS' }
        11 { 'SATA' }
        14 { 'Virtual' }
        16 { 'Storage Spaces' }
        17 { 'NVMe' }
        18 { 'SCM' }
        default { if ($disk.BusType) { [string]$disk.BusType } else { 'unknown' } }
    }
    $detail = "$name (size=${capacityGb}GiB,bus=$bus)"
    switch ([int]$disk.MediaType) {
        3 { $hddDetails += $detail }
        4 { $ssdDetails += $detail }
        default { $otherStorageDetails += "$detail (media type=$($disk.MediaType))" }
    }
}
if ($physicalDisks.Count -eq 0) {
    foreach ($disk in $fallbackDisks) {
        $capacityGb = [Math]::Round(([double]$disk.Size / 1GB), 2)
        $name = if ($disk.Model) { [string]$disk.Model } else { [string]$disk.DeviceID }
        $otherStorageDetails += "$name (size=${capacityGb}GiB,media type unknown)"
    }
}
$ssdDevices = if ($ssdDetails.Count -gt 0) { $ssdDetails -join '; ' } else { 'none detected' }
$hddDevices = if ($hddDetails.Count -gt 0) { $hddDetails -join '; ' } else { 'none detected' }
$otherStorageDevices = $otherStorageDetails -join '; '

$powerPlan = ''
try {
    $powerPlan = (& powercfg.exe /getactivescheme 2>$null | Out-String).Trim()
}
catch {
    $powerPlan = 'unavailable'
}

$largePageMinimumBytes = ''
try {
    if (-not ('CacheSystemInfoNative' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CacheSystemInfoNative {
    [DllImport("kernel32.dll")]
    public static extern UIntPtr GetLargePageMinimum();
}
'@ -ErrorAction Stop | Out-Null
    }
    $largePageMinimumBytes = [string][CacheSystemInfoNative]::GetLargePageMinimum().ToUInt64()
}
catch {
    $largePageMinimumBytes = 'unavailable'
}

$hypervisor = if ($null -ne $computer -and $computer.HypervisorPresent) { 'present' } else { 'not reported' }
$smtActive = if ($logicalCores -gt $physicalCores -and $physicalCores -gt 0) { 'yes' } elseif ($physicalCores -gt 0) { 'no' } else { 'unavailable' }
$numaNodeIds = @($numaNodes | ForEach-Object { [string]$_.NodeNumber } | Sort-Object -Unique)
$numaNodeCount = if ($numaNodes.Count -gt 0) { [string]$numaNodes.Count } else { 'unavailable' }
$architecture = if ($processors.Count -gt 0) {
    switch ([int]$processors[0].Architecture) {
        0 { 'x86' }
        5 { 'ARM' }
        9 { 'x64' }
        12 { 'ARM64' }
        default { 'unknown' }
    }
} else { 'unavailable' }
$cpuModel = (@($processorNames | Select-Object -Unique) -join '; ')
$cpuVendor = (@($vendors | Select-Object -Unique) -join '; ')
$cpuFamily = (@($families | Select-Object -Unique) -join ',')
$cpuModelId = (@($cpuidModels | Select-Object -Unique) -join ',')
$cpuFamily = if ($cpuidFamilies.Count -gt 0) { @($cpuidFamilies | Select-Object -Unique) -join ',' } else { $cpuFamily }
$cpuStepping = if ($cpuidSteppings.Count -gt 0) { @($cpuidSteppings | Select-Object -Unique) -join ',' } else { @($steppings | Select-Object -Unique) -join ',' }
$instructionCodes = (@($instructionSets | Select-Object -Unique) -join ',')

$values = [ordered]@{
    CPU_ARCH = $architecture
    CPU_VENDOR = $cpuVendor
    CPU_MODEL = $cpuModel
    CPU_FAMILY = $cpuFamily
    CPU_MODEL_ID = $cpuModelId
    CPU_STEPPING = $cpuStepping
    CPU_SOCKET_COUNT = [string]$processors.Count
    CPU_PHYSICAL_CORES = [string]$physicalCores
    CPU_LOGICAL_CORES = [string]$logicalCores
    CPU_SMT_ACTIVE = $smtActive
    CPU_MAX_MHZ = (@($maxMhz | Select-Object -Unique | Sort-Object) -join ',')
    CPU_CURRENT_MHZ = (@($currentMhz | Select-Object -Unique | Sort-Object) -join ',')
    CPU_VIRTUALIZATION = $hypervisor
    CPU_VIRTUALIZATION_FEATURES = (@($virtualizationDetails | Select-Object -Unique) -join ',')
    CPU_INSTRUCTION_SET_CODES = $instructionCodes
    CPU_ISA_FEATURES = (Get-DotNetInstructionFeatures)
    CPU_CACHE_LINE_SIZE_BYTES = (@($cacheLineSizes) -join ',')
    CPU_CACHE_LINE_SIZE_SOURCE = $cacheLineSizeSource
    CPU_L1D_CACHE_SIZE_KB = (@($l1dSizes) -join ',')
    CPU_L1I_CACHE_SIZE_KB = (@($l1iSizes) -join ',')
    CPU_L1_UNIFIED_CACHE_SIZE_KB = (@($l1uSizes) -join ',')
    CPU_L2_CACHE_SIZE_KB = (@($l2Sizes | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L3_CACHE_SIZE_KB = (@($l3Sizes | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1_N_WAY = (@($cacheWays.L1 | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L2_N_WAY = (@($cacheWays.L2 | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L3_N_WAY = (@($cacheWays.L3 | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1D_CACHE_SIZE_PER_INSTANCE_KB = (@($nativeCacheInfo.L1D.Sizes | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1I_CACHE_SIZE_PER_INSTANCE_KB = (@($nativeCacheInfo.L1I.Sizes | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1_UNIFIED_CACHE_SIZE_PER_INSTANCE_KB = (@($nativeCacheInfo.L1U.Sizes | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L2_CACHE_SIZE_PER_INSTANCE_KB = (@($nativeCacheInfo.L2.Sizes | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L3_CACHE_SIZE_PER_INSTANCE_KB = (@($nativeCacheInfo.L3.Sizes | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1D_CACHE_SET_COUNT_PER_INSTANCE = (@($nativeCacheInfo.L1D.SetCounts | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1I_CACHE_SET_COUNT_PER_INSTANCE = (@($nativeCacheInfo.L1I.SetCounts | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1_UNIFIED_CACHE_SET_COUNT_PER_INSTANCE = (@($nativeCacheInfo.L1U.SetCounts | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L2_CACHE_SET_COUNT_PER_INSTANCE = (@($nativeCacheInfo.L2.SetCounts | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L3_CACHE_SET_COUNT_PER_INSTANCE = (@($nativeCacheInfo.L3.SetCounts | Select-Object -Unique | Sort-Object) -join ',')
    CPU_L1D_CACHE_INSTANCE_COUNT = [string]$nativeCacheInfo.L1D.InstanceCount
    CPU_L1I_CACHE_INSTANCE_COUNT = [string]$nativeCacheInfo.L1I.InstanceCount
    CPU_L1_UNIFIED_CACHE_INSTANCE_COUNT = [string]$nativeCacheInfo.L1U.InstanceCount
    CPU_L2_CACHE_INSTANCE_COUNT = [string]$nativeCacheInfo.L2.InstanceCount
    CPU_L3_CACHE_INSTANCE_COUNT = [string]$nativeCacheInfo.L3.InstanceCount
    CPU_CACHE_TOPOLOGY = $cacheTopology
    CPU_POWER_PLAN = $powerPlan
    CPU_NUMA_NODE_COUNT = $numaNodeCount
    CPU_NUMA_NODE_IDS = ($numaNodeIds -join ',')
    PAGE_SIZE_BYTES = [string][Environment]::SystemPageSize
    LARGE_PAGE_MINIMUM_BYTES = $largePageMinimumBytes
    PHYSICAL_MEMORY_TOTAL_KB = $totalMemoryKb
    PHYSICAL_MEMORY_AVAILABLE_KB = $availableMemoryKb
    VIRTUAL_MEMORY_TOTAL_KB = $virtualMemoryTotalKb
    VIRTUAL_MEMORY_AVAILABLE_KB = $virtualMemoryAvailableKb
    VIRTUAL_MEMORY_COMMIT_LIMIT_KB = $virtualMemoryCommitLimitKb
    VIRTUAL_MEMORY_COMMITTED_KB = $virtualMemoryCommittedKb
    VIRTUAL_MEMORY_BACKING_TOTAL_KB = [string]$pageFileAllocatedKb
    VIRTUAL_MEMORY_BACKING_FREE_KB = $pageFileFreeKb
    VIRTUAL_MEMORY_BACKING_USED_KB = [string]$pageFileCurrentUsageKb
    VIRTUAL_MEMORY_BACKING_PEAK_USED_KB = [string]$pageFilePeakUsageKb
    GPU_DEVICES = (@($gpuDetails) -join '; ')
    SSD_DEVICES = $ssdDevices
    HDD_DEVICES = $hddDevices
    OTHER_STORAGE_DEVICES = $otherStorageDevices
}

$lines = foreach ($entry in $values.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace([string]$entry.Value)) { continue }
    if ($entry.Key -eq 'CPU_ISA_FEATURES' -and [string]$entry.Value -like 'unavailable*') { continue }
    '{0}={1}' -f $entry.Key, (ConvertTo-EnvString $entry.Value)
}
[System.IO.File]::WriteAllLines([System.IO.Path]::GetFullPath($OutputPath), [string[]]$lines, (New-Object -TypeName System.Text.UTF8Encoding -ArgumentList $false))
Write-Output "Wrote system details to $([System.IO.Path]::GetFullPath($OutputPath))"
