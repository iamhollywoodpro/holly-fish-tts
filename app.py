#!/usr/bin/env python3
"""
HOLLY Fish-Speech TTS API
FastAPI microservice for Fish-Speech-1.5
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import io
import soundfile as sf

from holly_fish_voice import get_holly_voice, HOLLY_VOICE_DESCRIPTION

# Initialize FastAPI
app = FastAPI(
    title="HOLLY Fish-Speech TTS API",
    description="High-quality TTS powered by Fish-Speech-1.5",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global voice generator (lazy load)
holly_voice = None


def get_generator():
    """Get or initialize the voice generator"""
    global holly_voice
    if holly_voice is None:
        holly_voice = get_holly_voice()
    return holly_voice


class TTSRequest(BaseModel):
    """TTS generation request"""
    text: str = Field(..., description="Text to synthesize", min_length=1, max_length=5000)
    voice: Optional[str] = Field(
        "holly",
        description="Voice preset (default: holly - female, professional)"
    )
    use_cache: Optional[bool] = Field(
        True,
        description="Use voice caching for faster repeats"
    )


class TTSResponse(BaseModel):
    """TTS generation response"""
    success: bool
    duration_seconds: Optional[float] = None
    sample_rate: int = 24000
    message: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 70)
    print("🎤 HOLLY Fish-Speech TTS API Starting...")
    print("=" * 70)


@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "HOLLY Fish-Speech TTS API",
        "model": "fishaudio/fish-speech-1.5",
        "version": "1.0.0",
        "voice": "HOLLY (Female, 30s, American, confident, intelligent, warm)",
        "description": HOLLY_VOICE_DESCRIPTION,
        "features": [
            "Zero-shot voice cloning",
            "High-quality 24kHz audio",
            "Voice caching for instant repeats",
            "3-5 second generation time",
            "Professional female voice"
        ],
        "endpoints": {
            "generate": "POST /generate - Generate TTS",
            "health": "GET /health - Health check",
            "cache_stats": "GET /cache/stats - Cache statistics",
            "cache_clear": "POST /cache/clear - Clear cache"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        generator = get_generator()
        return {
            "status": "healthy",
            "model_loaded": generator is not None,
            "model": "fish-speech-1.5",
            "voice": "HOLLY",
            "device": generator.device if generator else "unknown"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/generate")
async def generate_tts(request: TTSRequest):
    """
    Generate TTS audio from text
    
    Returns 24kHz mono WAV audio
    """
    try:
        generator = get_generator()
        
        # Generate audio
        import time
        start_time = time.time()
        
        audio, sample_rate = generator.generate(
            text=request.text,
            voice=request.voice,
            use_cache=request.use_cache
        )
        
        elapsed = time.time() - start_time
        
        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        wav_bytes = buffer.read()
        
        print(f"[API] ✅ Generated {len(audio)/sample_rate:.2f}s audio in {elapsed:.3f}s")
        
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={
                "X-Duration": str(elapsed),
                "X-Sample-Rate": str(sample_rate),
                "X-Audio-Length": str(len(audio)/sample_rate)
            }
        )
        
    except Exception as e:
        print(f"[API] ❌ Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    try:
        generator = get_generator()
        stats = generator.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/clear")
async def clear_cache():
    """Clear all cached audio"""
    try:
        generator = get_generator()
        generator.clear_cache()
        return {"success": True, "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
