import json
import threading
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.logging_colors import logger


REGISTRY_PATH = Path('user_data/cache/registry.json')
_lock = threading.Lock()


@dataclass
class InstalledVariant:
    path: str
    loader: Optional[str] = None
    quantization: Optional[str] = None
    dtype: Optional[str] = None
    sha: Optional[str] = None
    files: List[str] = field(default_factory=list)
    size_bytes: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class RegistryModel:
    model_id: str
    installed_variants: List[InstalledVariant] = field(default_factory=list)
    last_seen_card_etag: Optional[str] = None
    last_update_at: Optional[str] = None
    stats: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    pipelines: List[str] = field(default_factory=list)
    preferred_loader: Optional[str] = None
    favorite: bool = False


def _ensure_dir():
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load() -> Dict[str, Any]:
    _ensure_dir()
    if not REGISTRY_PATH.exists():
        return {"version": 1, "models": {}, "updated_at": None}
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
    except Exception:
        logger.warning("Model registry file is corrupt; recreating")
        return {"version": 1, "models": {}, "updated_at": None}


def _save(registry: Dict[str, Any]) -> None:
    _ensure_dir()
    tmp = REGISTRY_PATH.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(REGISTRY_PATH)


def upsert_model_card(model_id: str, card: Dict[str, Any]) -> None:
    with _lock:
        reg = _load()
        models = reg.setdefault('models', {})
        entry = models.get(model_id) or RegistryModel(model_id=model_id)
        if isinstance(entry, dict):
            entry = RegistryModel(**entry)
        # Basic hydration from card
        entry.pipelines = list({card.get('pipeline_tag')} - {None}) or entry.pipelines
        entry.tags = list(sorted(set((entry.tags or []) + (card.get('tags') or []))))
        models[model_id] = asdict(entry)
        _save(reg)


def record_install(model_id: str, variant: InstalledVariant) -> None:
    with _lock:
        reg = _load()
        models = reg.setdefault('models', {})
        entry = models.get(model_id) or RegistryModel(model_id=model_id)
        if isinstance(entry, dict):
            entry = RegistryModel(**entry)
        entry.installed_variants.append(variant)
        models[model_id] = asdict(entry)
        _save(reg)


def list_installed(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    reg = _load()
    out = []
    for model_id, entry in (reg.get('models') or {}).items():
        if isinstance(entry, RegistryModel):
            entry = asdict(entry)
        for var in entry.get('installed_variants', []) or []:
            rec = {"model_id": model_id, **var}
            out.append(rec)
    # TODO: apply filters in future
    return out


def mark_favorite(model_id: str, favorite: bool) -> None:
    with _lock:
        reg = _load()
        models = reg.setdefault('models', {})
        entry = models.get(model_id) or RegistryModel(model_id=model_id)
        if isinstance(entry, dict):
            entry = RegistryModel(**entry)
        entry.favorite = favorite
        models[model_id] = asdict(entry)
        _save(reg)


def get_registry_snapshot() -> Dict[str, Any]:
    return _load()

