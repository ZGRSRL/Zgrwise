# ZgrWise - Knowledge Management System

ZgrWise is a comprehensive knowledge management system that helps you collect, organize, search, and review highlights from various sources including web pages, PDFs, YouTube videos, RSS feeds, newsletters, and Kindle books.

## Features

- **Multi-source ingestion**: Web, PDF, YouTube, RSS, Newsletter, Kindle
- **AI-powered processing**: Automatic summarization and tagging using Gemini API
- **Hybrid search**: Combines text similarity and vector embeddings
- **Spaced repetition**: SM-2 algorithm for effective learning
- **Export to Obsidian**: Markdown export with frontmatter
- **Chrome extension**: Quick web clipping and highlighting
- **RSS automation**: Automatic feed monitoring and processing

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic + PostgreSQL 16 + pgvector + Redis
- **Worker**: Python (RQ) + pypdf + feedparser + trafilatura
- **AI**: Google Gemini API (summarization/auto-tagging) + sentence-transformers (embeddings)
- **Web**: Next.js 14 (App Router) + TypeScript + Tailwind CSS + React Query
- **Extensions**: Chrome MV3 web clipper + Obsidian sync plugin
- **Search**: Hybrid (pg_trgm/BM25 + cosine similarity + RRF fusion)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 2GB RAM
- Git
- Google Gemini API Key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ZgrWise
   ```

2. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Start the services**
   ```bash
   # Build and start all services
   docker compose up -d
   
   # Or use the Makefile
   make build
   make up
   ```

4. **Run database migrations**
   ```bash
   docker compose exec api alembic upgrade head
   # Or
   make migrate
   ```

5. **Verify services are running**
   ```bash
   make health
   ```

### Service URLs

- **API**: http://localhost:8000
- **Web UI**: http://localhost:3000
- **Database**: localhost:5432
- **Redis**: localhost:6379

## Usage

### 1. Web Interface

Visit http://localhost:3000 to access the main interface:

- **Inbox**: View and organize your latest sources and highlights
- **Search**: Find highlights using hybrid search (text + AI)
- **Review**: Practice with spaced repetition system
- **RSS**: Manage and monitor your RSS subscriptions
- **Settings**: Configure export paths and API settings

### 2. RSS Feeds

Add RSS feeds through the web interface or API:

```bash
curl -X POST http://localhost:8000/api/rss/feeds \
  -H "X-API-Key: devkey" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://hnrss.org/frontpage", "title": "Hacker News"}'
```

### 3. Chrome Extension

1. Load the extension from `apps/extension/` as an unpacked extension
2. Configure API base URL and key in extension options
3. Right-click on selected text → "Save Selection to ZgrWise"

### 4. Obsidian Integration

1. Install the plugin from `apps/obsidian-plugin/`
2. Configure API settings in Obsidian settings
3. Use command "Pull new highlights from ZgrWise"

### 5. API Usage

All API endpoints require the `X-API-Key` header:

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Create highlight
curl -X POST http://localhost:8000/api/highlights \
  -H "X-API-Key: devkey" \
  -H "Content-Type: application/json" \
  -d '{"source_id": 1, "text": "Your highlight text"}'

# Search highlights
curl -X POST http://localhost:8000/api/search \
  -H "X-API-Key: devkey" \
  -H "Content-Type: application/json" \
  -d '{"q": "search query", "limit": 20}'
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql+psycopg://zgr:zgrpass@db:5432/zgrwise

# Redis
REDIS_URL=redis://redis:6379/0

# AI Service (Gemini)
GEMINI_API_KEY=your-gemini-api-key-here
AI_MODEL=gemini-1.5-flash

# Embeddings
EMB_MODEL=BAAI/bge-small-en-v1.5
EMB_DIM=384

# API Security
API_KEY=your-secure-api-key-here
SECRET_KEY=your-secret-key-here

# CORS
CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:8501

# Export
OBSIDIAN_EXPORT_PATH=./data/exports
```

### Gemini API Setup

1. Get your free Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Add it to your `.env` file:
   ```bash
   GEMINI_API_KEY=your-actual-api-key-here
   ```
3. The system will automatically use Gemini for AI processing

## Development

### Project Structure

```
ZgrWise/
├── apps/
│   ├── api/                 # FastAPI backend
│   ├── worker/              # Background task processor
│   └── web/                 # Next.js frontend
├── packages/
│   └── shared/              # Common schemas and types
├── tools/
│   └── db/                  # Database initialization
├── docker-compose.yml       # Service orchestration
├── Makefile                 # Development commands
└── README.md
```

### Development Commands

```bash
# Start all services
make up

# Stop all services
make down

# View logs
make logs

# Run migrations
make migrate

# Check service health
make health

# Clean up everything
make clean
```

### Adding New Features

1. **API Endpoints**: Add routes in `apps/api/app/routes/`
2. **Background Tasks**: Create tasks in `apps/worker/worker/tasks/`
3. **Database Models**: Update `apps/api/app/models.py` and run migrations
4. **Frontend**: Add pages in `apps/web/app/`

## Troubleshooting

### Common Issues

1. **Services not starting**
   - Check Docker is running
   - Verify ports are available (8000, 3000, 5432, 6379, 11434)
   - Check service logs: `make logs`

2. **Database connection errors**
   - Wait for PostgreSQL to fully start (health checks)
   - Verify database credentials in `.env`
   - Check if migrations ran: `make migrate`

3. **Gemini API errors**
   - Verify your API key is correct in `.env`
   - Check API quota and limits in Google AI Studio
   - Ensure internet connection for API calls

4. **API authentication errors**
   - Verify `API_KEY` in `.env` matches request headers
   - Check API service is running: `make health`

### Logs and Debugging

```bash
# View all service logs
make logs

# View specific service logs
make api-logs
make worker-logs
make web-logs

# Check service health
make health

# Access database directly
docker compose exec db psql -U zgr -d zgrwise
```

## Performance and Scaling

### Resource Requirements

- **Minimum**: 2GB RAM, 2 CPU cores
- **Recommended**: 4GB RAM, 4 CPU cores
- **Production**: 8GB+ RAM, 8+ CPU cores

### Optimization Tips

1. **Database**: Use connection pooling and proper indexing
2. **Embeddings**: Batch process embeddings for better throughput
3. **Caching**: Redis caching for frequently accessed data
4. **Background Tasks**: Use worker queues for heavy processing

## Security

- API key authentication for all endpoints
- CORS configured for local development
- Database connections use environment variables
- No sensitive data in code or logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review service logs
- Open an issue on GitHub

---

**Happy knowledge management! 🧠✨** 