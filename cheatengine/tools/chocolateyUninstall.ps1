﻿Uninstall-ChocolateyPackage `
  -PackageName 'cheatengine' `
  -FileType 'EXE' `
  -Silent '/VERYSILENT /NORESTART' `
  -File (Get-UninstallRegistryKey -SoftwareName 'Cheat Engine 7.5').UninstallString.Trim('"')
