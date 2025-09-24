from functools import partial
from typing import List

import gradio as gr

from modules import shared
from modules.model_discovery import discover_models, SUPPORTED_PIPELINES
from modules.model_registry import get_registry_snapshot, mark_favorite
from modules.utils import gradio


def _search(query, pipelines, limit):
    try:
        pipelines = pipelines or ['text-generation']
        return {'results': discover_models(query, pipelines, None, limit)}
    except Exception as e:
        return {'results': [], 'error': str(e)}


def _toggle_fav(model_id, fav):
    try:
        mark_favorite(model_id, bool(fav))
        return f"Favorite set: {fav}"
    except Exception as e:
        return f"Error: {e}"


def create_ui():
    with gr.Tab("Browse", elem_id="model-browser-tab"):
        with gr.Row():
            with gr.Column(scale=1):
                q = gr.Textbox(label="Search", placeholder="Search models…")
                pipelines = gr.CheckboxGroup(SUPPORTED_PIPELINES, value=['text-generation'], label="Pipelines")
                limit = gr.Slider(10, 200, value=50, step=10, label="Limit")
                search_btn = gr.Button("Search")
                results = gr.JSON(label="Results", value={"results": []})
            with gr.Column(scale=1):
                gr.Markdown("Installed & Favorites")
                installed = gr.JSON(value=get_registry_snapshot, label="Registry Snapshot")
                fav_model = gr.Textbox(label="Model ID")
                fav_toggle = gr.Checkbox(label="Favorite", value=True)
                fav_btn = gr.Button("Apply Favorite")
                fav_status = gr.Markdown()

        search_btn.click(_search, [q, pipelines, limit], [results])
        fav_btn.click(_toggle_fav, [fav_model, fav_toggle], [fav_status]).then(lambda: get_registry_snapshot(), None, [installed])


def create_event_handlers():
    pass

