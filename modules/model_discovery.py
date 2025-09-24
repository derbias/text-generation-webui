from typing import Any, Dict, List, Optional

from modules.logging_colors import logger

try:
    from huggingface_hub import HfApi
except Exception:
    HfApi = None


SUPPORTED_PIPELINES = [
    'text-generation',
    'text2text-generation',
    'image-text-to-text',
    'text-to-image',
    'audio-to-audio',
    'automatic-speech-recognition',
]


def discover_models(query: Optional[str] = None,
                    pipelines: Optional[List[str]] = None,
                    filters: Optional[Dict[str, Any]] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
    if HfApi is None:
        logger.warning('huggingface_hub not available; discovery disabled')
        return []
    api = HfApi()
    pipelines = pipelines or ['text-generation']
    results: List[Dict[str, Any]] = []
    for pipeline_tag in pipelines:
        try:
            models = api.list_models(
                search=query or None,
                pipeline_tag=pipeline_tag,
                sort='downloads',
                direction=-1,
                limit=limit,
            )
            for m in models:
                results.append({
                    'model_id': m.modelId,
                    'pipeline_tag': getattr(m, 'pipeline_tag', pipeline_tag),
                    'downloads': getattr(m, 'downloads', None),
                    'likes': getattr(m, 'likes', None),
                    'tags': getattr(m, 'tags', None),
                    'license': getattr(m, 'license', None),
                    'last_modified': getattr(m, 'lastModified', None),
                })
        except Exception as e:
            logger.warning(f'Failed discovery for pipeline {pipeline_tag}: {e}')
    return results


def get_model_card(model_id: str) -> Dict[str, Any]:
    if HfApi is None:
        return {}
    api = HfApi()
    try:
        card = api.model_info(model_id)
        data = card.__dict__.copy()
        # Normalize keys of interest
        return {
            'model_id': model_id,
            'pipeline_tag': getattr(card, 'pipeline_tag', None),
            'tags': getattr(card, 'tags', None),
            'license': getattr(card, 'license', None),
            'sha': getattr(card, 'sha', None),
            'safetensors': getattr(card, 'safetensors', None),
            'cardData': getattr(card, 'cardData', None),
        }
    except Exception as e:
        logger.warning(f'Failed to fetch model card for {model_id}: {e}')
        return {}


def estimate_compatibility(model_id: str, system_info: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder heuristic; integrate with existing GPU layer advisor
    try:
        return {
            'is_compatible': True,
            'recommended_loader': 'Transformers',
            'reasons': [],
        }
    except Exception:
        return {'is_compatible': False, 'recommended_loader': None, 'reasons': ['internal error']}

