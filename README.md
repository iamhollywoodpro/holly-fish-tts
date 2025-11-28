# 🎤 HOLLY Fish-Speech TTS

**High-quality, fast Text-to-Speech powered by Fish-Speech-1.5**

Fish-Speech-1.5 is **#2 ranked on TTS Arena** with **1M+ hours of training data**. Perfect for HOLLY AI's voice!

---

## ✨ Why Fish-Speech-1.5?

- ⚡ **5-10x FASTER than Maya1** (3-5 seconds vs 20-30 seconds)
- 🏆 **#2 ranked quality** on TTS Arena (ELO 1339)
- 🎭 **Zero-shot voice cloning** (can create custom voices)
- 🎤 **Professional female voice** for HOLLY
- 💰 **100% FREE** to self-host
- 🚀 **3-5 second generation** (acceptable speed!)

---

## 🚀 Quick Deploy to Oracle Cloud (FREE Forever)

### **One-Command Setup:**

```bash
# On your Oracle Cloud Ubuntu VM:
curl -sSL https://raw.githubusercontent.com/iamhollywoodpro/holly-fish-tts/main/setup_oracle.sh | bash
```

That's it! Wait 10-15 minutes and your TTS API will be running.

---

## 📋 Manual Setup (If you prefer step-by-step)

### **1. Create Oracle Cloud VM (Free Tier)**

1. Go to: https://www.oracle.com/cloud/free/
2. Sign up (free forever)
3. Create VM:
   - **Shape**: VM.Standard.E2.1.Micro (always free)
   - **Image**: Ubuntu 22.04
   - **RAM**: 1GB (free tier)
   - **Disk**: 50GB (free tier)
4. Note your **Public IP**

### **2. SSH into VM**

```bash
ssh ubuntu@YOUR_PUBLIC_IP
```

### **3. Run Setup Script**

```bash
curl -sSL https://raw.githubusercontent.com/iamhollywoodpro/holly-fish-tts/main/setup_oracle.sh | bash
```

### **4. Wait for Setup (10-15 minutes)**

The script will:
- ✅ Install Python 3.11
- ✅ Install Fish-Speech-1.5
- ✅ Set up FastAPI server
- ✅ Configure Nginx reverse proxy
- ✅ Create systemd service (auto-restart)
- ✅ Start the TTS API

### **5. Test Your API**

```bash
# Health check
curl http://YOUR_PUBLIC_IP/health

# Generate voice
curl -X POST http://YOUR_PUBLIC_IP/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello Hollywood! I am HOLLY, powered by Fish-Speech!"}' \
  --output holly_test.wav

# Play the audio
play holly_test.wav  # or open in audio player
```

---

## 🎯 Update HOLLY Frontend (Vercel)

Once your Oracle Cloud API is running:

1. Go to: https://vercel.com/iamhollywoodpros-projects/holly-ai-agent
2. Settings → Environment Variables
3. Add/Edit:
   - **Name**: `TTS_API_URL`
   - **Value**: `http://YOUR_ORACLE_IP`
4. Save & Redeploy

Now HOLLY will use Fish-Speech-1.5! 🎉

---

## 📊 API Endpoints

### **POST /generate**
Generate TTS from text

**Request:**
```json
{
  "text": "Hello Hollywood!",
  "voice": "holly",
  "use_cache": true
}
```

**Response:** WAV audio file (24kHz, mono)

### **GET /health**
Health check

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model": "fish-speech-1.5",
  "voice": "HOLLY"
}
```

### **GET /cache/stats**
Cache statistics

**Response:**
```json
{
  "cached_phrases": 15,
  "total_size_mb": 2.3,
  "cache_dir": "/tmp/holly_fish_cache"
}
```

### **POST /cache/clear**
Clear all cached audio

---

## 🎤 HOLLY's Voice

**Voice Description:**
- **Gender**: Female
- **Age**: 30s
- **Accent**: American
- **Tone**: Confident, intelligent, warm
- **Style**: Professional yet friendly, conversational pacing

**Generation Speed:**
- **First time**: 3-5 seconds
- **Cached**: <0.1 seconds (instant!)

---

## 🔧 Management Commands

```bash
# View logs
sudo journalctl -u holly-tts -f

# Restart service
sudo systemctl restart holly-tts

# Stop service
sudo systemctl stop holly-tts

# Start service
sudo systemctl start holly-tts

# Check status
sudo systemctl status holly-tts
```

---

## 💰 Cost

### **Oracle Cloud Free Tier:**
- ✅ **1 VM** (1 CPU, 1GB RAM) - **FREE FOREVER**
- ✅ **50GB disk** - **FREE FOREVER**
- ✅ **10TB bandwidth/month** - **FREE FOREVER**

**Your cost: $0/month** 🎉

---

## 🆚 Comparison

| Model | Speed | Quality | Emotions | Cost | Best For |
|-------|-------|---------|----------|------|----------|
| **Fish-Speech-1.5** | 3-5s | ⭐⭐⭐⭐⭐ | ✅ Yes | Free | **HOLLY** |
| Maya1 | 20-30s | ⭐⭐⭐⭐ | ✅ Yes | Free | Slow projects |
| Kokoro-82M | <1s | ⭐⭐⭐⭐ | ❌ No | Free | Speed only |

**Winner: Fish-Speech-1.5!** 🏆

---

## 📚 Documentation

- **Fish-Speech GitHub**: https://github.com/fishaudio/fish-speech
- **HuggingFace**: https://huggingface.co/fishaudio/fish-speech-1.5
- **Official Demo**: https://fish.audio/

---

## 🐛 Troubleshooting

### **Service won't start**
```bash
# Check logs
sudo journalctl -u holly-tts -f

# Common issue: Model download timeout
# Solution: Wait 5 minutes for Fish-Speech to download (~1GB)
```

### **Audio quality issues**
```bash
# Check sample rate
curl http://YOUR_IP/generate \
  -d '{"text":"test"}' \
  -o test.wav

# Inspect audio
file test.wav
# Should show: 24000 Hz, mono
```

### **Slow generation**
- First generation: 3-5 seconds (normal)
- Cached generation: <0.1 seconds
- Check cache stats: `curl http://YOUR_IP/cache/stats`

---

## 🎉 Success Checklist

- ✅ Oracle Cloud VM created
- ✅ Setup script completed
- ✅ `/health` returns `"model_loaded": true`
- ✅ `/generate` creates WAV file
- ✅ Vercel `TTS_API_URL` updated
- ✅ HOLLY speaks with new voice!

---

## 🚀 What's Next?

1. **Test HOLLY's voice** at https://holly.nexamusicgroup.com
2. **Pre-cache common phrases** (optional)
3. **Fine-tune voice** (optional - custom HOLLY voice)
4. **Add SSL certificate** (optional - for HTTPS)

---

**Built with ❤️ for HOLLY AI** 🎤

Powered by [Fish-Speech-1.5](https://github.com/fishaudio/fish-speech) 🐟
