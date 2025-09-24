### Model Registry & Caching - Specification (Phase 3)

Goals
- Local registry to track discovered and installed models, versions, files, loaders, quantization, and metadata snapshots.
- Provide caching for Hub queries and model cards; track updates and notify.
- Expose APIs for version comparison and rollback metadata (files remain managed by existing download flows initially).

Storage
- Location: `user_data/cache/registry.json` (JSON; possible sqlite in future).
- Schema (top-level keys): version, updated_at, models: { model_id: RegistryModel }.
- RegistryModel: { model_id, installed_variants[], last_seen_card_etag?, last_update_at, stats: { uses, last_used_at, avg_load_ms? }, tags[], pipelines[], preferred_loader?, favorite? }
- InstalledVariant: { path, loader, quantization, dtype, sha?, files[], size_bytes?, created_at }

APIs
- upsert_model_card(model_card: ModelCard) -> None
- record_install(model_id, variant: InstalledVariant) -> None
- list_installed(filters) -> list[InstalledVariant]
- mark_favorite(model_id, favorite: bool) -> None
- get_update_status(model_id) -> { has_update, current_rev, remote_rev }

Events
- Emit basic callbacks (Python) when registry changes for UI refresh hooks.

Concurrency & Safety
- File lock during write; atomic tmp write + rename.

Out-of-scope (Phase 3)
- Moving/renaming model files; integrate later with existing downloader.

