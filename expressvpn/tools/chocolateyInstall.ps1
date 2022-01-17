$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName            = 'expressvpn'
  fileType               = 'exe'
  url64bit               = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_10.16.0.8_release.exe'
  checksum64             = '2d0443fff1429d44f61d92646a71a40cb9d599a4e1cd02018a34aeb98ecb9785'
  checksumType64         = 'sha256'
  silentArgs             = '/quiet'
  validExitCodes         = @(0,-2147023258)
  softwareName           = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
