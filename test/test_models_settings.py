from modules.models_settings import infer_loader


def test_infer_loader_prefers_llamacpp_for_gguf(tmp_path, monkeypatch):
    model_name = "some-model.Q4_K_M.gguf"
    state = {}
    loader = infer_loader(model_name, state, hf_quant_method=None)
    assert loader == 'llama.cpp'


def test_infer_loader_exllama_hf_for_exl2(tmp_path, monkeypatch):
    model_name = "user/repo-exl2"
    state = {}
    loader = infer_loader(model_name, state, hf_quant_method='exl2')
    assert loader in ['ExLlamav2_HF', 'ExLlamav2']


def test_infer_loader_transformers_default(tmp_path, monkeypatch):
    model_name = "user/repo"
    state = {}
    loader = infer_loader(model_name, state, hf_quant_method=None)
    assert loader in ['Transformers', 'llama.cpp', 'ExLlamav2_HF', 'ExLlamav3']

