# ZgrWise Hotfix Setup Script
Write-Host "🔥 ZgrWise Hotfix Setup Script" -ForegroundColor Red
Write-Host "================================" -ForegroundColor Red

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item env.example .env
    Write-Host "⚠️  IMPORTANT: Edit .env file and set your API_KEY and SECRET_KEY!" -ForegroundColor Red
    Write-Host "   Current values are placeholders and NOT secure!" -ForegroundColor Red
}

# Build and start services
Write-Host "🐳 Building and starting Docker services..." -ForegroundColor Blue
docker compose down
docker compose build
docker compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Run database migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Green
docker compose exec api alembic upgrade head

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Cyan
try {
    $apiHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "API: OK" -ForegroundColor Green
} catch {
    Write-Host "API: FAILED" -ForegroundColor Red
}

try {
    $webResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
    Write-Host "Web: OK" -ForegroundColor Green
} catch {
    Write-Host "Web: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Hotfix setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Service URLs:" -ForegroundColor Cyan
Write-Host "   API: http://localhost:8000" -ForegroundColor White
Write-Host "   Web: http://localhost:3000" -ForegroundColor White
Write-Host "   Redis: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Edit .env file with secure API_KEY and SECRET_KEY" -ForegroundColor White
Write-Host "   2. Test the application" -ForegroundColor White
Write-Host "   3. Check logs: docker compose logs -f" -ForegroundColor White