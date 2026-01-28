
# 依赖安装
conda create -n ootd python==3.11
python -m pip install -U "git+https://github.com/huggingface/diffusers.git"
python -m pip install -U transformers accelerate safetensors
python -m pip install torch torchvision torchaudio   --index-url https://download.pytorch.org/whl/cu121

# FastAPI 相关依赖
python -m pip install fastapi "pydantic<3" uvicorn requests pillow httpx

# 去背景依赖
python -m pip install rembg

# 预下载 rembg 模型（用于 Docker 打包）
# 模型会下载到 ~/.u2net/ 目录
python scripts/download_rembg_model.py
# 或下载所有模型（rembg + 检查 flux2-klein）
python scripts/download_all_models.py

# 架构说明
本项目分为三个模块：

## 1. API 服务（业务逻辑层）
- 位置：`main.py`
- 职责：接收 Web 端请求、参数校验、提示词生成、任务管理、图片去背景处理、调用推理服务
- 启动：`python -m uvicorn main:app --reload --port 8000`

## 2. 推理服务（纯推理层）
- 位置：`inference_service/main.py`
- 职责：模型加载、执行推理、返回结果
- 启动：`python -m uvicorn inference_service.main:app --reload --port 8001`
- 或：`python inference_service/main.py`（默认端口 8001）

## 3. 去背景服务（可选独立服务，也可作为库使用）
- 位置：`background_removal_service/`
- 职责：图片去背景处理
- **作为库使用**：API 服务直接导入调用（不走 HTTP，内部服务调用）
- **作为独立服务**（可选）：`python -m uvicorn background_removal_service.main:app --reload --port 8002`
- 或：`python background_removal_service/main.py`（默认端口 8002）

## 环境变量
- `INFERENCE_SERVICE_URL`: 推理服务地址（默认：http://localhost:8001）
- `INFERENCE_PORT`: 推理服务端口（默认：8001）
- `BG_REMOVAL_PORT`: 去背景服务端口（默认：8002，仅当作为独立服务时使用）

## 启动顺序
1. 先启动推理服务（端口 8001）
2. 再启动 API 服务（端口 8000）
3. API 服务会自动调用推理服务进行推理
4. API 服务内部调用去背景服务（不走 HTTP，直接导入函数调用）

## 图片去背景说明
- 每个图片字段都有对应的 `*_bg_removed` 参数（默认为 `false`）
- 如果 `*_bg_removed=false`，API 服务会自动调用去背景服务处理图片
- 如果 `*_bg_removed=true`，API 服务会直接使用原图（假设已经去背景）
- 去背景处理在 `_process_task` 中完成，是内部服务调用，不走 HTTP

## Docker 打包说明

### 模型预下载
在构建 Docker 镜像前，建议预先下载所有模型：

```bash
# 预下载 rembg 模型（会下载到 ~/.u2net/）
python scripts/download_rembg_model.py

# 或下载所有模型并检查
python scripts/download_all_models.py
```

### Docker 构建
参考 `Dockerfile.example` 创建你的 Dockerfile：

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# 预下载 rembg 模型（构建时下载，避免运行时下载）
RUN python -c "from rembg import new_session; new_session()"
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 模型存储位置
- **rembg 模型**：默认存储在 `~/.u2net/` 或 `$HOME/.u2net/`
- **flux2-klein 模型**：需要放在 `./flux2-klein/FLUX.2-klein-4B/` 目录

### Docker Compose
参考 `docker-compose.example.yml` 配置多服务部署。