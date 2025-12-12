# FixHtmlUmlautsRobust.ps1
# Run as Administrator

# ======================
# Configuration
# ======================
$rootDir   = "D:\\busineshuboffline CHATGTP\\TOGETHERSYSTEMS- GITHUB\\Nieuwe map (3)"
$backupDir = "C:\\Backups\\HtmlUmlautFixes_UltraRobust_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$logFile   = "C:\\Logs\\HtmlUmlautFix_UltraRobust_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# ======================
# Umlaut mapping (robust)
# ======================
$umlautMap = @{}
$umlautMap['ä'] = '&auml;'
$umlautMap['ö'] = '&ouml;'
$umlautMap['ü'] = '&uuml;'
$umlautMap['Ä'] = '&Auml;'
$umlautMap['Ö'] = '&Ouml;'
$umlautMap['Ü'] = '&Uuml;'
$umlautMap['ß'] = '&szlig;'

if (-not $umlautMap -or $umlautMap.Count -eq 0) {
    throw "umlautMap was not initialized correctly. Aborting."
}

# ======================
# Create necessary directories
# ======================
if (-not (Test-Path -Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}
if (-not (Test-Path -Path (Split-Path -Path $logFile -Parent))) {
    New-Item -ItemType Directory -Path (Split-Path -Path $logFile -Parent) -Force | Out-Null
}

# ======================
# Initialize counters
# ======================
$processedFiles    = 0
$modifiedFiles     = 0
$totalReplacements = 0
$filesWithUmlauts  = @()
$errorFiles        = @()

# ======================
# Log function with timestamp
# ======================
function Write-Log {
    param([string]$message)
    $timestamp  = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logMessage = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $logMessage -Encoding UTF8
    Write-Host $logMessage
}

# ======================
# Function to get file encoding
# ======================
function Get-FileEncoding {
    param([string]$filePath)

    $encodings = @(
        [System.Text.Encoding]::UTF8,
        [System.Text.UTF8Encoding]::new($false),      # UTF-8 without BOM
        [System.Text.Encoding]::GetEncoding(1252),    # Windows-1252 (ANSI)
        [System.Text.Encoding]::Default,
        [System.Text.Encoding]::Unicode,
        [System.Text.Encoding]::BigEndianUnicode
    )

    foreach ($encoding in $encodings) {
        try {
            $content = [System.IO.File]::ReadAllText($filePath, $encoding)
            return @{
                Encoding = $encoding
                Content  = $content
            }
        }
        catch {
            continue
        }
    }

    return $null
}

# ======================
# Function to safely write file
# ======================
function Write-FileSafely {
    param(
        [string]$filePath,
        [string]$content,
        [System.Text.Encoding]$encoding
    )

    $tempFile = [System.IO.Path]::GetTempFileName()
    try {
        [System.IO.File]::WriteAllText($tempFile, $content, $encoding)

        # Verify the file was written correctly
        $verifyContent = [System.IO.File]::ReadAllText($tempFile, $encoding)
        if ($verifyContent -ne $content) {
            throw "Content verification failed"
        }

        # If we got here, the file was written correctly, so move it to the destination
        Move-Item -Path $tempFile -Destination $filePath -Force -ErrorAction Stop
        return $true
    }
    catch {
        Write-Log "❌ Failed to write file: $filePath - $_"
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
        }
        return $false
    }
}

# ======================
# Start logging
# ======================
Write-Log "=== Starting Ultra-Robust HTML Umlaut Fix Process ==="
Write-Log "Root directory: $rootDir"
Write-Log "Backup directory: $backupDir"
Write-Log "Log file: $logFile"

