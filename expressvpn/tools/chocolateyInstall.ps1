$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName          = 'expressvpn'
  fileType             = 'exe'
  url64bit             = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_10.30.0.0_release.exe'
  checksum64           = '585dd4792148dcb6be5835760340e90099f92f1bdcd6e4562bd0a16792dea1a6'
  checksumType64       = 'sha256'
  silentArgs           = '/quiet'
  validExitCodes       = @(0,-2147023258) #The -2147023258 code is if app is already installed with the same version.
  softwareName         = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
