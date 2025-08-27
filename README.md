# Malaysian Loan Bot - Elestio Deployment

Production-ready Malaysian Loan Consultant AI Bot optimized for 2GB/2CPU Elestio VPS deployment.

## 🚀 Quick Deploy to Elestio

1. **Fork this repository** to your GitHub account
2. **Login to Elestio Dashboard** → https://dash.elest.io
3. **Go to CI/CD** → **New Pipeline**
4. **Select "Git Repository"** as deployment source
5. **Connect your forked repository**
6. **Choose deployment target:** 2GB/2CPU VPS
7. **Set environment variables** (see below)
8. **Deploy!**

## 📋 Required Environment Variables

Set these in Elestio's environment variables section:

```bash
MASTER_DB_PASSWORD=your_secure_database_password_2025
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
MALAYSIAN_LOAN_WHATSAPP_TOKEN=your_whatsapp_business_api_token
EXTERNAL_CHATWOOT_URL=https://your-chatwoot-domain.com
EXTERNAL_CHATWOOT_TOKEN=your_chatwoot_api_token
EXTERNAL_ERP_URL=https://your-erp-system.com/api
EXTERNAL_ERP_TOKEN=your_erp_api_token
```

## 🔧 Reverse Proxy Configuration

In Elestio's reverse proxy settings:
- **Protocol:** HTTPS
- **Port:** 443
- **Target Protocol:** HTTP
- **Target IP:** 172.17.0.1
- **Target Port:** 80
- **Path:** /

## 📊 Resource Allocation (2GB VPS)

```
Container Memory Breakdown:
┌─────────────────────────────────────┐
│  PostgreSQL:        200MB (10%)     │
│  Redis:              50MB (2.5%)    │
│  Malaysian Bot:   1,200MB (60%)     │
│  Nginx:              15MB (0.8%)    │
│  System Overhead:   200MB (10%)     │
├─────────────────────────────────────┤
│  TOTAL USAGE:     1,665MB (83%)     │
│  AVAILABLE:         335MB (17%)     │
│  VPS LIMIT:       2,000MB (100%)    │
└─────────────────────────────────────┘
```

## 🔗 Post-Deployment Setup

After successful deployment:

1. **Get your domain:** `https://your-unique-id.elest.io`
2. **Test health endpoint:** `https://your-domain/health`
3. **Configure WhatsApp webhook:** `https://your-domain/client/001/webhook`
4. **Monitor logs** via Elestio dashboard

## 💰 Expected Performance

- **Memory Usage:** ~1.67GB (83% of 2GB)
- **Response Time:** <3 seconds
- **Uptime:** >99%
- **Concurrent Users:** 5-10 simultaneously
- **Monthly Cost:** ~$30/month
- **Revenue Potential:** $600/month (1 client)
- **Profit:** $570/month (95% margin)

## 🏗️ Architecture

```
Internet → HTTPS (443) → Nginx (80) → Malaysian Loan Bot (8080)
                                   ↓
                              PostgreSQL (5432) + Redis (6379)
                                   ↓
                           External CRM/ERP APIs
```

## 📞 Support

- Malaysian Loan Bot handles WhatsApp conversations
- Integrates with your existing Chatwoot CRM
- Connects to your existing ERP system
- Automated loan application processing
- RAG-enabled document analysis

**🎯 Ready for immediate deployment to Elestio!**