# ======================
# Get all HTML files
# ======================
try {
    $htmlFiles  = Get-ChildItem -Path $rootDir -Include "*.html", "*.htm" -Recurse -File -ErrorAction SilentlyContinue
    $totalFiles = $htmlFiles.Count
    Write-Log "Found $totalFiles HTML files to process"

    $currentFile = 0

    foreach ($file in $htmlFiles) {
        $currentFile++
        $relativePath     = $file.FullName.Substring($rootDir.Length + 1)
        $fileChanged      = $false
        $fileReplacements = 0
        $percentComplete  = if ($totalFiles -gt 0) { [math]::Round(($currentFile / $totalFiles) * 100, 2) } else { 100 }

        Write-Progress -Activity "Processing HTML files" -Status "Processing $relativePath ($currentFile of $totalFiles)" -PercentComplete $percentComplete

        try {
            # Skip files larger than 2MB to avoid memory issues
            if ($file.Length -gt 2MB) {
                $errorMsg = "Skipping large file: $relativePath (Size: $([math]::Round($file.Length / 1MB, 2)) MB)"
                Write-Log $errorMsg
                $errorFiles += "$relativePath (File too large: $([math]::Round($file.Length / 1MB, 2)) MB)"
                continue
            }

            # Read file content with encoding detection
            $fileInfo = Get-FileEncoding -filePath $file.FullName
            if ($null -eq $fileInfo) {
                $errorMsg = "❌ Failed to read file (encoding detection failed): $relativePath"
                Write-Log $errorMsg
                $errorFiles += $errorMsg
                continue
            }

            $content  = $fileInfo.Content
            $encoding = $fileInfo.Encoding

            # Check for Umlauts
            $umlautMap.GetEnumerator() | ForEach-Object {
                $char = $_.Key
                if ($content -match [regex]::Escape($char)) {
                    $count = ([regex]::Matches($content, [regex]::Escape($char))).Count
                    $fileReplacements         += $count
                    $script:totalReplacements += $count
                    $fileChanged              = $true
                    if ($filesWithUmlauts -notcontains $relativePath) {
                        $filesWithUmlauts += $relativePath
                    }
                    Write-Log "Found $count '$char' in $relativePath"
                }
            }

            # If Umlauts found, process the file
            if ($fileChanged) {
                $modifiedFiles++

                # Create backup directory structure
                $backupPath    = Join-Path -Path $backupDir -ChildPath $relativePath
                $backupDirPath = Split-Path -Path $backupPath -Parent

                if (-not (Test-Path -Path $backupDirPath)) {
                    New-Item -ItemType Directory -Path $backupDirPath -Force | Out-Null
                }

                # Save original as backup
                try {
                    Copy-Item -Path $file.FullName -Destination $backupPath -Force
                    Write-Log "✅ Created backup: $backupPath"
                }
                catch {
                    $errorMsg = "❌ Failed to create backup for: $relativePath - $_"
                    Write-Log $errorMsg
                    $errorFiles += $errorMsg
                    throw
                }

                # Replace Umlauts
                $umlautMap.GetEnumerator() | ForEach-Object {
                    $char        = $_.Key
                    $replacement = $_.Value
                    $content     = $content -replace [regex]::Escape($char), $replacement
                }

                # Save with original encoding
                if (-not (Write-FileSafely -filePath $file.FullName -content $content -encoding $encoding)) {
                    throw "Failed to write file content"
                }

                Write-Log "✅ Fixed $fileReplacements Umlauts in $relativePath"
            }
        }
        catch {
            $errorMsg = "❌ Error processing $($file.FullName): $_"
            Write-Log $errorMsg
            $errorFiles += $errorMsg
        }
        finally {
            $processedFiles++
        }
    }
}
catch {
    $errorMsg = "❌ Error getting HTML files: $_"
    Write-Log $errorMsg
    $errorFiles += $errorMsg
}

# ======================
# Generate rollback script
# ======================
$rollbackScript = @"
# Rollback Script for HTML Umlaut Fixes
# Generated on: $(Get-Date)
# To undo all changes, run this script as Administrator

`$backupDir = "$backupDir"
`$rootDir = "$rootDir"

Write-Host "Starting rollback of HTML Umlaut fixes..." -ForegroundColor Cyan
Write-Host "Restoring files from: `$backupDir" -ForegroundColor Cyan

# Restore files from backup
Get-ChildItem -Path `$backupDir -Recurse -File | ForEach-Object {
    `$relativePath = `$_.FullName.Substring(`$backupDir.Length + 1)
    `$targetPath = Join-Path -Path `$rootDir -ChildPath `$relativePath
    `$targetDir = Split-Path -Path `$targetPath -Parent

    if (-not (Test-Path -Path `$targetDir)) {
        New-Item -ItemType Directory -Path `$targetDir -Force | Out-Null
    }

    try {
        Copy-Item -Path `$_.FullName -Destination `$targetPath -Force
        Write-Host "✅ Restored: `$relativePath" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to restore: `$relativePath - `$_" -ForegroundColor Red
    }
}

Write-Host "`nRollback complete. All files have been restored from backup." -ForegroundColor Green
Write-Host "Backup directory: `$backupDir" -ForegroundColor Cyan
Write-Host "Note: The backup directory has not been deleted. Please verify the rollback was successful before removing it." -ForegroundColor Yellow
"@

$rollbackScriptPath = Join-Path -Path $backupDir -ChildPath "Rollback-HtmlUmlautFixes.ps1"
$rollbackScript | Out-File -FilePath $rollbackScriptPath -Encoding UTF8

# ======================
# Generate summary
# ======================
$summary = @"
=== HTML Umlaut Fix Summary ===
Processed HTML files: $processedFiles
HTML files with Umlauts: $($filesWithUmlauts.Count)
Total Umlauts fixed: $totalReplacements
Files with errors: $($errorFiles.Count)
Backup location: $backupDir
Rollback script: $rollbackScriptPath
Log file: $logFile

Files with Umlauts found:
$($filesWithUmlauts -join "`n")

Files with errors:
$($errorFiles -join "`n")

To verify the changes, run this script again.
If you need to rollback, run: powershell -ExecutionPolicy Bypass -File "$rollbackScriptPath"
"@

Write-Log $summary
Write-Host $summary -ForegroundColor Cyan

# ======================
# Create a desktop shortcut to the log file
# ======================
try {
    $wshShell = New-Object -ComObject WScript.Shell
    $shortcut = $wshShell.CreateShortcut("$env:USERPROFILE\Desktop\HtmlUmlautFix_Log.lnk")
    $shortcut.TargetPath   = "notepad.exe"
    $shortcut.Arguments    = "`"$logFile`""
    $shortcut.IconLocation = "notepad.exe,0"
    $shortcut.Description  = "View HTML Umlaut Fix Log"
    $shortcut.Save()
    Write-Host "`nA shortcut to the log file has been placed on your desktop." -ForegroundColor Green
}
catch {
    Write-Log "Warning: Could not create desktop shortcut: $_"
}

Write-Host "Process complete! Check the log file for details: $logFile" -ForegroundColor Green
