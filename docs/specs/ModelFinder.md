### Enhanced Model Finder - Specification (Phase 1)

Goals
- Support multi-pipeline discovery beyond text-generation: text2text-generation, image-text-to-text, text-to-image, audio-to-audio, automatic-speech-recognition.
- Provide rich search and filtering against Hugging Face Hub metadata (license, downloads, likes, framework, quantization, size, tags, inference tasks).
- Return enriched model metadata for UI detail views and preflight checks.

APIs
- Registry-facing function signatures (Python):
  - discover_models(query: str, pipelines: list[str], filters: dict, limit: int) -> list[DiscoveredModel]
  - get_model_card(model_id: str) -> ModelCard
  - estimate_compatibility(model_id: str, system_info: dict) -> CompatibilityReport

Data Contracts
- DiscoveredModel: { model_id, pipeline_tag, repo_size_bytes?, downloads, likes, license, tags, frameworks, architectures, last_modified, card_data_min }
- ModelCard: { model_id, pipeline_tag, parameters?, layers?, architectures, datasets, training_details, evals, usage_examples, license, hardware_reqs }
- CompatibilityReport: { is_compatible, reasons[], recommended_loader, est_vram_gb?, dtype_hint?, quantization_options[] }

Filtering
- Text query (name/tags), pipeline_tag, license, framework (transformers, llama.cpp, TensorRT, exllama), quantization (gguf, gptq, awq, exl2/3), min/max params, downloads range, likes range.

Pagination
- Use Hub pagination; default limit 50; support cursor/offset for future.

Performance
- Cache: short-lived in-memory cache (60–300s) for list queries; persistent cache via Model Registry for model cards.
- Batched card fetches; avoid fetching full card for list.

Error Handling
- Gracefully degrade when HF API unavailable; return cached results if present.

Security
- Respect HF tokens from settings; do not log secrets.

Open Questions
- Extent of on-device benchmark integration in Phase 1 (likely out-of-scope, collect later).

