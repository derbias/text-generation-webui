import gradio as gr

from modules import extensions as extensions_module
from modules import shared
from modules.logging_colors import logger


def _collect_extension_status():
    statuses = []
    for name in sorted(extensions_module.state.keys()):
        info = extensions_module.state.get(name)
        if not info:
            continue
        enabled, _, module_obj = info
        ver = getattr(module_obj, "__version__", "") if module_obj else ""
        line = f"- {name} : {'enabled' if enabled else 'disabled'}"
        if ver:
            line += f" ({ver})"
        statuses.append(line)
    if not statuses:
        statuses.append("- No extensions loaded")
    return "\n".join(statuses)


def _collect_logs(limit: int = 100):
    buf = getattr(logger, 'buffer', [])
    if not buf:
        return "No logs collected yet."
    return "\n".join(buf[-limit:])


def _render_system_report():
    model = shared.model_name
    loader = shared.args.loader
    ext_status = _collect_extension_status()
    logs = _collect_logs()
    sections = []
    sections.append(
        "### System\n\n- Model: {}\n- Loader: {}".format(model, loader)
    )
    sections.append("### Extensions\n{}".format(ext_status))
    sections.append("### Recent logs\n```\n{}\n```".format(logs))
    return "\n\n".join(sections)


def create_ui():
    with gr.Tab("System", elem_id="system-tab"):
        with gr.Row():
            with gr.Column():
                shared.gradio['system_refresh'] = gr.Button('Refresh', elem_classes='refresh-button')
                shared.gradio['system_report'] = gr.Markdown(_render_system_report())


def create_event_handlers():
    shared.gradio['system_refresh'].click(
        _render_system_report,
        None,
        shared.gradio['system_report']
    )

