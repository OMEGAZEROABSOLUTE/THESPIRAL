# Documentation Index

The `docs` directory contains reference material for Spiral OS.

Milestone VIII expands on the sovereign voice work with memory-aided routing and
a new session logger. See [milestone_viii_plan.md](milestone_viii_plan.md) for
the design and [../README_OPERATOR.md](../README_OPERATOR.md) for updated
commands including the avatar and creative consoles. The OS Guardian policy
format is detailed in [os_guardian.md](os_guardian.md).

- [ALBEDO_LAYER.md](ALBEDO_LAYER.md)
- [CORPUS_MEMORY.md](CORPUS_MEMORY.md)
- [CROWN_OVERVIEW.md](CROWN_OVERVIEW.md)
- [DASHBOARD.md](DASHBOARD.md)
- [ETHICS_VALIDATION.md](ETHICS_VALIDATION.md)
- [INANNA_CORE.md](INANNA_CORE.md)
- [JSON_STRUCTURES.md](JSON_STRUCTURES.md)
- [LLM_FRAMEWORKS.md](LLM_FRAMEWORKS.md)
- [LLM_MODELS.md](LLM_MODELS.md)
- [SOUL_CODE.md](SOUL_CODE.md)
- [VAST_DEPLOYMENT.md](VAST_DEPLOYMENT.md)
- [archetype_logic.md](archetype_logic.md)
- [audio_ingestion.md](audio_ingestion.md)
- [avatar_ethics.md](avatar_ethics.md)
- [avatar_pipeline.md](avatar_pipeline.md)
- [cloud_deployment.md](cloud_deployment.md)
- [os_guardian.md](os_guardian.md)
- [os_guardian_container.md](os_guardian_container.md)
- [os_guardian_planning.md](os_guardian_planning.md)
- [os_guardian_permissions.md](os_guardian_permissions.md)
- [crown_manifest.md](crown_manifest.md)
- [deployment_overview.md](deployment_overview.md)
- [design.md](design.md)
- [emotional_memory_matrix.md](emotional_memory_matrix.md)
- [how_to_use.md](how_to_use.md)
- [milestone_viii_plan.md](milestone_viii_plan.md)
- [ml_environment.md](ml_environment.md)
- [project_overview.md](project_overview.md)
- [psychic_loop.md](psychic_loop.md)
- [rag_music_oracle.md](rag_music_oracle.md)
- [rag_pipeline.md](rag_pipeline.md)
- [scripts/ingest_sacred_inputs.sh](../scripts/ingest_sacred_inputs.sh)
- [ritual_manifesto.md](ritual_manifesto.md)
- [root_chakra_overview.md](root_chakra_overview.md)
- [sonic_core_harmonics.md](sonic_core_harmonics.md)
- [voice_aura.md](voice_aura.md)
- [../start_avatar_console.sh](../start_avatar_console.sh)
- [spiral_cortex_terminal.md](spiral_cortex_terminal.md)
- [spiritual_architecture.md](spiritual_architecture.md)

Recent updates add tests for the fallback text-to-speech helper and verify connectivity to the GLM service during initialization.
The startup script `start_crown_console.sh` now checks for Docker, `nc`, `sox`
and `ffmpeg` via `scripts/check_prereqs.sh` before launching. Use
`scripts/stop_crown_console.sh` to terminate all processes when shutting down.
