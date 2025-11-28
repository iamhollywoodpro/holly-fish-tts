# 🚀 HOLLY Fish-Speech-1.5 TTS - Render.com Deployment

## One-Click Deploy (5 Minutes)

### Step 1: Push to GitHub
```bash
cd holly-fish-tts
git init
git add .
git commit -m "Initial HOLLY Fish-Speech TTS"
git remote add origin https://github.com/iamhollywoodpro/holly-fish-tts.git
git push -u origin main
```

### Step 2: Deploy to Render.com
1. Go to: https://render.com/
2. Sign up/Login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub account
5. Select repository: `holly-fish-tts`
6. Render auto-detects `render.yaml`
7. Click "Create Web Service"
8. Wait 5-8 minutes for deployment

### Step 3: Get Your API URL
After deployment completes:
- Your URL will be: `https://holly-fish-tts.onrender.com`
- Test it: `https://holly-fish-tts.onrender.com/health`

### Step 4: Update Vercel
1. Go to: https://vercel.com/iamhollywoodpros-projects/holly-ai-agent
2. Settings → Environment Variables
3. Set `TTS_API_URL` = `https://holly-fish-tts.onrender.com`
4. Redeploy

### Step 5: Test HOLLY
Go to: https://holly.nexamusicgroup.com
HOLLY should speak with Fish-Speech-1.5 voice!

## 🎯 Render.com Free Tier
- ✅ 750 hours/month FREE
- ✅ Auto-restart on crash
- ✅ Built-in SSL
- ✅ Real-time logs
- ✅ Auto-deploy on git push

## 🔧 Troubleshooting

### Check Logs
https://dashboard.render.com → Select service → Logs tab

### Check Health
```bash
curl https://holly-fish-tts.onrender.com/health
```

### Test Voice
```bash
curl "https://holly-fish-tts.onrender.com/generate?text=Hello%20Hollywood"
```

## 📊 Performance
- **Cold Start:** 20-30 seconds (first request)
- **Warm Response:** 3-5 seconds
- **Quality:** 24kHz high-quality audio
- **Emotions:** 20+ emotion tags supported

---

**DEPLOYMENT COMPLETE! 🎤✨**
