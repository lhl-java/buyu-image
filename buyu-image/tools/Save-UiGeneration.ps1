param(
  [Parameter(Mandatory=$true)][string]$SourceImage,
  [Parameter(Mandatory=$true)][string]$RequestPath,
  [Parameter(Mandatory=$true)][string]$StartedAt,
  [Parameter(Mandatory=$true)][string]$CompletedAt,
  [string]$Review = 'Visual draft checked by producing agent; pending user review.',
  [string]$Scope = 'UI art design or state board; example values and features, no runtime integration claimed.',
  [string]$CanvasDescription = 'Landscape approx 16:9; native actual dimensions recorded, no size selector exposed.'
)
$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
function Get-ProjectRelativePath([string]$Path) {
  $absolutePath=[System.IO.Path]::GetFullPath($Path)
  if (-not $absolutePath.StartsWith($projectRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)) { throw "Path outside project: $absolutePath" }
  return $absolutePath.Substring($projectRoot.Length+1).Replace('\','/')
}
$requestAbsolute = [System.IO.Path]::GetFullPath($RequestPath)
if (-not $requestAbsolute.StartsWith($projectRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)) { throw 'Request outside project' }
$request = Get-Content -LiteralPath $requestAbsolute -Raw | ConvertFrom-Json
$outputDirectory = Split-Path -Parent $requestAbsolute
$stem = [System.IO.Path]::GetFileName($requestAbsolute) -replace '\.request\.json$',''
$outputPath = Join-Path $outputDirectory ($stem+'.png')
if (Test-Path -LiteralPath $outputPath) { throw "Output already exists: $outputPath" }
$promptPath = Join-Path $outputDirectory ($stem+'.prompt.txt')
if (-not (Test-Path -LiteralPath $promptPath)) { throw 'Missing saved prompt' }
$savedPrompt = Get-Content -LiteralPath $promptPath -Raw
if ($savedPrompt.TrimEnd() -ne $request.prompt.TrimEnd()) { throw 'Saved prompt differs from submitted request' }
$receiptPath = Join-Path $outputDirectory ($stem+'.tool-result.txt')
if (-not (Test-Path -LiteralPath $receiptPath)) { throw 'Missing tool receipt' }
Copy-Item -LiteralPath $SourceImage -Destination $outputPath
$sourceHash=(Get-FileHash -LiteralPath $SourceImage -Algorithm SHA256).Hash.ToLowerInvariant()
$outputHash=(Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceHash -ne $outputHash) { throw 'Image copy mismatch' }
Add-Type -AssemblyName System.Drawing
$bitmap=[System.Drawing.Bitmap]::new($outputPath)
$imageWidth=$bitmap.Width
$imageHeight=$bitmap.Height
$pixelFormat=$bitmap.PixelFormat.ToString()
$bitmap.Dispose()
$config=Get-Content -LiteralPath (Join-Path $projectRoot 'config/image-generation.json') -Raw | ConvertFrom-Json
$referenceRecords=foreach ($reference in $request.referenced_image_paths) {
  $relativeReference=Get-ProjectRelativePath $reference
  [ordered]@{file=$relativeReference;sha256=(Get-FileHash -LiteralPath $reference -Algorithm SHA256).Hash.ToLowerInvariant();role='Actual image input: approved Daoist Q art style and current fishing game continuity; task prompt specifies exact role.'}
}
$record=[ordered]@{
  schemaVersion=1
  file=Get-ProjectRelativePath $outputPath
  sha256=$outputHash
  generatedAt=$CompletedAt
  startedAt=$StartedAt
  width=$imageWidth
  height=$imageHeight
  format='PNG'
  pixelFormat=$pixelFormat
  tool='image_gen.imagegen'
  route='builtin'
  configSnapshot=$config
  submittedParameters=[ordered]@{model=$null;quality=$null;transparent_background=$request.transparent_background;referenced_image_paths=@($request.referenced_image_paths)}
  actualModel=$null
  actualQuality=$null
  unverifiedReason='宿主管理；工具未开放 model/quality 参数，本次结果未披露实际型号及质量。'
  evidence=[ordered]@{toolResult=[System.IO.Path]::GetFileName($receiptPath);sourceOutput=$SourceImage;toolResultId=[System.IO.Path]::GetFileNameWithoutExtension($SourceImage);request=[System.IO.Path]::GetFileName($requestAbsolute)}
  prompt=[System.IO.Path]::GetFileName($promptPath)
  references=@($referenceRecords)
  requestedCanvasInPrompt=$CanvasDescription
  resampled=$false
  status='draft_pending_user_review'
  visualReview=$Review
  scope=$Scope
}
$record | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath ($outputPath+'.generation.json') -Encoding utf8
[ordered]@{file=$record.file;width=$imageWidth;height=$imageHeight;sha256=$outputHash;record=$record.file+'.generation.json'} | ConvertTo-Json -Compress
