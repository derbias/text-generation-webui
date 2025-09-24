import math

from modules import shared


def detect_vram_gb() -> float:
    try:
        import torch
        if torch.cuda.is_available():
            return round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
    except Exception:
        pass
    return 0.0


def suggest_gpu_layers(model_name: str, current_layers: int, ctx_size: int) -> int:
    vram = detect_vram_gb()
    # Very rough heuristic: scale layers by available VRAM and ctx size
    if vram <= 0:
        return current_layers
    scale = min(1.0, max(0.1, (vram - 2.0) / 20.0))  # leave ~2GB headroom
    base = max(0, int(current_layers * scale))
    # adjust slightly for very large ctx
    if ctx_size > 8192:
        base = max(0, int(base * 0.9))
    return base


