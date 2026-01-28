"""Pre-download all models (rembg + flux2-klein) for Docker image building."""

import os
import sys

print("=" * 60)
print("Pre-downloading all models for Docker image")
print("=" * 60)

# 1. Download rembg model
print("\n[1/2] Downloading rembg model...")
try:
    from rembg import new_session

    session = new_session()
    print("✓ rembg model downloaded successfully")
    print(f"  Location: {os.path.expanduser('~/.u2net/')}")
except ImportError:
    print("  WARNING: rembg is not installed. Skipping...")
    print("  Install with: python -m pip install rembg")
except Exception as e:
    print(f"  WARNING: Failed to download rembg model: {e}")

# 2. Check flux2-klein model
print("\n[2/2] Checking flux2-klein model...")
flux_model_path = "./flux2-klein/FLUX.2-klein-4B"
if os.path.exists(flux_model_path):
    print(f"✓ flux2-klein model found at: {flux_model_path}")
else:
    print(f"  WARNING: flux2-klein model not found at: {flux_model_path}")
    print("  Please ensure the model is available before building Docker image")

print("\n" + "=" * 60)
print("Model pre-download completed!")
print("=" * 60)

