<#
.SYNOPSIS
  Export common Windows login/security events to CSV.

.PARAMETER StartTime
  Start time to query from. Default = 24 hours ago.

.PARAMETER EndTime
  End time to query to. Default = now.

.PARAMETER OutputPath
  CSV output path. Default = .\login-events-YYYYMMDD_HHMMSS.csv

.NOTES
  Run as Administrator to read the Security event log.
#>

param(
  [datetime]$StartTime = (Get-Date).AddDays(-1),
  [datetime]$EndTime   = (Get-Date),
  [string]$OutputPath  = "$(Join-Path -Path (Get-Location) -ChildPath ('login-events-{0}.csv' -f (Get-Date -Format 'yyyyMMdd_HHmmss')))"
)

# Event IDs commonly related to authentication/logon/logoff/privilege:
$ids = @(4624,4625,4634,4672,4768,4776,4778,4779,4647) 

function Parse-EventXml {
  param($winEvent)
  $xml = [xml]$winEvent.ToXml()
  $data = @{}
  $i = 0
  foreach($d in $xml.Event.EventData.Data) {
    $name = $d.Name
    if(-not $name -or $name -eq '') { $name = "Data$i"; $i++ }
    $data[$name] = $d.'#text'
  }
  # create a PSObject with common fields plus all EventData entries
  $obj = [PSCustomObject]@{
    TimeCreated   = $winEvent.TimeCreated
    Id            = $winEvent.Id
    LevelDisplay  = $winEvent.LevelDisplayName
    ProviderName  = $winEvent.ProviderName
    MachineName   = $winEvent.MachineName
    RecordId      = $winEvent.RecordId
    Message       = $winEvent.Message
  }
  foreach($k in $data.Keys) {
    $obj | Add-Member -NotePropertyName $k -NotePropertyValue $data[$k]
  }
  return $obj
}

Write-Host "Querying Security log: IDs $($ids -join ', ') from $StartTime to $EndTime ..." -ForegroundColor Cyan

try {
  $filter = @{
    LogName = 'Security'
    Id      = $ids
    StartTime = $StartTime
    EndTime = $EndTime
  }

  $events = Get-WinEvent -FilterHashtable $filter -ErrorAction Stop

  if(-not $events) {
    Write-Warning "No events found for that time range/IDs."
    return
  }

  $out = foreach($e in $events) {
    Parse-EventXml -winEvent $e
  }

  $out | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
  Write-Host "Exported $($out.Count) events to $OutputPath" -ForegroundColor Green
}
catch {
  Write-Error "Failed to query events: $_"
}
