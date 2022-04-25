$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName          = 'expressvpn'
  fileType             = 'exe'
  url64bit             = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_10.23.0.6_release.exe'
  checksum64           = '3afc3f78415035fdefeeda47f28dbcb2c305abc5dc520129722b0b0407b21b99'
  checksumType64       = 'sha256'
  silentArgs           = '/quiet'
  validExitCodes       = @(0,-2147023258) #The -2147023258 code is if app is already installed with the same version.
  softwareName         = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
