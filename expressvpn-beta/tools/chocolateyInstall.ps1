$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName    = 'expressvpn'
  fileType       = 'exe'
  url64bit       = 'https://www.expressvpn.works/clients/windows/expressvpn_windows_12.33.0.46_release.exe'
  checksum64     = '2a6879286aabef3697e859edc98004a05517bdddd6b742e1e48289fcb98d0489'
  checksumType64 = 'sha256'
  silentArgs     = '/quiet'
  validExitCodes = @(0, -2147023258) #The -2147023258 code is if app is already installed with the same version.
  softwareName   = 'expressvpn*'
}
Install-ChocolateyPackage @packageArgs
