$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName            = 'expressvpn'
  fileType               = 'exe'
  url64bit               = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_10.15.0.8_release.exe'
  checksum64             = 'd404b92d7635b0d0b7c486262392dd65fcb4ba7d6d77598441b15714684ab086'
  checksumType64         = 'sha256'
  silentArgs             = '/quiet'
  validExitCodes         = @(0,-2147023258)
  softwareName           = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
