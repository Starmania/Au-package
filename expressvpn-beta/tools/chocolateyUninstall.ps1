$ErrorActionPreference = 'Stop';

$packageName = 'expressvpn'

$uninstalled = $false
[string]$key = Get-UninstallRegistryKey -SoftwareName 'ExpressVPN' | ForEach-Object BundleCachePath

Write-Verbose ("Uninstallation: " + $key)

if ($null -ne $key) {

  $packageArgs = @{
    packageName    = $packageName
    fileType       = 'EXE'
    silentArgs     = '/uninstall /quiet'
    validExitCodes = @(0)
    file           = $key
  }
  
  Uninstall-ChocolateyPackage @packageArgs
}
else {
  Write-Warning "$packageName has already been uninstalled by other means."
}