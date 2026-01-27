
# 依赖安装
conda create -n ootd python==3.11
python -m pip install -U "git+https://github.com/huggingface/diffusers.git"
python -m pip install -U transformers accelerate safetensors
python -m pip install torch torchvision torchaudio   --index-url https://download.pytorch.org/whl/cu121