# Railway Deployment Guide

## Prerequisites

1. Railway account
2. GitHub repository connected to Railway
3. PostgreSQL database provisioned in Railway

## Deployment Steps

### 1. Create New Project on Railway

1. Go to [Railway](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose this repository
5. Set root directory to `/backend`

### 2. Add PostgreSQL Database

1. Click "+ New" in your project
2. Select "Database" > "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable

### 3. Configure Environment Variables

Go to your service settings and add these environment variables:

```bash
# Database (automatically set by Railway)
DATABASE_URL=<automatically set>

# Authentication
SECRET_KEY=<generate with: openssl rand -hex 32>

# LLM API
GEMINI_API_KEY=<your Gemini API key>
GEMINI_API_KEY1=<optional second key>
GEMINI_API_KEY2=<optional third key>

# GitHub Integration (optional)
GITHUB_TOKEN=<your GitHub token>

# CORS - Frontend URLs (comma-separated)
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Optional: A6000 GPU Server
USE_A6000_MODELS=false
A6000_STT_URL=<GPU server URL for STT>
A6000_TTS_URL=<GPU server URL for TTS>
```

### 4. Generate SECRET_KEY

Run this command locally:
```bash
openssl rand -hex 32
```

Copy the output and paste it as `SECRET_KEY` in Railway.

### 5. Deploy

Railway will automatically deploy when you push to your GitHub repository.

## Important Notes

### ML Dependencies

The backend includes heavy ML dependencies:
- torch (~2GB)
- opencv-python (~100MB)
- mediapipe (~50MB)
- openai-whisper (includes model downloads)

**Build Time:** Expect 5-10 minutes for first deployment

**Memory Usage:** Recommend at least 2GB RAM

**Alternative:** Use A6000 GPU server for ML processing (set `USE_A6000_MODELS=true`)

### File Uploads

Railway uses ephemeral filesystem. Uploaded files will be lost on redeploy.

**Solutions:**
1. Use cloud storage (AWS S3, Google Cloud Storage)
2. Use Railway Volumes (persistent storage)
3. Store files in PostgreSQL as BYTEA (not recommended for large files)

### Database Migration

First deployment will automatically create all tables (models are in `models.py`).

For future schema changes, consider using Alembic for migrations.

## Monitoring

### Health Check

```
GET https://your-railway-domain.up.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Logs

View logs in Railway dashboard under "Deployments" tab.

## Troubleshooting

### Build Fails

- Check Railway build logs
- Verify all dependencies in requirements.txt are compatible
- Consider removing heavy ML dependencies if not needed

### Database Connection Error

- Verify `DATABASE_URL` is set by Railway PostgreSQL
- Check database is running
- Ensure `psycopg2-binary` is in requirements.txt

### CORS Errors

- Add your frontend domain to `ALLOWED_ORIGINS`
- Use comma-separated list for multiple domains
- Include both `https://` and `https://www.` if needed

## Production Checklist

- [ ] `SECRET_KEY` set to secure random value
- [ ] `ALLOWED_ORIGINS` set to production domain(s)
- [ ] PostgreSQL database provisioned
- [ ] All API keys configured (GEMINI_API_KEY, GITHUB_TOKEN)
- [ ] Health check endpoint returns "healthy"
- [ ] File upload strategy decided (cloud storage or volumes)
- [ ] Monitoring and alerts configured

## Cost Optimization

### Option 1: Lightweight Deploy (Recommended for MVP)
- Remove heavy ML dependencies
- Use external APIs (OpenAI Whisper API)
- Keep only core FastAPI + Gemini
- Estimated: $5-10/month

### Option 2: Full Stack Deploy
- Keep all ML dependencies
- Use Railway Pro plan for more resources
- Estimated: $20-30/month

### Option 3: Hybrid
- Deploy lightweight backend to Railway
- Use separate A6000 GPU server for ML
- Set `USE_A6000_MODELS=true`
- Estimated: $5-10/month (Railway) + GPU server cost
