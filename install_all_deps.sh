#!/usr/bin/env bash

# This script manually installs all dependencies for text-generation-webui (AMD Linux).
# It should be run after the conda environment has been created and activated.

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Installing core dependencies..."

# Core dependencies from requirements_amd.txt
$(pwd)/installer_files/env/bin/python -m pip install accelerate==1.8.*
$(pwd)/installer_files/env/bin/python -m pip install colorama
$(pwd)/installer_files/env/bin/python -m pip install datasets
$(pwd)/installer_files/env/bin/python -m pip install einops
$(pwd)/installer_files/env/bin/python -m pip install fastapi==0.112.4
$(pwd)/installer_files/env/bin/python -m pip install gradio==4.37.*
$(pwd)/installer_files/env/bin/python -m pip install html2text==2025.4.15
$(pwd)/installer_files/env/bin/python -m pip install huggingface_hub>=0.11.0
$(pwd)/installer_files/env/bin/python -m pip install jinja2==3.1.6
$(pwd)/installer_files/env/bin/python -m pip install markdown
$(pwd)/installer_files/env/bin/python -m pip install numpy==2.2.*
$(pwd)/installer_files/env/bin/python -m pip install pandas
$(pwd)/installer_files/env/bin/python -m pip install peft==0.17.*
$(pwd)/installer_files/env/bin/python -m pip install Pillow>=9.5.0
$(pwd)/installer_files/env/bin/python -m pip install psutil
$(pwd)/installer_files/env/bin/python -m pip install pydantic==2.8.2
$(pwd)/installer_files/env/bin/python -m pip install PyPDF2==3.0.1
$(pwd)/installer_files/env/bin/python -m pip install python-docx==1.1.2
$(pwd)/installer_files/env/bin/python -m pip install pyyaml
$(pwd)/installer_files/env/bin/python -m pip install requests
$(pwd)/installer_files/env/bin/python -m pip install rich
$(pwd)/installer_files/env/bin/python -m pip install safetensors==0.6.*
$(pwd)/installer_files/env/bin/python -m pip install scipy
$(pwd)/installer_files/env/bin/python -m pip install sentencepiece
$(pwd)/installer_files/env/bin/python -m pip install tensorboard
$(pwd)/installer_files/env/bin/python -m pip install transformers==4.56.*
$(pwd)/installer_files/env/bin/python -m pip install tqdm
$(pwd)/installer_files/env/bin/python -m pip install wandb

echo "Installing API dependencies..."

# API dependencies
$(pwd)/installer_files/env/bin/python -m pip install flask_cloudflared==0.0.14
$(pwd)/installer_files/env/bin/python -m pip install sse-starlette==1.6.5
$(pwd)/installer_files/env/bin/python -m pip install tiktoken

echo "Installing AMD wheels..."

# AMD wheels (Linux x86_64, Python 3.11)
$(pwd)/installer_files/env/bin/python -m pip install https://github.com/oobabooga/llama-cpp-binaries/releases/download/v0.46.0/llama_cpp_binaries-0.46.0+vulkan-py3-none-linux_x86_64.whl
$(pwd)/installer_files/env/bin/python -m pip install https://github.com/turboderp-org/exllamav2/releases/download/v0.3.2/exllamav2-0.3.2+rocm6.2.4.torch2.6.0-cp311-cp311-linux_x86_64.whl

echo "All dependencies installed."
