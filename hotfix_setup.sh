#!/bin/bash

echo "🔥 ZgrWise Hotfix Setup Script"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp env.example .env
    echo "⚠️  IMPORTANT: Edit .env file and set your API_KEY and SECRET_KEY!"
    echo "   Current values are placeholders and NOT secure!"
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker compose down
docker compose build
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker compose exec api alembic upgrade head

# Check service health
echo "🏥 Checking service health..."
echo "API: $(curl -s http://localhost:8000/health || echo 'FAILED')"
echo "Web: $(curl -s http://localhost:3000 > /dev/null && echo 'OK' || echo 'FAILED')"
echo "Redis: $(docker compose exec redis redis-cli ping || echo 'FAILED')"

echo ""
echo "✅ Hotfix setup complete!"
echo ""
echo "🔗 Service URLs:"
echo "   API: http://localhost:8000"
echo "   Web: http://localhost:3000"
echo "   Redis: localhost:6379"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with secure API_KEY and SECRET_KEY"
echo "   2. Test the application"
echo "   3. Check logs: docker compose logs -f"