# Deployment Overview

This guide summarises how to launch Spiral OS on a Vast.ai server and how to run the stack locally with Docker Compose.

## Configure environment variables

Run `bash scripts/setup_local.sh` to copy `secrets.env.example` to `secrets.env` and provide values for the required tokens and ports:

- `HF_TOKEN` – Hugging Face token for downloading models
- `OPENAI_API_KEY` – optional OpenAI key
- `GLM_API_URL` / `GLM_API_KEY` – GLM service endpoint and key
- `GLM_SHELL_URL` / `GLM_SHELL_KEY` – shell service endpoint and key

See `secrets.env.example` for the full list.

## Download model weights

Before the first launch download the required models. For example:

```bash
python download_models.py deepseek_v3
```

Models are stored under `INANNA_AI/models`.

## Launch on Vast.ai

Follow the steps below to start Spiral OS on a Vast.ai instance.

1. Optionally verify that Docker and other tools are available:

   ```bash
   bash scripts/check_prereqs.sh
   ```

2. Boot the stack for the first time. The `--setup` flag installs packages
   and downloads any configured models:

   ```bash
   bash scripts/vast_start.sh --setup
   ```

   The script reads `secrets.env`, brings up the `INANNA_AI` container and
   waits for port `8000` before opening `web_console/index.html` in your
   browser.

3. Subsequent restarts require only:

   ```bash
   bash scripts/vast_start.sh
   ```

4. Check that the API endpoints respond correctly:

   ```bash
   python scripts/vast_check.py http://localhost:8000
   ```

   The checker polls `/health` and `/ready` and performs a dummy `/offer`
   exchange. It exits with a non‑zero status if any step fails.

To update the repository in place run `bash scripts/update_and_restart.sh`.

## Local Docker Compose

To test locally without Vast.ai simply run:

```bash
docker-compose up
```

The compose file builds the main `INANNA_AI` container and mounts `data`, `logs` and `INANNA_AI/models`. Optional `deepseek`, `mistral` and `kimi_k2` services are also defined. Each exposes its own port and expects a corresponding model directory:

```
INANNA_AI  -> 8000/8001  INANNA_AI/models
deepseek   -> 8002       INANNA_AI/models/DeepSeek-V3
mistral    -> 8003       INANNA_AI/models/Mistral-8x22B
kimi_k2    -> 8010       INANNA_AI/models/Kimi-K2
```

Run `docker-compose up` to start everything or specify a subset such as `docker-compose up INANNA_AI deepseek`. Once running, open `web_console/index.html` to issue commands through the FastAPI endpoint.

For details on browser permissions see
[how_to_use.md](how_to_use.md#connecting-via-webrtc).


