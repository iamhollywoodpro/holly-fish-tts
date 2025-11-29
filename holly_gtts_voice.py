#!/usr/bin/env python3
"""
HOLLY gTTS Voice - 100% FREE FOREVER
Uses Google's free Text-to-Speech API
NO API KEYS, NO LIMITS, NO COST
"""

import os
import time
import hashlib
import numpy as np
import soundfile as sf
from typing import Optional, Dict
from pathlib import Path
from gtts import gTTS
import tempfile

HOLLY_VOICE_DESCRIPTION = """
Female voice in her 30s with an American accent. 
Confident, intelligent, warm tone with clear diction. 
Professional yet friendly, conversational pacing.
"""

# Cache directory
CACHE_DIR = Path("/tmp/holly_gtts_cache")
CACHE_DIR.mkdir(exist_ok=True)


class HollyGTTSVoice:
    """Google TTS - 100% FREE FOREVER, Unlimited"""
    
    def __init__(self):
        """Initialize gTTS"""
        print("[HOLLY gTTS] Initializing...")
        self.device = "cloud (Google's free servers)"
        print(f"[HOLLY gTTS] ✅ Ready (100% FREE FOREVER)")
        print(f"[HOLLY gTTS] Cache: {CACHE_DIR}")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path"""
        return CACHE_DIR / f"{cache_key}.wav"
    
    def _load_from_cache(self, cache_key: str) -> Optional[np.ndarray]:
        """Load from cache"""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                audio, sr = sf.read(str(cache_path))
                print(f"[HOLLY gTTS] 🎯 Cache HIT")
                return audio
            except:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, audio: np.ndarray, sample_rate: int = 24000):
        """Save to cache"""
        try:
            cache_path = self._get_cache_path(cache_key)
            sf.write(str(cache_path), audio, sample_rate)
            print(f"[HOLLY gTTS] 💾 Cached")
        except Exception as e:
            print(f"[HOLLY gTTS] ⚠️ Cache save failed: {e}")
    
    def generate(
        self,
        text: str,
        voice: str = "holly",
        use_cache: bool = True,
    ) -> tuple[np.ndarray, int]:
        """
        Generate speech using Google TTS (100% FREE)
        
        Returns:
            (audio_array, sample_rate) tuple
        """
        start_time = time.time()
        
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text)
            cached_audio = self._load_from_cache(cache_key)
            if cached_audio is not None:
                elapsed = time.time() - start_time
                print(f"[HOLLY gTTS] ⚡ Generated in {elapsed:.3f}s (cached)")
                return cached_audio, 24000
        
        print(f"[HOLLY gTTS] 🎤 Generating: {text[:50]}...")
        
        try:
            # Generate speech with gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temp MP3 file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                mp3_path = tmp.name
            
            tts.save(mp3_path)
            
            # Convert MP3 to WAV and load
            # We'll use soundfile which can read MP3 via libsndfile
            try:
                audio, sample_rate = sf.read(mp3_path)
            except:
                # If soundfile can't read MP3, use pydub as fallback
                from pydub import AudioSegment
                sound = AudioSegment.from_mp3(mp3_path)
                
                # Convert to numpy array
                samples = np.array(sound.get_array_of_samples(), dtype=np.float32)
                samples = samples / 32768.0  # Normalize to [-1, 1]
                
                # Handle stereo
                if sound.channels == 2:
                    samples = samples.reshape((-1, 2))
                    samples = samples.mean(axis=1)  # Convert to mono
                
                audio = samples
                sample_rate = sound.frame_rate
            
            os.unlink(mp3_path)
            
            elapsed = time.time() - start_time
            print(f"[HOLLY gTTS] ✅ Generated in {elapsed:.3f}s")
            
            # Cache result
            if use_cache:
                self._save_to_cache(cache_key, audio, sample_rate)
            
            return audio, sample_rate
            
        except Exception as e:
            print(f"[HOLLY gTTS] ❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            # Return silence fallback
            sample_rate = 24000
            duration = len(text) / 15
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
        """Clear cache"""
        for cache_file in CACHE_DIR.glob("*.wav"):
            cache_file.unlink()
        print("[HOLLY gTTS] 🗑️ Cache cleared")


# Singleton
_holly_voice_instance = None


def get_holly_voice() -> HollyGTTSVoice:
    """Get HOLLY voice instance"""
    global _holly_voice_instance
    if _holly_voice_instance is None:
        _holly_voice_instance = HollyGTTSVoice()
    return _holly_voice_instance
