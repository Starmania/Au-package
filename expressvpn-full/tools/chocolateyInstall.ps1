$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName    = 'expressvpn-full'
  fileType       = 'exe'
  url64bit       = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_10.28.0.7_release.exe'
  checksum64     = '10b74e750ac5b4c1a79c3ad9dfd69c0985dc5cb2a773bca228f3803e85d345e3'
  checksumType64 = 'sha256'
  silentArgs     = '/quiet'
  validExitCodes = @(0, -2147023258) #The -2147023258 code is if app is already installed with the same version.
  softwareName   = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
