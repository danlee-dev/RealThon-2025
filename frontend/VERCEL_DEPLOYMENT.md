# Vercel Deployment Guide

## Prerequisites

1. Vercel account
2. GitHub repository connected to Vercel
3. Backend deployed on Railway (see backend/RAILWAY_DEPLOYMENT.md)

## Deployment Steps

### 1. Import Project to Vercel

1. Go to [Vercel](https://vercel.com)
2. Click "Add New..." > "Project"
3. Import your GitHub repository
4. Vercel will automatically detect Next.js

### 2. Configure Project Settings

**Framework Preset:** Next.js (auto-detected)

**Root Directory:** `frontend`

**Build Command:** `npm run build` (default)

**Output Directory:** `.next` (default)

**Install Command:** `npm install` (default)

### 3. Configure Environment Variables

Go to Project Settings > Environment Variables and add:

```bash
# Backend API URL (from Railway deployment)
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app

# Optional: Disable mock data in production
NEXT_PUBLIC_USE_MOCK_DATA=false
```

**Important:** Replace `https://your-backend.up.railway.app` with your actual Railway backend URL.

### 4. Deploy

Click "Deploy" and Vercel will:
1. Install dependencies
2. Build the Next.js app
3. Deploy to production

## Environment Variables Explained

### NEXT_PUBLIC_API_URL
- **Required:** Yes
- **Description:** Backend API base URL
- **Development:** `http://localhost:8000`
- **Production:** Your Railway backend URL (e.g., `https://your-app.up.railway.app`)

### NEXT_PUBLIC_USE_MOCK_DATA
- **Required:** No
- **Description:** Enable mock data mode when backend is unavailable
- **Development:** `true` (optional, for frontend-only development)
- **Production:** `false` or omit

## CORS Configuration

After deploying frontend to Vercel, update your backend CORS settings:

1. Go to Railway dashboard
2. Select your backend service
3. Add environment variable:
   ```
   ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,https://your-custom-domain.com
   ```
4. Redeploy backend

## Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Go to Project Settings > Domains
2. Add your custom domain
3. Follow Vercel's DNS configuration instructions

### Update Backend CORS

After adding custom domain, update `ALLOWED_ORIGINS` in Railway:
```
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,https://your-custom-domain.com
```

## Automatic Deployments

Vercel automatically deploys:
- **Production:** Every push to `main` branch
- **Preview:** Every pull request

## Monitoring

### Deployment Logs

View logs in Vercel dashboard under "Deployments" tab.

### Runtime Logs

View function logs in Vercel dashboard under "Logs" tab.

## Troubleshooting

### Build Fails

**Error:** `Module not found`
- **Solution:** Ensure all dependencies are in `package.json`
- Run `npm install` locally to verify

**Error:** `Type errors`
- **Solution:** Fix TypeScript errors locally
- Run `npm run build` locally to verify

### API Connection Fails

**Error:** CORS errors in browser console
- **Solution:** Add Vercel domain to backend `ALLOWED_ORIGINS`

**Error:** `Failed to fetch`
- **Solution:** Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is running on Railway

### Environment Variables Not Working

**Issue:** Changes to env vars not reflected
- **Solution:** Redeploy after changing environment variables
- Vercel requires redeploy for env var changes to take effect

## Production Checklist

- [ ] Backend deployed to Railway
- [ ] `NEXT_PUBLIC_API_URL` set to Railway backend URL
- [ ] `NEXT_PUBLIC_USE_MOCK_DATA` set to `false` or removed
- [ ] Backend `ALLOWED_ORIGINS` includes Vercel domain
- [ ] Custom domain configured (optional)
- [ ] Build succeeds locally (`npm run build`)
- [ ] TypeScript checks pass (`npm run lint`)

## Development Workflow

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Preview Deployments

Every pull request gets a unique preview URL for testing before merging to production.

### Production Deployment

```bash
# Merge to main branch
git checkout main
git merge your-feature-branch
git push origin main

# Vercel automatically deploys
```

## Cost

Vercel offers:
- **Hobby Plan:** Free for personal projects
- **Pro Plan:** $20/month for commercial projects

Features on free plan:
- Unlimited deployments
- Automatic HTTPS
- Preview deployments
- Analytics (limited)

## Performance Optimization

### Image Optimization

Next.js automatically optimizes images using `next/image`. Vercel serves optimized images at build time.

### Edge Functions

For better performance, consider using Vercel Edge Functions for API routes (if needed).

### Caching

Vercel automatically caches static assets and pages. Configure in `next.config.js` if needed.

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Support](https://vercel.com/support)
