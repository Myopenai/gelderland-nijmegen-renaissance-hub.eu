$path = 'D:\\busineshuboffline CHATGTP\\KEAN\\scripts\\FixHtmlUmlautsRobust.ps1'

$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$null, [ref]$errors)

if ($errors -and $errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Host "ERROR: $($_.Message)" }
    exit 1
}
else {
    Write-Host 'Syntax OK'
}
