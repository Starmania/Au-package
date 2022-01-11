$ErrorActionPreference = 'Stop';

$packageName = 'expressvpn'

#$uninstalled = $false
[array]$key = Get-UninstallRegistryKey -SoftwareName 'ExpressVPN' | ForEach-Object QuietUninstallString

if ($key.Count -ne 0) {
  $key | ForEach-Object {
    $packageArgs = @{
      packageName    = $packageName
      fileType       = 'EXE'
      silentArgs     = ''
      validExitCodes = @(0)
      file           = $key
    }
    Uninstall-ChocolateyPackage @packageArgs
  }
} elseif ($key.Count -eq 0) {
  Write-Warning "$packageName has already been uninstalled by other means."
}