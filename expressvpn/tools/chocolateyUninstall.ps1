#Import-Module "$env:ChocolateyInstall\helpers\chocolateyInstaller.psm1" -Force
$ErrorActionPreference = 'Stop';

$packageName = 'expressvpn'

#$uninstalled = $false
[array]$key = Get-UninstallRegistryKey -SoftwareName 'ExpressVPN' | ForEach-Object BundleCachePath

if ($null -ne $key) {

    $packageArgs = @{
      packageName    = $packageName
      fileType       = 'EXE'
      silentArgs     = '/uninstall /quiet'
      validExitCodes = @(0)
      file           = $key[0]
    }
  
    Uninstall-ChocolateyPackage @packageArgs
} else {
  Write-Warning "$packageName has already been uninstalled by other means."
}