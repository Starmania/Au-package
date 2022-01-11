import-module au

$releases = 'https://www.expressvpn.com/latest#windows'

function global:au_SearchReplace {
   @{
        ".\tools\chocolateyInstall.ps1" = @{
            "(?i)(^\s*url64bit\s*=\s*)('.*')"   = "`$1'$($Latest.URL64)'"
            "(?i)(^\s*checksum64\s*=\s*)('.*')" = "`$1'$($Latest.Checksum64)'"
        }
    }
}

function global:au_GetLatest {
    $download_page = Invoke-WebRequest -Uri $releases -MaximumRedirection 0 -UseBasicParsing -UserAgent "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"

    $url64   = $download_page.Links | Where-Object href -Match '\.exe$' | ForEach-Object href | Select-Object -First 1
    $version = $url64 -split '/' | Select-Object -Last 1
    $version = $version -split '_' | Select-Object -Last 1 -Skip 1

    @{
        URL64   = $url64
        Version = $version
    }
}

update -ChecksumFor 64
