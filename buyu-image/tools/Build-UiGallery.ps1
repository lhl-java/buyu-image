$ErrorActionPreference='Stop'
$projectRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$manifestPath=Join-Path $projectRoot 'docs/UI_SUITE_20261026.json'
$manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$items=foreach($task in $manifest.tasks){
  $imageRecordPath=$null
  if($task.owner -eq 'existing'){$imageRecordPath=Join-Path $projectRoot 'designs/ui/fishing-main-v1/fishing-main-v1.png.generation.json'}
  else{
    $taskDirectory=Join-Path $projectRoot $task.folder
    if(Test-Path -LiteralPath $taskDirectory){
      $candidateRecords=Get-ChildItem -LiteralPath $taskDirectory -Filter '*.png.generation.json' -File | Sort-Object LastWriteTimeUtc -Descending
      foreach($candidate in $candidateRecords){
        $candidateRecord=Get-Content -LiteralPath $candidate.FullName -Raw | ConvertFrom-Json
        if($candidateRecord.status -eq 'draft_pending_user_review' -and (Test-Path -LiteralPath (Join-Path $projectRoot $candidateRecord.file))){$imageRecordPath=$candidate.FullName;break}
      }
    }
  }
  if($imageRecordPath -and (Test-Path -LiteralPath $imageRecordPath)){
    $imageRecord=Get-Content -LiteralPath $imageRecordPath -Raw | ConvertFrom-Json
    $imagePath=Join-Path $projectRoot $imageRecord.file
    if(-not (Test-Path -LiteralPath $imagePath)){throw "Missing selected image: $imagePath"}
    if((Get-FileHash -LiteralPath $imagePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $imageRecord.sha256){throw "Image hash mismatch: $imagePath"}
    $recordRelative=$imageRecordPath.Substring($projectRoot.Length+1).Replace('\','/')
    $promptRelative=((Split-Path -Parent $imageRecordPath)+'\'+$imageRecord.prompt).Substring($projectRoot.Length+1).Replace('\','/')
    $task.status='design_complete_pending_user_review'
    $task | Add-Member -NotePropertyName selectedFile -NotePropertyValue $imageRecord.file -Force
    $task | Add-Member -NotePropertyName generationRecord -NotePropertyValue $recordRelative -Force
    [ordered]@{id=$task.id;title=$task.title;category=$task.category;available=$true;image='../'+$imageRecord.file;record='../'+$recordRelative;prompt='../'+$promptRelative;width=$imageRecord.width;height=$imageRecord.height;sha256=$imageRecord.sha256}
  }else{[ordered]@{id=$task.id;title=$task.title;category=$task.category;available=$false}}
}
$catalog=[ordered]@{updatedAt=[DateTimeOffset]::UtcNow.ToString('o');items=@($items)}
$catalogJson=$catalog|ConvertTo-Json -Depth 12
$galleryDirectory=Join-Path $projectRoot 'gallery'
New-Item -ItemType Directory -Path $galleryDirectory -Force|Out-Null
$catalogJson|Set-Content -LiteralPath (Join-Path $galleryDirectory 'catalog.json') -Encoding utf8
('window.UI_CATALOG = '+$catalogJson+';')|Set-Content -LiteralPath (Join-Path $galleryDirectory 'gallery-data.js') -Encoding utf8
$manifest|ConvertTo-Json -Depth 14|Set-Content -LiteralPath $manifestPath -Encoding utf8
[ordered]@{available=@($items|Where-Object{$_.available}).Count;total=$items.Count;gallery=(Join-Path $galleryDirectory 'index.html')}|ConvertTo-Json -Compress
