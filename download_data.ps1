# Download PDFs for Module 3 exercises
# PowerShell version of download_data.sh

Write-Host "=== Downloading PDF Files for Session 9 ===" -ForegroundColor Cyan
Write-Host ""

# Create directories
$capDir = "data/climate-action-plans"
$corpDir = "data/corporate-sustainability"

New-Item -ItemType Directory -Force -Path $capDir | Out-Null
New-Item -ItemType Directory -Force -Path $corpDir | Out-Null

function Download-PDF {
    param(
        [string]$Dir,
        [string]$FileName,
        [string]$Url
    )
    
    $filePath = Join-Path $Dir $FileName
    
    if (Test-Path $filePath) {
        Write-Host "  [OK] Already exists: $FileName" -ForegroundColor Green
        return
    }
    
    Write-Host "  [Downloading] $FileName" -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $Url -OutFile $filePath -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        $fileSize = (Get-Item $filePath).Length / 1MB
        Write-Host "  [OK] $FileName - $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
    }
    catch {
        Write-Host "  [FAILED] $FileName - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "=== Climate Action Plans ===" -ForegroundColor Cyan

Download-PDF $capDir "oakland-ecap-2020.pdf" `
    "https://cao-94612.s3.amazonaws.com/documents/Oakland-ECAP-07-24.pdf"

Download-PDF $capDir "portland-cap-2015.pdf" `
    "https://www.portland.gov/sites/default/files/2019-07/cap-2015_june30-2015_web_0.pdf"

Download-PDF $capDir "austin-climate-equity-2021.pdf" `
    "https://www.austintexas.gov/sites/default/files/files/Sustainability/Climate%20Equity%20Plan/Climate%20Equity%20Plan%20Full%20Document__FINAL.pdf"

Download-PDF $capDir "seattle-cap-2013.pdf" `
    "https://www.seattle.gov/documents/Departments/Environment/ClimateChange/2013_CAP_20130612.pdf"

Download-PDF $capDir "annarbor-a2zero-2020.pdf" `
    "https://www.a2gov.org/departments/sustainability/Documents/A2ZERO%20Climate%20Action%20Plan%20_3.0.pdf"

Download-PDF $capDir "ca-scoping-plan-2022.pdf" `
    "https://ww2.arb.ca.gov/sites/default/files/2023-04/2022-sp.pdf"

Download-PDF $capDir "ipcc-ar6-wg3-spm.pdf" `
    "https://www.ipcc.ch/report/ar6/wg3/downloads/report/IPCC_AR6_WGIII_SummaryForPolicymakers.pdf"

Write-Host ""
Write-Host "=== Corporate Sustainability Reports ===" -ForegroundColor Cyan

Download-PDF $corpDir "apple-env-2024.pdf" `
    "https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2024.pdf"

Download-PDF $corpDir "microsoft-sustainability-2023.pdf" `
    "https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RW1lMjE"

Download-PDF $corpDir "amazon-sustainability-2022.pdf" `
    "https://sustainability.aboutamazon.com/2022-sustainability-report.pdf"

Download-PDF $corpDir "google-env-report-2023.pdf" `
    "https://www.gstatic.com/gumdrop/sustainability/google-2023-environmental-report.pdf"

Write-Host ""
Write-Host "=== Download Complete ===" -ForegroundColor Green
Write-Host "PDFs saved to:" -ForegroundColor Cyan
Write-Host "  - $capDir" -ForegroundColor White
Write-Host "  - $corpDir" -ForegroundColor White
