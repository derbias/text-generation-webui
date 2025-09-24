### Enhanced Model Browser & Detail UI - Specification (Phase 1-2)

Tabs
- Browse: Hub discovery with filters, multi-pipeline selector, search, sort.
- Installed: Local models from registry + `utils.get_available_models()` for backward-compat.
- Collections & Favorites: simple tags and favorite toggle.

Browse Grid Item
- Title, pipeline, downloads, likes, license, tags, quick actions: View, Download, Add to Favorites.

Detail View
- Rich model card (size, parameters, architectures, datasets, evals, license), usage snippets, recommended loader, compatibility report, sample outputs placeholder.

Interactions
- Preflight: run compatibility analysis; show suggested loader and settings.
- One-Click Load: download if needed, then load with suggested loader.

Endpoints (backed by FastAPI on Gradio app)
- GET /api/models/search?q&pipelines&filters&limit
- GET /api/models/{model_id}/card
- POST /api/models/{model_id}/favorite

Performance
- Debounced search; incremental rendering; cached responses.

Accessibility
- Keyboard navigation, focus order, contrasts consistent with current theme.

