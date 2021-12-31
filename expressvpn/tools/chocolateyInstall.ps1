$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName            = 'expressvpn'
  fileType               = 'exe'
  url64bit               = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_10.14.0.8_release.exe'
  checksum64             = 'f333857c9a2fa85e38d82ad2ad5b4cd9ba4e384e851d85fb1e8e75470c758588'
  checksumType64         = 'sha256'
  silentArgs             = '/qn'
  validExitCodes         = @(0)
  softwareName           = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
