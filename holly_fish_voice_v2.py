#!/usr/bin/env python3
"""
HOLLY Fish-Speech-1.5 Voice Generator - REAL IMPLEMENTATION
Uses Fish-Speech's inference engine directly
"""

import os
import sys
import time
import hashlib
import numpy as np
import soundfile as sf
import torch
from typing import Optional, Dict
from pathlib import Path

# Add fish-speech to path
FISH_SPEECH_PATH = Path(__file__).parent / "fish-speech-repo"
sys.path.insert(0, str(FISH_SPEECH_PATH))

from fish_speech.inference_engine import TTSInferenceEngine
from fish_speech.models.vqgan.modules.firefly import FireflyArchitecture

HOLLY_VOICE_DESCRIPTION = """
Female voice in her 30s with an American accent. 
Confident, intelligent, warm tone with clear diction. 
Professional yet friendly, conversational pacing.
"""

# Cache directory for generated audio
CACHE_DIR = Path("/tmp/holly_fish_cache")
CACHE_DIR.mkdir(exist_ok=True)

# Reference audio directory
REF_AUDIO_DIR = Path(__file__).parent / "reference_audio"
REF_AUDIO_DIR.mkdir(exist_ok=True)


class HollyFishVoice:
    """Fish-Speech-1.5 TTS wrapper for HOLLY AI - REAL IMPLEMENTATION"""
    
    def __init__(self):
        """Initialize Fish-Speech model"""
        print("[HOLLY Fish-Speech] Initializing REAL Fish-Speech-1.5...")
        
        # Check device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[HOLLY Fish-Speech] Device: {self.device}")
        
        # Model paths
        self.llama_checkpoint = os.getenv(
            "LLAMA_CHECKPOINT",
            "fishaudio/fish-speech-1.5"
        )
        self.decoder_checkpoint = os.getenv(
            "DECODER_CHECKPOINT", 
            "fishaudio/fish-speech-1.5"
        )
        
        # Load models
        print("[HOLLY Fish-Speech] Loading models...")
        try:
            self.engine = TTSInferenceEngine(
                llama_checkpoint_path=self.llama_checkpoint,
                decoder_checkpoint_path=self.decoder_checkpoint,
                decoder_config_name="firefly_gan_vq",
                device=self.device,
                half=False,  # Use full precision for CPU
                compile=False,  # Don't compile for compatibility
            )
            print("[HOLLY Fish-Speech] ✅ Models loaded successfully!")
        except Exception as e:
            print(f"[HOLLY Fish-Speech] ❌ Failed to load models: {e}")
            print("[HOLLY Fish-Speech] Falling back to checkpoint download...")
            # Try to download models
            self._download_models()
            self.engine = TTSInferenceEngine(
                llama_checkpoint_path=self.llama_checkpoint,
                decoder_checkpoint_path=self.decoder_checkpoint,
                decoder_config_name="firefly_gan_vq",
                device=self.device,
                half=False,
                compile=False,
            )
        
        # Load or create reference audio
        self.reference_audio = self._load_reference_audio()
        
        print(f"[HOLLY Fish-Speech] ✅ Ready!")
        print(f"[HOLLY Fish-Speech] Cache: {CACHE_DIR}")
        print(f"[HOLLY Fish-Speech] Reference: {self.reference_audio}")
    
    def _download_models(self):
        """Download Fish-Speech models from HuggingFace"""
        from huggingface_hub import snapshot_download
        
        print("[HOLLY Fish-Speech] Downloading models from HuggingFace...")
        
        # Download LLAMA model
        snapshot_download(
            repo_id="fishaudio/fish-speech-1.5",
            local_dir="./checkpoints/fish-speech-1.5",
            local_dir_use_symlinks=False,
        )
        
        self.llama_checkpoint = "./checkpoints/fish-speech-1.5"
        self.decoder_checkpoint = "./checkpoints/fish-speech-1.5"
        
        print("[HOLLY Fish-Speech] ✅ Models downloaded!")
    
    def _load_reference_audio(self) -> Optional[np.ndarray]:
        """Load reference audio for voice cloning"""
        # Check for existing reference audio
        ref_files = list(REF_AUDIO_DIR.glob("*.wav"))
        
        if ref_files:
            ref_path = ref_files[0]
            audio, sr = sf.read(str(ref_path))
            print(f"[HOLLY Fish-Speech] Loaded reference audio: {ref_path.name}")
            return audio
        
        # If no reference audio, create a silent one as placeholder
        # In production, you should provide a real voice sample
        print("[HOLLY Fish-Speech] ⚠️ No reference audio found!")
        print("[HOLLY Fish-Speech] Please add a WAV file to: reference_audio/")
        return None
    
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
                print(f"[HOLLY Fish-Speech] 🎯 Cache HIT: {cache_key[:8]}...")
                return audio
            except:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, audio: np.ndarray, sample_rate: int = 24000):
        """Save audio to cache"""
        try:
            cache_path = self._get_cache_path(cache_key)
            sf.write(str(cache_path), audio, sample_rate)
            print(f"[HOLLY Fish-Speech] 💾 Cached: {cache_key[:8]}...")
        except Exception as e:
            print(f"[HOLLY Fish-Speech] ⚠️ Cache save failed: {e}")
    
    def generate(
        self,
        text: str,
        voice: str = "holly",
        use_cache: bool = True,
    ) -> tuple[np.ndarray, int]:
        """
        Generate speech from text using Fish-Speech-1.5
        
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
                print(f"[HOLLY Fish-Speech] ⚡ Generated in {elapsed:.3f}s (cached)")
                return cached_audio, 24000
        
        # Generate new audio using Fish-Speech
        print(f"[HOLLY Fish-Speech] 🎤 Generating: {text[:50]}...")
        
        try:
            # Prepare references (if available)
            references = []
            if self.reference_audio is not None:
                references = [{
                    "audio": self.reference_audio,
                    "text": HOLLY_VOICE_DESCRIPTION,
                }]
            
            # Generate audio using the engine
            result = self.engine.inference(
                text=text,
                references=references,
                max_new_tokens=1024,
                chunk_length=200,
                top_p=0.8,
                repetition_penalty=1.1,
                temperature=0.8,
            )
            
            # Extract audio from result
            if hasattr(result, 'audio'):
                audio = result.audio
            elif isinstance(result, dict) and 'audio' in result:
                audio = result['audio']
            else:
                audio = result
            
            # Convert to numpy array if needed
            if torch.is_tensor(audio):
                audio = audio.cpu().numpy()
            
            # Ensure float32
            audio = audio.astype(np.float32)
            
            sample_rate = 24000
            elapsed = time.time() - start_time
            
            print(f"[HOLLY Fish-Speech] ✅ Generated {len(audio)/sample_rate:.2f}s audio in {elapsed:.3f}s")
            
            # Cache the result
            if use_cache:
                self._save_to_cache(cache_key, audio, sample_rate)
            
            return audio, sample_rate
            
        except Exception as e:
            print(f"[HOLLY Fish-Speech] ❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Return short beep as fallback
            print("[HOLLY Fish-Speech] Returning fallback beep")
            sample_rate = 24000
            duration = 0.5
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = (np.sin(2 * np.pi * 440 * t) * 0.3).astype(np.float32)
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
        print("[HOLLY Fish-Speech] 🗑️ Cache cleared")


# Singleton instance
_holly_voice_instance = None


def get_holly_voice() -> HollyFishVoice:
    """Get or create HOLLY voice generator instance"""
    global _holly_voice_instance
    if _holly_voice_instance is None:
        _holly_voice_instance = HollyFishVoice()
    return _holly_voice_instance


if __name__ == "__main__":
    # Test the voice generator
    print("=" * 50)
    print("HOLLY Fish-Speech Voice Generator - REAL TEST")
    print("=" * 50)
    
    holly = get_holly_voice()
    
    # Test generation
    test_text = "Hello Hollywood! I am HOLLY, powered by Fish-Speech-1.5!"
    print(f"\nTest text: {test_text}")
    
    audio, sr = holly.generate(test_text)
    print(f"Audio shape: {audio.shape}")
    print(f"Sample rate: {sr} Hz")
    print(f"Duration: {len(audio) / sr:.2f} seconds")
    
    # Check if it's actually audio (not silence)
    max_amplitude = np.max(np.abs(audio))
    print(f"Max amplitude: {max_amplitude}")
    
    if max_amplitude < 0.001:
        print("⚠️ WARNING: Audio is silent or very quiet!")
    else:
        print("✅ Audio contains sound data!")
    
    # Save test output
    output_file = "holly_test_real.wav"
    sf.write(output_file, audio, sr)
    print(f"\n✅ Saved to: {output_file}")
    
    # Cache stats
    stats = holly.get_cache_stats()
    print(f"\nCache stats: {stats}")
