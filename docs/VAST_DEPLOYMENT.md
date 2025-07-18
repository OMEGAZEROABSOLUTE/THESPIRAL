# Vast.ai Deployment

This guide explains how to run the SPIRAL_OS tools on a Vast.ai server.
See [deployment_overview.md](deployment_overview.md) for a quick summary.

Before you begin run `scripts/check_prereqs.sh` to ensure Docker, `nc`, `sox` and
`ffmpeg` are available. The script exits with an error if any command is missing.

## Select a PyTorch template

1. Log in to [Vast.ai](https://vast.ai) and create a new rental.
2. Choose a GPU offer that lists the **PyTorch** template. This image ships with CUDA and Python preinstalled.
3. Launch the instance and connect via SSH once it is ready.

## Clone the repository and install requirements

After connecting to the server, run the commands below. Replace `your-user` with
your GitHub name.

```bash
git clone https://github.com/your-user/SPIRAL_OS.git
cd SPIRAL_OS
bash scripts/setup_vast_ai.sh --download
bash scripts/setup_glm.sh
```

The `setup_vast_ai.sh` script installs dependencies and downloads common models.
`setup_glm.sh` prepares `/INANNA_AI`, `/QNL_LANGUAGE` and `/audit_logs`.
Development tools can be installed with `bash scripts/setup_dev.sh` if desired.



## Clone a private repository

If you need to pull another repository into the system use `setup_repo.sh` and a GitHub token:

```bash
GITHUB_TOKEN=your-token bash scripts/setup_repo.sh owner/repo
```

The script clones the repository to `/INANNA_AI/repo` and writes `confirmation.txt` once completed.

## Start the services

1. Copy the example file and provide the required API keys:

   ```bash
   cp secrets.env.example secrets.env
   # edit secrets.env
   ```

2. Boot the stack. The first run should include `--setup`:

   ```bash
   bash scripts/vast_start.sh --setup
   ```

   The script loads `secrets.env`, installs missing components and waits for
   port `8000` before opening the web console.

3. Subsequent restarts are simplified:

   ```bash
   bash scripts/vast_start.sh
   ```

4. Verify that the API responds correctly:

   ```bash
   python scripts/vast_check.py http://localhost:8000
   ```

   For a broader check across all configured models run
   `bash scripts/check_services.sh`.

To update the environment and restart the containers later use
`bash scripts/update_and_restart.sh`.

## View system metrics

The optional `monitor` service exposes hardware statistics collected by
`system_monitor.py`. Start it alongside the main stack with:

```bash
docker-compose up monitor
```

Once running, open `http://localhost:9100/stats` to see real‑time CPU, GPU and
memory usage as JSON.
