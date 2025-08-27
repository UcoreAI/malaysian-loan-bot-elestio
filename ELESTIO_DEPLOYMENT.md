# 🚀 Elestio Deployment Guide

## Quick Deploy Steps

### 1. Fork This Repository
- Click "Fork" button in GitHub
- Clone to your account

### 2. Login to Elestio
- Go to https://dash.elest.io
- Sign up/Login to your account

### 3. Create CI/CD Pipeline
- Click **"CI/CD"** from left sidebar
- Click **"+ New Pipeline"**
- Select **"Git Repository"** as source
- Connect your forked repository

### 4. Configure Deployment
- **Target Type:** Deploy on new VM
- **Cloud Provider:** DigitalOcean/Vultr (recommended for Asia)
- **Region:** Singapore (closest to Malaysia)
- **Plan:** 2GB RAM / 2 CPU / 40GB Storage
- **Project Name:** malaysian-loan-bot

### 5. Set Environment Variables

**Required Variables in Elestio Dashboard:**
```bash
MASTER_DB_PASSWORD=your_secure_password_123
OPENAI_API_KEY=sk-your-actual-openai-key-here
MALAYSIAN_LOAN_WHATSAPP_TOKEN=your_whatsapp_token
EXTERNAL_CHATWOOT_URL=https://your-chatwoot.com
EXTERNAL_CHATWOOT_TOKEN=your_chatwoot_token
EXTERNAL_ERP_URL=https://your-erp.com/api
EXTERNAL_ERP_TOKEN=your_erp_token
```

### 6. Configure Reverse Proxy

In Elestio's reverse proxy settings:
- **Protocol:** HTTPS
- **Port:** 443
- **Target Protocol:** HTTP  
- **Target IP:** 172.17.0.1
- **Target Port:** 80
- **Path:** /

### 7. Deploy!
- Click **"Create CI/CD Pipeline"**
- Wait 3-5 minutes for deployment
- Get your domain: `https://your-id.elest.io`

## Post-Deployment

### Test Endpoints
```bash
# Health Check
curl https://your-domain.elest.io/health

# Webhook (should return method not allowed)
curl https://your-domain.elest.io/client/001/webhook
```

### Configure WhatsApp Webhook
Set your WhatsApp webhook URL to:
```
https://your-domain.elest.io/client/001/webhook
```

## Expected Performance
- **Memory Usage:** ~1.67GB (83% of 2GB)
- **Response Time:** <3 seconds
- **Concurrent Users:** 5-10
- **Monthly Cost:** ~$30
- **Revenue Potential:** $600/month

## Troubleshooting

### Container Not Starting
1. Check environment variables are set correctly
2. Verify OpenAI API key is valid
3. Check logs in Elestio dashboard

### Database Connection Issues
1. Ensure MASTER_DB_PASSWORD is set
2. Wait for PostgreSQL container to fully start
3. Check database logs

### WhatsApp Integration Issues
1. Verify WHATSAPP_TOKEN is valid
2. Check webhook URL is correctly set
3. Test with health endpoint first

## Architecture Overview

```
Internet → HTTPS/443 → Nginx/80 → Malaysian Bot/8080
                              ↓
                        PostgreSQL + Redis
                              ↓  
                    External CRM/ERP APIs
```

## Support
- Monitor logs via Elestio dashboard
- Use health endpoint for monitoring
- Check container resource usage in dashboard

**🎯 Your Malaysian Loan Bot is now live on Elestio!**