param([switch]$AllowPending)
$ErrorActionPreference='Stop'
$projectRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$manifest=Get-Content -LiteralPath (Join-Path $projectRoot 'docs/UI_SUITE_20261026.json') -Raw | ConvertFrom-Json
$catalog=Get-Content -LiteralPath (Join-Path $projectRoot 'gallery/catalog.json') -Raw | ConvertFrom-Json
$problems=[System.Collections.Generic.List[string]]::new()
$checked=0
$summaries=foreach($item in $catalog.items){
  if(-not $item.available){if(-not $AllowPending){$problems.Add('Pending: '+$item.id)};continue}
  $imagePath=[System.IO.Path]::GetFullPath((Join-Path (Join-Path $projectRoot 'gallery') $item.image))
  $recordPath=[System.IO.Path]::GetFullPath((Join-Path (Join-Path $projectRoot 'gallery') $item.record))
  $promptPath=[System.IO.Path]::GetFullPath((Join-Path (Join-Path $projectRoot 'gallery') $item.prompt))
  foreach($requiredPath in @($imagePath,$recordPath,$promptPath)){if(-not (Test-Path -LiteralPath $requiredPath)){$problems.Add('Missing: '+$requiredPath)}}
  if(-not (Test-Path -LiteralPath $recordPath)){continue}
  $record=Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
  $imageBytes=[System.IO.File]::ReadAllBytes($imagePath)
  if($imageBytes.Length -lt 24 -or $imageBytes[0] -ne 137 -or $imageBytes[1] -ne 80 -or $imageBytes[2] -ne 78 -or $imageBytes[3] -ne 71){$problems.Add('Invalid PNG: '+$item.id);continue}
  $pngWidth=([int64]$imageBytes[16]*16777216)+([int64]$imageBytes[17]*65536)+([int64]$imageBytes[18]*256)+$imageBytes[19]
  $pngHeight=([int64]$imageBytes[20]*16777216)+([int64]$imageBytes[21]*65536)+([int64]$imageBytes[22]*256)+$imageBytes[23]
  if($pngWidth -ne $record.width -or $pngHeight -ne $record.height){$problems.Add('Dimension mismatch: '+$item.id)}
  if((Get-FileHash -LiteralPath $imagePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $record.sha256){$problems.Add('Hash mismatch: '+$item.id)}
  if($record.resampled -ne $false){$problems.Add('Unexpected resampling: '+$item.id)}
  if($record.route -ne 'builtin'){$problems.Add('Unexpected route: '+$item.id)}
  if(-not $record.configSnapshot -or -not $record.unverifiedReason){$problems.Add('Missing model evidence declaration: '+$item.id)}
  [DateTimeOffset]::Parse($record.generatedAt)|Out-Null
  foreach($ref in @('designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png')){
    if(-not @($record.references|Where-Object{$_.file -eq $ref}).Count){$problems.Add('Missing primary style input: '+$item.id)}
  }
  if($item.id -ne '05-gameplay'){
    $receiptPath=Join-Path (Split-Path -Parent $recordPath) $record.evidence.toolResult
    $requestPath=Join-Path (Split-Path -Parent $recordPath) $record.evidence.request
    foreach($requiredPath in @($receiptPath,$requestPath)){if(-not(Test-Path -LiteralPath $requiredPath)){$problems.Add('Missing actual call evidence: '+$item.id)}}
    if(Test-Path -LiteralPath $requestPath){$request=Get-Content -LiteralPath $requestPath -Raw|ConvertFrom-Json;if((Get-Content -LiteralPath $promptPath -Raw).TrimEnd() -ne $request.prompt.TrimEnd()){$problems.Add('Prompt/request mismatch: '+$item.id)}}
  }
  $checked++
  [ordered]@{id=$item.id;file=$record.file;width=$pngWidth;height=$pngHeight;sha256=$record.sha256;model=$record.actualModel;quality=$record.actualQuality}
}
if($catalog.items.Count -ne 31 -or $manifest.tasks.Count -ne 31){$problems.Add('Expected 31 design items')}
$report=[ordered]@{checkedAt=[DateTimeOffset]::UtcNow.ToString('o');expected=31;checked=$checked;pending=31-$checked;passed=$problems.Count -eq 0;complete=$checked -eq 31;problems=@($problems);items=@($summaries);scope='File integrity and per-image evidence; visual review recorded by producing agents, not client runtime acceptance.'}
$report|ConvertTo-Json -Depth 14|Set-Content -LiteralPath (Join-Path $projectRoot 'docs/UI_SUITE_VALIDATION.json') -Encoding utf8
[ordered]@{checked=$checked;pending=31-$checked;passed=$report.passed;problems=@($problems)}|ConvertTo-Json -Depth 6 -Compress
if($problems.Count -gt 0){exit 1}
