param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectPath = 'E:\\starshine_quote'
)

$ErrorActionPreference = 'Stop'

function Info([string]$message) { Write-Host $message -ForegroundColor Cyan }
function Ok([string]$message)   { Write-Host $message -ForegroundColor Green }
function Fail([string]$message) { Write-Host $message -ForegroundColor Red }

if (-not (Test-Path -LiteralPath $ProjectPath)) {
    Fail "Project directory not found: $ProjectPath"
    Read-Host | Out-Null
    exit 1
}

Set-Location -LiteralPath $ProjectPath

$dart = Join-Path -Path $ProjectPath -ChildPath 'lib\main.dart'
if (-not (Test-Path -LiteralPath $dart)) {
    Fail "lib/main.dart not found at $dart"
    Read-Host | Out-Null
    exit 1
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$bak   = "${dart}.bak_${stamp}"
Copy-Item -LiteralPath $dart -Destination $bak -Force
Ok "✅ Backup created: $bak"

$fixed = @'
_card(
  title: 'Preview',
  trailing: Text(
    "Base \$${basePrice()} • Discount -\$${discountAmount} • Add-ons \$${addonsTotal}",
    style: const TextStyle(color: Color(0xB3FFFFFF)),
  ),
  child: Row(
    children: [
      const Text('TOTAL', style: TextStyle(fontSize:18,fontWeight:FontWeight.w800)),
      SizedBox(width:12),
      Text("\$${total}",style:TextStyle(fontSize:22,fontWeight:FontWeight.w900,color:Colors.cyan)),
      Spacer(),
      _clearBtn(_clearAll,label:'Clear all'),
    ],
  ),
),
'@

$content = Get-Content -LiteralPath $dart -Raw
$pattern = '(?s)_card\s*\(\s*title\s*:\s*(["''])Preview\1.*?\),'
$content = [regex]::Replace($content, $pattern, $fixed)
Set-Content -LiteralPath $dart -Value $content -Encoding UTF8
Ok '✅ Preview block patched.'

Info '🚀 Building Windows app...'
flutter run -d windows

Write-Host "`n===============================" -ForegroundColor Cyan
Write-Host 'BUILD FINISHED — PRESS ENTER TO CLOSE' -ForegroundColor Yellow
Read-Host | Out-Null
