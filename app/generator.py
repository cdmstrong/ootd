"""Legacy generator module - kept for backward compatibility.

This module is deprecated. Use app.client.InferenceClient instead.
"""

from __future__ import annotations

from .client import InferenceClient

# For backward compatibility, export the client
__all__ = ["InferenceClient"]


