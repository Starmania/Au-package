# Renders the cheatengine package for a given version into a staging folder and
# packs it with choco. Run from the repository root on a Windows machine.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$StagingRoot = "$PSScriptRoot\..\staging",
    [switch]$Push,
    [string]$ApiKey,
    [string]$Source = 'https://push.chocolatey.org/'
)

$ErrorActionPreference = 'Stop'

$releases = Get-Content "$PSScriptRoot\releases.json" -Raw | ConvertFrom-Json
if (-not $releases.PSObject.Properties.Name.Contains($Version)) {
    throw "No release information for version $Version in releases.json."
}
$release = $releases.$Version

$staging = Join-Path $StagingRoot $Version
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Path "$staging\tools" -Force | Out-Null

# nuspec: only the version changes
(Get-Content "$PSScriptRoot\cheatengine.nuspec" -Raw) `
    -replace '<version>[\d.]+</version>', "<version>$Version</version>" |
    Set-Content "$staging\cheatengine.nuspec" -NoNewline -Encoding UTF8

# install script: url, checksum and silent args come from releases.json
$install = Get-Content "$PSScriptRoot\tools\chocolateyInstall.ps1" -Raw
$install = $install -replace "-Url '.*'", "-Url '$($release.url)'"
$install = $install -replace "-Checksum '.*'", "-Checksum '$($release.checksum)'"
$install = $install -replace "-Silent '.*'", "-Silent '$($release.silentArgs)'"
$install | Set-Content "$staging\tools\chocolateyInstall.ps1" -NoNewline -Encoding UTF8

# uninstall script: the registry display name carries the version
(Get-Content "$PSScriptRoot\tools\chocolateyUninstall.ps1" -Raw) `
    -replace 'Cheat Engine \d+\.\d+', "Cheat Engine $Version" |
    Set-Content "$staging\tools\chocolateyUninstall.ps1" -NoNewline -Encoding UTF8

Write-Host "Packing cheatengine $Version..."
choco pack "$staging\cheatengine.nuspec" --output-directory $staging
if ($LASTEXITCODE -ne 0) { throw "choco pack failed with exit code $LASTEXITCODE." }

$nupkg = Join-Path $staging "cheatengine.$Version.nupkg"
if (-not (Test-Path $nupkg)) { throw "Expected $nupkg to exist after packing." }
Write-Host "Built $nupkg"

if ($Push) {
    if ([string]::IsNullOrWhiteSpace($ApiKey)) { throw 'An API key is required to push.' }
    Write-Host "Pushing cheatengine $Version to $Source..."
    choco push $nupkg --source $Source --api-key $ApiKey
    if ($LASTEXITCODE -ne 0) { throw "choco push failed with exit code $LASTEXITCODE." }
    Write-Host "Pushed cheatengine $Version."
}
