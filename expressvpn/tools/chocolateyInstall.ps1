#http://help.preyproject.com/article/188-prey-unattended-install-for-computers

$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName            = 'prey'
  fileType               = 'msi'
  url                    = 'https://github.com/prey/prey-node-client/releases/download/v1.6.6/prey-windows-1.6.6-x86.msi'
  url64bit               = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_10.14.0.8_release.exe'
  checksum               = 'b38c383da6cfc283d9e59ab22629688f82cc4007f166563084a18680cfc450d3'
  checksum64             = 'f333857c9a2fa85e38d82ad2ad5b4cd9ba4e384e851d85fb1e8e75470c758588'
  checksumType           = 'sha256'
  checksumType64         = 'sha256'
  silentArgs             = '/qn'
  validExitCodes         = @(0)
  softwareName           = 'prey*'
}
Install-ChocolateyPackage @packageArgs
