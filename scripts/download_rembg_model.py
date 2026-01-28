"""Pre-download rembg model for Docker image building."""

import os
import sys

try:
    from rembg import new_session

    print("Downloading rembg model (u2net)...")
    # This will download the model to ~/.u2net/ or $HOME/.u2net/
    session = new_session()
    print("✓ rembg model downloaded successfully")
    print(f"Model location: {os.path.expanduser('~/.u2net/')}")
except ImportError:
    print("ERROR: rembg is not installed. Please install it first:")
    print("  python -m pip install rembg")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed to download rembg model: {e}")
    sys.exit(1)

