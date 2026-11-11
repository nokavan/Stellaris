# Синдикат Сопротивления — патчер мегаструктур для кочевников.
# Основан на NomadPatch.ps1 из «Nomad Can Build Megastructures — Mod Compatible Edition» (с разрешения автора).
# Изменено: очищается только папка этого патча (в ней лежат лишь сгенерированные файлы), сам патч пропускается.
$ModPath = $PSScriptRoot

# Dynamically get the current Windows user's "Documents" folder path
$DocsPath = [Environment]::GetFolderPath("MyDocuments")

# Construct the correct Stellaris documents directory
$StellarisDocDir = Join-Path $DocsPath "Paradox Interactive\Stellaris"
$JsonPath = Join-Path $StellarisDocDir "dlc_load.json"
Write-Host "====================================="
Write-Host "  Nomad Mega Universal Patch"
Write-Host "  nomad_mega_universal_patch"
Write-Host "====================================="
Write-Host ""
Write-Host "Reading activated mod list from launcher (dlc_load.json)..."

try {
    if (Test-Path $JsonPath) {
        $JsonContent = Get-Content $JsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($null -ne $JsonContent.enabled_mods) {
            $PlaysetModDirs = @()
            foreach ($mod in $JsonContent.enabled_mods) {
                # Skip this mod itself
                if ($mod -match "nomad_mega_universal_patch" -or $mod -match "partisan_syndicate_nomad_mega_patch") { continue }
                
                $modFile = Join-Path $StellarisDocDir $mod
                if (Test-Path $modFile) {
                    $modContent = Get-Content $modFile -Encoding UTF8
                    $pathLine = $modContent | Select-String -Pattern '^path="(.*)"'
                    if ($pathLine) {
                        $PlaysetModDirs += $pathLine.Matches[0].Groups[1].Value
                    } else {
                        $archiveLine = $modContent | Select-String -Pattern '^archive="(.*)"'
                        if ($archiveLine) {
                            # Archive format mods are not supported yet, but most Workshop mods use path/folder format
                        }
                    }
                }
            }
            Write-Host "Successfully read playset! Detected $($PlaysetModDirs.Count) other enabled mod(s)!"
        }
    } else {
        Write-Host "dlc_load.json file not found."
    }
} catch {
    Write-Host "Error reading dlc_load.json: $_"
}

$PatchMegaPath = Join-Path $ModPath "common\megastructures"
if (-not (Test-Path $PatchMegaPath)) {
    New-Item -ItemType Directory -Force -Path $PatchMegaPath | Out-Null
}

$PatchTechPath = Join-Path $ModPath "common\technology"
if (-not (Test-Path $PatchTechPath)) {
    New-Item -ItemType Directory -Force -Path $PatchTechPath | Out-Null
}

Write-Host ""
Write-Host "Cleaning up old generated third-party megastructure compatibility files..."
# Only clean non-vanilla-override files, preserve base vanilla support
Get-ChildItem -Path $PatchMegaPath -Filter "*.txt" | Remove-Item -Force -ErrorAction SilentlyContinue

# Clean previously generated tech patches (keep reference mod and base support files)
Get-ChildItem -Path $PatchTechPath -Filter "*.txt" | Remove-Item -Force -ErrorAction SilentlyContinue

