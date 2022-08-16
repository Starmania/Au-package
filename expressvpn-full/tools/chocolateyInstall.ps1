$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName          = 'expressvpn'
  fileType             = 'exe'
  url64bit             = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_12.29.0.17_release.exe'
  checksum64           = '0a9bdbeca37c029a83528c3cfc3ea36eee4f8c666ff1a21a2361d9b0a57b00f9'
  checksumType64       = 'sha256'
  silentArgs           = '/quiet'
  validExitCodes       = @(0,-2147023258) #The -2147023258 code is if app is already installed with the same version.
  softwareName         = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
