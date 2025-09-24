import torch
import subprocess
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from time import time
from huggingface_hub import HfApi, ModelFilter
from modules.logging_colors import logger

def get_system_info():
    system_info = {
        "gpu_type": "AMD", # Assuming AMD based on user's choice
        "vram_gb": 0,
        "rocm_version": "Unknown"
    }

    try:
        # Get ROCm version
        rocm_smi_output = subprocess.run(['rocm-smi', '--version'], capture_output=True, text=True, check=True)
        match = re.search(r'ROCm Version:\s*(\d+\.\d+\.\d+)', rocm_smi_output.stdout)
        if match:
            system_info["rocm_version"] = match.group(1)

        # Get VRAM
        rocm_smi_output = subprocess.run(['rocm-smi', '--showmeminfo', 'vram', '--json'], capture_output=True, text=True, check=True)
        vram_data = json.loads(rocm_smi_output.stdout)
        # Assuming a single GPU for simplicity, or taking the first one
        if 'card' in vram_data and len(vram_data['card']) > 0:
            # VRAM is usually reported in MB, convert to GB
            total_vram_mb = vram_data['card'][0]['VRAM Total']
            system_info["vram_gb"] = round(total_vram_mb / 1024, 2)

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not get detailed AMD GPU info using rocm-smi: {e}")
        # Fallback to PyTorch if rocm-smi fails
        if torch.cuda.is_available(): # PyTorch uses 'cuda' for AMD GPUs with ROCm backend
            try:
                system_info["vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
                # PyTorch doesn't expose ROCm version easily, so keep as Unknown if rocm-smi failed
            except Exception as e:
                logger.warning(f"Could not get VRAM info from PyTorch: {e}")

    logger.info(f"Detected System Info: {system_info}")
    return system_info

def estimate_model_compatibility(model_info, system_info):
    # Heuristic for estimating VRAM usage and compatibility
    # Returns (is_compatible, estimated_vram_gb, recommended_loader)

    model_id = model_info.modelId
    tags = model_info.tags if model_info.tags else []
    estimated_vram_gb = 0
    recommended_loader = "Unknown"

    # Default VRAM per billion parameters for different quantization levels (rough estimates)
    # These values can vary significantly based on model architecture and loader implementation
    VRAM_PER_BILLION_PARAMS_FP16 = 2.0 # GB
    VRAM_PER_BILLION_PARAMS_Q8 = 1.0 # GB (for GGUF Q8)
    VRAM_PER_BILLION_PARAMS_Q4 = 0.6 # GB (for GGUF Q4 or Transformers 4-bit)

    # Try to get model parameters from model_info.cardData or tags
    model_params_billion = 0
    if model_info.cardData and 'model_size' in model_info.cardData:
        size_str = model_info.cardData['model_size'].lower()
        match = re.search(r'(\d+\.?\d*)[bB]', size_str)
        if match:
            model_params_billion = float(match.group(1))
    elif 'parameters' in tags:
        for tag in tags:
            match = re.search(r'(\d+\.?\d*)[bB]', tag)
            if match:
                model_params_billion = float(match.group(1))
                break

    if model_params_billion == 0:
        # Fallback: if parameters not found, try to estimate from total_size if available
        if model_info.safetensors and model_info.safetensors.get('total_size'):
            total_size_gb = model_info.safetensors['total_size'] / (1024**3)
            # Rough estimate: 1B params ~ 2GB in FP16
            model_params_billion = total_size_gb / VRAM_PER_BILLION_PARAMS_FP16

    if model_params_billion == 0:
        return False, 0, "Unknown" # Cannot estimate compatibility without model size

    # Heuristics based on model type and quantization
    if "gguf" in tags or "GGUF" in model_id:
        recommended_loader = "llama.cpp"
        # Try to detect quantization from model_id
        if re.search(r'Q(8|6|5)_K_M', model_id):
            estimated_vram_gb = model_params_billion * VRAM_PER_BILLION_PARAMS_Q8
        elif re.search(r'Q(4|3|2)_K_M', model_id):
            estimated_vram_gb = model_params_billion * VRAM_PER_BILLION_PARAMS_Q4
        else:
            # Assume Q4 if not specified for GGUF
            estimated_vram_gb = model_params_billion * VRAM_PER_BILLION_PARAMS_Q4

    elif "exl2" in tags or "ExLlamaV2" in model_id:
        recommended_loader = "ExLlamaV2"
        # ExLlamaV2 is highly optimized, assume similar to GGUF Q4 for VRAM
        estimated_vram_gb = model_params_billion * VRAM_PER_BILLION_PARAMS_Q4

    elif "safetensors" in tags or "pytorch" in tags:
        recommended_loader = "Transformers"
        # Assume 4-bit quantization for Transformers models on AMD to be compatible
        estimated_vram_gb = model_params_billion * VRAM_PER_BILLION_PARAMS_Q4

    else:
        # For other types, assume FP16 if no quantization info
        estimated_vram_gb = model_params_billion * VRAM_PER_BILLION_PARAMS_FP16

    # Add a buffer for overhead
    required_vram_gb = estimated_vram_gb * 1.2

    is_compatible = system_info["vram_gb"] >= required_vram_gb
    return is_compatible, required_vram_gb, recommended_loader

def find_compatible_models():
    system_info = get_system_info()
    hf_api = HfApi()
    compatible_models_list = []

    # Search for text-generation models
    # This can be slow and might need pagination or more specific filtering
    # Increased limit for better results
    models = hf_api.list_models(
        pipeline_tag="text-generation",
        sort="downloads",
        direction=-1, # Most downloaded first
        limit=200 # Limit to top 200 for now
    )

    for model in models:
        is_compatible, required_vram, loader = estimate_model_compatibility(model, system_info)
        if is_compatible:
            compatible_models_list.append({
                "model_id": model.modelId,
                "required_vram": f"{required_vram:.2f} GB",
                "recommended_loader": loader
            })

    if compatible_models_list:
        output = f"### Compatible Models Found (Estimated VRAM for your {system_info['gpu_type']} with {system_info['vram_gb']} GB VRAM):\n\n"
        for m in compatible_models_list:
            output += f"- **{m['model_id']}** (Estimated VRAM: {m['required_vram']}, Recommended Loader: {m['recommended_loader']})\n"
        return output
    else:
        return f"No compatible models found based on current heuristics for your {system_info['gpu_type']} with {system_info['vram_gb']} GB VRAM."


# ---------------------------------------------
# Enhanced multi-pipeline discovery with caching
# ---------------------------------------------

_DISCOVERY_CACHE: Dict[str, Tuple[float, Any]] = {}
_DEFAULT_TTL_SECONDS = 900


def _make_cache_key(
    pipelines: Optional[List[str]],
    query: Optional[str],
    limit: int,
    filters: Optional[Dict[str, Any]],
    include_meta: bool
) -> str:
    return str((tuple(sorted(pipelines or [])), query or '', limit, tuple(sorted((filters or {}).items())), include_meta))


def _get_from_cache(key: str, ttl_seconds: int) -> Optional[Any]:
    entry = _DISCOVERY_CACHE.get(key)
    if not entry:
        return None
    ts, data = entry
    if time() - ts <= ttl_seconds:
        return data
    try:
        del _DISCOVERY_CACHE[key]
    except Exception:
        pass
    return None


def _set_cache(key: str, data: Any) -> None:
    _DISCOVERY_CACHE[key] = (time(), data)


def clear_discovery_cache() -> None:
    _DISCOVERY_CACHE.clear()


def _extract_model_metadata(mi) -> Dict[str, Any]:
    # Safely extract known fields; fall back to None if missing
    meta = {
        'model_id': getattr(mi, 'modelId', None),
        'sha': getattr(mi, 'sha', None),
        'pipeline_tag': getattr(mi, 'pipeline_tag', None),
        'private': getattr(mi, 'private', None),
        'gated': getattr(mi, 'gated', None),
        'likes': getattr(mi, 'likes', None),
        'downloads': getattr(mi, 'downloads', None),
        'tags': getattr(mi, 'tags', None),
        'last_modified': getattr(mi, 'lastModified', None),
        'siblings': [s.rfilename for s in getattr(mi, 'siblings', [])] if getattr(mi, 'siblings', None) else None,
    }

    card = getattr(mi, 'cardData', None) or {}
    meta.update({
        'license': card.get('license') if isinstance(card, dict) else None,
        'datasets': card.get('datasets') if isinstance(card, dict) else None,
        'model_size': card.get('model_size') if isinstance(card, dict) else None,
        'architecture': card.get('model_architecture') or card.get('architecture') if isinstance(card, dict) else None,
        'language': card.get('language') if isinstance(card, dict) else None,
        'library_name': getattr(mi, 'library_name', None),
        'library_version': getattr(mi, 'library_version', None),
        'inference': card.get('inference') if isinstance(card, dict) else None,
        'training': card.get('training') if isinstance(card, dict) else None,
        'metrics': card.get('metrics') if isinstance(card, dict) else None,
        'example_inputs': card.get('example_input') or card.get('example_inputs') if isinstance(card, dict) else None,
        'example_outputs': card.get('example_output') or card.get('example_outputs') if isinstance(card, dict) else None,
    })

    # Roughly infer params if present
    params_b = None
    size_str = None
    try:
        size_str = (card.get('model_size') or '').lower() if isinstance(card, dict) else None
    except Exception:
        pass
    if size_str:
        m = re.search(r'(\d+\.?\d*)\s*[bB]', size_str)
        if m:
            try:
                params_b = float(m.group(1))
            except Exception:
                params_b = None
    if params_b is None and getattr(mi, 'safetensors', None) and isinstance(mi.safetensors, dict) and mi.safetensors.get('total_size'):
        total_size_gb = mi.safetensors['total_size'] / (1024 ** 3)
        params_b = total_size_gb / 2.0
    meta['parameters_b'] = params_b
    return meta


def discover_models(
    pipelines: Optional[List[str]] = None,
    query: Optional[str] = None,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
    include_meta: bool = True,
    ttl_seconds: int = _DEFAULT_TTL_SECONDS
) -> Dict[str, Any]:
    """
    Discover models across multiple pipelines with optional filters and metadata.
    Returns a dict with keys: items (list), total (int), pipelines (list)
    """
    api = HfApi()
    pipelines = pipelines or [
        'text-generation',
        'text2text-generation',
        'image-text-to-text',
        'text-to-image',
        'audio-to-audio',
        'automatic-speech-recognition'
    ]
    filters = filters or {}

    key = _make_cache_key(pipelines, query, limit, filters, include_meta)
    cached = _get_from_cache(key, ttl_seconds)
    if cached is not None:
        return cached

    all_items: List[Dict[str, Any]] = []
    for ptag in pipelines:
        try:
            model_filter = ModelFilter(
                task=ptag,
                tags=filters.get('tags') if filters else None,
                library=filters.get('library') if filters else None,
                dataset=filters.get('dataset') if filters else None,
                language=filters.get('language') if filters else None,
            )
        except Exception:
            model_filter = None

        try:
            results = api.list_models(
                filter=model_filter,
                search=query,
                sort=filters.get('sort') if filters else 'downloads',
                direction=filters.get('direction') if filters else -1,
                limit=limit
            )
        except Exception as e:
            logger.warning(f"HF discovery failed for pipeline {ptag}: {e}")
            results = []

        for mi in results:
            item = {
                'model_id': getattr(mi, 'modelId', None),
                'pipeline_tag': getattr(mi, 'pipeline_tag', ptag),
            }
            if include_meta:
                item.update(_extract_model_metadata(mi))
            all_items.append(item)

    payload = {
        'items': all_items,
        'total': len(all_items),
        'pipelines': pipelines,
    }
    _set_cache(key, payload)
    return payload
