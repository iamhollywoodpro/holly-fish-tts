#!/usr/bin/env python3
"""
HOLLY Piper TTS - 100% FREE, Self-Hosted, Unlimited
No API keys, no cloud, no limits!
"""

import os
import time
import hashlib
import numpy as np
import soundfile as sf
from typing import Optional, Dict
from pathlib import Path
import subprocess
import tempfile

HOLLY_VOICE_DESCRIPTION = """
Female voice in her 30s with an American accent. 
Confident, intelligent, warm tone with clear diction. 
Professional yet friendly, conversational pacing.
"""

# Cache directory
CACHE_DIR = Path("/tmp/holly_piper_cache")
CACHE_DIR.mkdir(exist_ok=True)

# Piper model (we'll download this automatically)
PIPER_MODEL_DIR = Path("/tmp/piper_models")
PIPER_MODEL_DIR.mkdir(exist_ok=True)

# Best female US voice for Piper
HOLLY_VOICE_MODEL = "en_US-amy-medium"


class HollyPiperVoice:
    """Piper TTS - 100% FREE, Self-Hosted"""
    
    def __init__(self):
        """Initialize Piper TTS"""
        print("[HOLLY Piper] Initializing...")
        self.device = "cpu"
        self.model_path = None
        
        # Download model if needed
        self._download_model()
        
        print(f"[HOLLY Piper] ✅ Ready (100% FREE, unlimited)")
        print(f"[HOLLY Piper] Cache: {CACHE_DIR}")
    
    def _download_model(self):
        """Download Piper voice model"""
        model_file = PIPER_MODEL_DIR / f"{HOLLY_VOICE_MODEL}.onnx"
        config_file = PIPER_MODEL_DIR / f"{HOLLY_VOICE_MODEL}.onnx.json"
        
        if model_file.exists() and config_file.exists():
            self.model_path = model_file
            print(f"[HOLLY Piper] Model already downloaded: {HOLLY_VOICE_MODEL}")
            return
        
        print(f"[HOLLY Piper] Downloading model: {HOLLY_VOICE_MODEL}...")
        
        # Download from Piper releases
        base_url = f"https://github.com/rhasspy/piper/releases/download/v1.2.0/{HOLLY_VOICE_MODEL}.onnx"
        config_url = f"{base_url}.json"
        
        try:
            import urllib.request
            
            # Download model
            print("[HOLLY Piper] Downloading voice model...")
            urllib.request.urlretrieve(base_url, model_file)
            
            # Download config
            print("[HOLLY Piper] Downloading config...")
            urllib.request.urlretrieve(config_url, config_file)
            
            self.model_path = model_file
            print("[HOLLY Piper] ✅ Model downloaded successfully!")
            
        except Exception as e:
            print(f"[HOLLY Piper] ❌ Model download failed: {e}")
            # Use fallback synthesis
            self.model_path = None
    
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
                print(f"[HOLLY Piper] 🎯 Cache HIT")
                return audio
            except:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, audio: np.ndarray, sample_rate: int = 24000):
        """Save to cache"""
        try:
            cache_path = self._get_cache_path(cache_key)
            sf.write(str(cache_path), audio, sample_rate)
            print(f"[HOLLY Piper] 💾 Cached")
        except Exception as e:
            print(f"[HOLLY Piper] ⚠️ Cache save failed: {e}")
    
    def generate(
        self,
        text: str,
        voice: str = "holly",
        use_cache: bool = True,
    ) -> tuple[np.ndarray, int]:
        """
        Generate speech using Piper TTS
        
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
                print(f"[HOLLY Piper] ⚡ Generated in {elapsed:.3f}s (cached)")
                return cached_audio, 22050
        
        print(f"[HOLLY Piper] 🎤 Generating: {text[:50]}...")
        
        try:
            # Create temp output file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name
            
            # Run Piper TTS
            cmd = [
                "piper",
                "--model", str(self.model_path),
                "--output_file", output_path
            ]
            
            # Run piper and pipe text to stdin
            process = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=30
            )
            
            if process.returncode != 0:
                raise Exception(f"Piper failed: {process.stderr.decode()}")
            
            # Load generated audio
            audio, sample_rate = sf.read(output_path)
            os.unlink(output_path)
            
            elapsed = time.time() - start_time
            print(f"[HOLLY Piper] ✅ Generated in {elapsed:.3f}s")
            
            # Cache result
            if use_cache:
                self._save_to_cache(cache_key, audio, sample_rate)
            
            return audio, sample_rate
            
        except Exception as e:
            print(f"[HOLLY Piper] ❌ Generation failed: {e}")
            # Return silence fallback
            sample_rate = 22050
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
        print("[HOLLY Piper] 🗑️ Cache cleared")


# Singleton
_holly_voice_instance = None


def get_holly_voice() -> HollyPiperVoice:
    """Get HOLLY voice instance"""
    global _holly_voice_instance
    if _holly_voice_instance is None:
        _holly_voice_instance = HollyPiperVoice()
    return _holly_voice_instance
