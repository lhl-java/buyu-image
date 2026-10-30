$ErrorActionPreference='Stop'
$projectRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$catalog=Get-Content -LiteralPath (Join-Path $projectRoot 'gallery/catalog.json') -Raw|ConvertFrom-Json
$items=@($catalog.items|Where-Object{$_.available})
if($items.Count -ne 31){throw 'Overview requires all 31 completed design items'}
Add-Type -AssemblyName System.Drawing
$columns=5
$cellWidth=352
$imageHeight=198
$cellHeight=240
$gap=16
$margin=24
$header=100
$rows=[int][Math]::Ceiling($items.Count/$columns)
$canvasWidth=($margin*2)+($columns*$cellWidth)+(($columns-1)*$gap)
$canvasHeight=$header+($rows*$cellHeight)+(($rows-1)*$gap)+$margin
$canvas=[System.Drawing.Bitmap]::new($canvasWidth,$canvasHeight)
$graphics=[System.Drawing.Graphics]::FromImage($canvas)
$graphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$graphics.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$paper=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(247,240,223))
$jade=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(23,63,54))
$white=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(255,249,237))
$gold=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(192,166,107),1)
$headingFont=[System.Drawing.Font]::new('Microsoft YaHei',26,[System.Drawing.FontStyle]::Bold)
$smallFont=[System.Drawing.Font]::new('Microsoft YaHei',11)
$captionFont=[System.Drawing.Font]::new('Microsoft YaHei',11,[System.Drawing.FontStyle]::Bold)
$graphics.FillRectangle($paper,0,0,$canvasWidth,$canvasHeight)
$graphics.DrawString('捕鱼 · 道家 Q 版 UI 全套总览',$headingFont,$jade,[single]$margin,[single]18)
$graphics.DrawString('31 项设计 · 缩小拼排预览，原生整屏及逐图记录请查看本地图集',$smallFont,$jade,[single]$margin,[single]64)
$sources=for($index=0;$index -lt $items.Count;$index++){
  $item=$items[$index]
  $sourcePath=[System.IO.Path]::GetFullPath((Join-Path (Join-Path $projectRoot 'gallery') $item.image))
  $recordPath=[System.IO.Path]::GetFullPath((Join-Path (Join-Path $projectRoot 'gallery') $item.record))
  if(-not $sourcePath.StartsWith($projectRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Source outside project'}
  $col=$index%$columns
  $row=[int][Math]::Floor($index/$columns)
  $left=$margin+($col*($cellWidth+$gap))
  $top=$header+($row*($cellHeight+$gap))
  $graphics.FillRectangle($white,$left,$top,$cellWidth,$cellHeight)
  $image=[System.Drawing.Bitmap]::new($sourcePath)
  $ratio=[Math]::Min($cellWidth/$image.Width,$imageHeight/$image.Height)
  $drawWidth=[int][Math]::Round($image.Width*$ratio)
  $drawHeight=[int][Math]::Round($image.Height*$ratio)
  $dest=[System.Drawing.Rectangle]::new($left+[int](($cellWidth-$drawWidth)/2),$top+[int](($imageHeight-$drawHeight)/2),$drawWidth,$drawHeight)
  $graphics.DrawImage($image,$dest)
  $image.Dispose()
  $graphics.DrawRectangle($gold,$left,$top,$cellWidth,$cellHeight)
  $graphics.DrawString(($item.id.Substring(0,2)+' · '+$item.title),$captionFont,$jade,[single]($left+11),[single]($top+$imageHeight+10))
  [ordered]@{id=$item.id;file=$sourcePath.Substring($projectRoot.Length+1).Replace('\','/');sha256=$item.sha256;generationRecord=$recordPath.Substring($projectRoot.Length+1).Replace('\','/');row=$row;column=$col}
}
$overviewPath=Join-Path $projectRoot 'gallery/ui-overview.jpg'
$encoder=[System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders()|Where-Object{$_.MimeType -eq 'image/jpeg'}
$encoderParams=[System.Drawing.Imaging.EncoderParameters]::new(1)
$encoderParams.Param[0]=[System.Drawing.Imaging.EncoderParameter]::new([System.Drawing.Imaging.Encoder]::Quality,[long]92)
$canvas.Save($overviewPath,$encoder,$encoderParams)
$graphics.Dispose();$canvas.Dispose();$paper.Dispose();$jade.Dispose();$white.Dispose();$gold.Dispose();$headingFont.Dispose();$smallFont.Dispose();$captionFont.Dispose();$encoderParams.Dispose()
$record=[ordered]@{schemaVersion=1;file='gallery/ui-overview.jpg';sha256=(Get-FileHash -LiteralPath $overviewPath -Algorithm SHA256).Hash.ToLowerInvariant();createdAt=[DateTimeOffset]::UtcNow.ToString('o');width=$canvasWidth;height=$canvasHeight;format='JPEG';tool='System.Drawing local overview compositor';route='local_derived_preview';actualModel=$null;actualQuality=$null;operation=[ordered]@{type='reduced_thumbnail_contact_sheet';columns=$columns;cellWidth=$cellWidth;cellHeight=$cellHeight;sourceImagesUnchanged=$true;nativeDetailClaim=$false};derivedFrom=@($sources)}
$record|ConvertTo-Json -Depth 12|Set-Content -LiteralPath ($overviewPath+'.generation.json') -Encoding utf8
[ordered]@{file=$overviewPath;width=$canvasWidth;height=$canvasHeight;sources=$sources.Count}|ConvertTo-Json -Compress