if ($PlaysetModDirs.Count -eq 0) {
    Write-Host "No other enabled mods detected, or playset is empty. No additional third-party compatibility patches needed."
    Write-Host "This mod includes base vanilla megastructure support. You can launch the game directly."
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($False)
$Count = 0
$TechCount = 0

function Process-File {
    param([string]$FilePath)
    
    $rawBytes = [System.IO.File]::ReadAllBytes($FilePath)
    $content = [System.Text.Encoding]::UTF8.GetString($rawBytes)
    if ($content.Length -gt 0 -and $content[0] -eq [char]0xFEFF) {
        $content = $content.Substring(1)
    }
    
    # Skip files that already use the waystation check inline script
    if ($content -match "system_ownership_or_waystation_check") {
        return $null
    }
    
    $lines = $content -split "`r?`n"
    
    $newLines = @()
    $inPossibleBlock = $false
    $possibleStartLine = -1
    $possibleDepth = 0
    $braceDepth = 0
    $needsInjection = $false
    
    # Track negative block stack: each entry is the depth at which a NOR/NAND/NOT started
    $negativeBlockDepths = @()
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $cleanLine = $line -replace '#.*', ''
        
        $openBraces = ($cleanLine -replace '[^{]', '').Length
        $closeBraces = ($cleanLine -replace '[^}]', '').Length
        
        # Detect entry into NOR / NAND / NOT blocks (before brace depth increases)
        if ($cleanLine -match "\b(NOR|NAND|NOT)\s*=\s*\{") {
            $negativeBlockDepths += ($braceDepth + $openBraces)
        }
        
        $braceDepth += $openBraces
        
        if ($cleanLine -match "\bpossible\s*=\s*\{") {
            $inPossibleBlock = $true
            $possibleStartLine = $i
            $possibleDepth = $braceDepth
        }
        
        if ($inPossibleBlock) {
            # Check if currently inside a negative block
            $inNegative = ($negativeBlockDepths.Count -gt 0 -and $braceDepth -ge $negativeBlockDepths[-1])
            
            if ($cleanLine -match "(is_inside_border|is_within_borders_of)\s*=\s*(from|root)") {
                if ($inNegative) {
                    # Inside NOR/NAND/NOT: replace with always = no to neutralize the negative wrapper
                    $line = $line -replace "(is_inside_border|is_within_borders_of)\s*=\s*(from|root)", "always = no"
                } else {
                    $line = $line -replace "(is_inside_border|is_within_borders_of)\s*=\s*(from|root)", "always = yes"
                }
                $needsInjection = $true
            }
            if ($cleanLine -match "exists\s*=\s*starbase") {
                if ($inNegative) {
                    $line = $line -replace "exists\s*=\s*starbase", "always = no"
                } else {
                    $line = $line -replace "exists\s*=\s*starbase", "always = yes"
                }
                $needsInjection = $true
            }
        }
        
        $newLines += $line
        
        $braceDepth -= $closeBraces
        
        # Pop negative block depths when exiting them
        while ($negativeBlockDepths.Count -gt 0 -and $braceDepth -lt $negativeBlockDepths[-1]) {
            if ($negativeBlockDepths.Count -eq 1) {
                $negativeBlockDepths = @()
            } else {
                $negativeBlockDepths = $negativeBlockDepths[0..($negativeBlockDepths.Count - 2)]
            }
        }
        
        if ($inPossibleBlock -and $braceDepth -lt $possibleDepth) {
            $inPossibleBlock = $false
            if ($needsInjection) {
                $blockContent = $lines[$possibleStartLine..$i] -join "`n"
                if (-not ($blockContent -match "system_ownership_or_waystation_check")) {
                    $newLines[$possibleStartLine] = $newLines[$possibleStartLine] + "`r`n`t`tinline_script = megastructures/system_ownership_or_waystation_check"
                }
            }
        }
    }
    
    if ($needsInjection) {
        $resultContent = $newLines -join "`r`n"
        if ($resultContent -match "is_nomadic\s*=\s*no") {
            $resultContent = $resultContent -replace "is_nomadic\s*=\s*no", "always = yes"
        }
        return $resultContent
    }
    return $null
}

Write-Host ""
Write-Host "Scanning all enabled mods for megastructure files, please wait..."

foreach ($Dir in $PlaysetModDirs) {
    $TargetDir = Join-Path $Dir "common\megastructures"
    if (Test-Path $TargetDir) {
        $Files = Get-ChildItem -Path $TargetDir -Filter "*.txt"
        foreach ($File in $Files) {
            if ($File.Name -eq "00_ring_world.txt" -or $File.Name -eq "habitats.txt") { continue }
            
            Write-Host "  Processing: $($File.Name)"
            $NewContent = Process-File -FilePath $File.FullName
            if ($null -ne $NewContent) {
                $NewFilePath = Join-Path $PatchMegaPath $File.Name
                [System.IO.File]::WriteAllText($NewFilePath, $NewContent, $utf8NoBom)
                $Count++
            }
        }
    }
}

# Technology scan: lift is_nomadic = no blocks in tech files
# 科技扫描：解除科技文件中的游牧限制
Write-Host ""
Write-Host "Scanning technology files for nomad restrictions..."
Write-Host "正在扫描科技文件中的游牧限制..."

foreach ($Dir in $PlaysetModDirs) {
    $TargetDir = Join-Path $Dir "common\technology"
    if (Test-Path $TargetDir) {
        $Files = Get-ChildItem -Path $TargetDir -Filter "*.txt"
        foreach ($File in $Files) {
            $rawBytes = [System.IO.File]::ReadAllBytes($File.FullName)
            $content = [System.Text.Encoding]::UTF8.GetString($rawBytes)
            if ($content.Length -gt 0 -and $content[0] -eq [char]0xFEFF) {
                $content = $content.Substring(1)
            }
            if ($content -match "is_nomadic\s*=\s*no") {
                $newContent = $content -replace "is_nomadic\s*=\s*no", "always = yes"
                $NewFilePath = Join-Path $PatchTechPath $File.Name
                [System.IO.File]::WriteAllText($NewFilePath, $newContent, $utf8NoBom)
                $TechCount++
            }
        }
    }
}

Write-Host ""
Write-Host "====================================="
Write-Host "  Scan and replacement complete!"
Write-Host "  Successfully generated:"
Write-Host "    $Count megastructure compatibility file(s)"
Write-Host "    $TechCount technology patch file(s)"
Write-Host "====================================="
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
