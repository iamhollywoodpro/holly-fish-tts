#!/usr/bin/env python3
"""
HOLLY Fish-Audio Cloud TTS
Uses Fish Audio Cloud API for high-quality TTS
"""

import os
import time
import hashlib
import numpy as np
import soundfile as sf
import requests
from typing import Optional, Dict
from pathlib import Path

HOLLY_VOICE_DESCRIPTION = """
Female voice in her 30s with an American accent. 
Confident, intelligent, warm tone with clear diction. 
Professional yet friendly, conversational pacing.
"""

# Cache directory for generated audio
CACHE_DIR = Path("/tmp/holly_fish_cache")
CACHE_DIR.mkdir(exist_ok=True)

# Fish Audio API configuration
FISH_AUDIO_API_URL = "https://api.fish.audio/v1/tts"
FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")  # Set this environment variable

# HOLLY reference voice ID (you'll need to create this in Fish Audio dashboard)
# For now, we'll use a default female voice
HOLLY_VOICE_ID = os.getenv("HOLLY_VOICE_ID", "default_female_voice")


class HollyFishVoiceCloud:
    """Fish-Audio Cloud TTS wrapper for HOLLY AI"""
    
    def __init__(self):
        """Initialize Fish-Audio Cloud client"""
        print("[HOLLY Fish-Audio Cloud] Initializing...")
        self.api_key = FISH_AUDIO_API_KEY
        self.voice_id = HOLLY_VOICE_ID
        self.device = "cloud"  # Running on Fish Audio servers
        
        if not self.api_key:
            print("[HOLLY Fish-Audio Cloud] ⚠️  No API key found! Set FISH_AUDIO_API_KEY environment variable")
            print("[HOLLY Fish-Audio Cloud] Using fallback mode...")
        
        print(f"[HOLLY Fish-Audio Cloud] ✅ Ready (cloud-based)")
        print(f"[HOLLY Fish-Audio Cloud] Cache: {CACHE_DIR}")
    
    def _get_cache_key(self, text: str, voice: str = "holly") -> str:
        """Generate cache key for text"""
        content = f"{text}:{voice}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path"""
        return CACHE_DIR / f"{cache_key}.wav"
    
    def _load_from_cache(self, cache_key: str) -> Optional[np.ndarray]:
        """Load audio from cache"""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                audio, sr = sf.read(str(cache_path))
                print(f"[HOLLY Fish-Audio Cloud] 🎯 Cache HIT: {cache_key[:8]}...")
                return audio
            except:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, audio: np.ndarray, sample_rate: int = 24000):
        """Save audio to cache"""
        try:
            cache_path = self._get_cache_path(cache_key)
            sf.write(str(cache_path), audio, sample_rate)
            print(f"[HOLLY Fish-Audio Cloud] 💾 Cached: {cache_key[:8]}...")
        except Exception as e:
            print(f"[HOLLY Fish-Audio Cloud] ⚠️  Cache save failed: {e}")
    
    def generate(
        self,
        text: str,
        voice: str = "holly",
        use_cache: bool = True,
    ) -> tuple[np.ndarray, int]:
        """
        Generate speech from text using Fish Audio Cloud API
        
        Args:
            text: Text to synthesize
            voice: Voice preset (default: holly)
            use_cache: Use caching (default: True)
        
        Returns:
            (audio_array, sample_rate) tuple
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(text, voice)
            cached_audio = self._load_from_cache(cache_key)
            if cached_audio is not None:
                elapsed = time.time() - start_time
                print(f"[HOLLY Fish-Audio Cloud] ⚡ Generated in {elapsed:.3f}s (cached)")
                return cached_audio, 24000
        
        # Generate new audio via Fish Audio API
        print(f"[HOLLY Fish-Audio Cloud] 🎤 Generating: {text[:50]}...")
        
        try:
            if not self.api_key:
                # Fallback: Generate silence with estimated duration
                print("[HOLLY Fish-Audio Cloud] ⚠️  API key not set, using fallback")
                sample_rate = 24000
                duration = len(text) / 20  # Estimate ~20 chars/second
                audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
                
                elapsed = time.time() - start_time
                print(f"[HOLLY Fish-Audio Cloud] ✅ Generated in {elapsed:.3f}s (fallback)")
                return audio, sample_rate
            
            # Call Fish Audio API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "reference_id": self.voice_id,
                "format": "wav",
                "mp3_bitrate": 128,
                "opus_bitrate": -1000,
                "latency": "normal"
            }
            
            response = requests.post(
                FISH_AUDIO_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Fish Audio API error: {response.status_code} - {response.text}")
            
            # Parse audio from response
            audio_bytes = response.content
            
            # Save to temp file and load with soundfile
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            audio, sample_rate = sf.read(tmp_path)
            os.unlink(tmp_path)
            
            elapsed = time.time() - start_time
            print(f"[HOLLY Fish-Audio Cloud] ✅ Generated in {elapsed:.3f}s")
            
            # Cache the result
            if use_cache:
                self._save_to_cache(cache_key, audio, sample_rate)
            
            return audio, sample_rate
            
        except Exception as e:
            print(f"[HOLLY Fish-Audio Cloud] ❌ Generation failed: {e}")
            # Return silence as fallback
            sample_rate = 24000
            duration = len(text) / 20
            audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
            return audio, sample_rate
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        cache_files = list(CACHE_DIR.glob("*.wav"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cached_phrases": len(cache_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(CACHE_DIR),
        }
    
    def clear_cache(self):
        """Clear all cached audio"""
        for cache_file in CACHE_DIR.glob("*.wav"):
            cache_file.unlink()
        print("[HOLLY Fish-Audio Cloud] 🗑️  Cache cleared")


# Singleton instance
_holly_voice_instance = None


def get_holly_voice() -> HollyFishVoiceCloud:
    """Get or create HOLLY voice generator instance"""
    global _holly_voice_instance
    if _holly_voice_instance is None:
        _holly_voice_instance = HollyFishVoiceCloud()
    return _holly_voice_instance
