## [Unreleased]

### Added
- OpenAI-compatible API: non-persistent API keys endpoints:
  - `GET /v1/internal/api-keys` (masked status only)
  - `POST /v1/internal/api-keys/validate` (no storage)
- Simple per-path metrics for OpenAI endpoints (middleware increments `requests_total` and `endpoint_counts`).
- System tab now shows "API keys configured: yes/no" (non-persistent).
- Public wrappers for internal calls:
  - `extensions/openai/logits.get_next_logits_public`
  - `extensions/openai/models.load_model_public`

### Changed
- OpenAI server bind: use a single host for uvicorn; still advertise all URLs.
- Extensive lazy-imports to avoid import-time failures and break circular imports.
- Linter cleanup: wrapped long lines, refined logging, safer exception chaining.
- Docs: recommended API startup command; audio transcription dependency note.

### Fixed
- Circular import involving token encode/decode (`extensions/openai/tokens.py`).
- CORS config guard when `cors_origin` is not present.

