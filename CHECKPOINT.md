# Checkpoint - 2026-02-13

This file marks a pause point for the current build.

## Current status

Implemented and validated:

- Ruleset-agnostic RPG simulation core
- Multi-run campaign risk/pitfall analysis for DM prep
- Episode export artifacts
  - `episode_package.json`
  - `tts_script.txt`
  - `image_prompts.txt`
- Media rendering adapters
  - TTS: OpenAI, ElevenLabs
  - Images: OpenAI
- Video assembly pipeline (ffmpeg)
  - scene clips + concat into MP4
  - clear diagnostics when assets/tools are missing

## Key run commands

Simulation + analysis:

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 30
```

Export episode assets:

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 3 --export-episodes --export-dir outputs
```

Render media (requires keys):

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 1 --export-episodes --render-media --tts-provider openai --image-provider openai --export-dir outputs
```

Assemble video (requires rendered scene media + ffmpeg):

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 1 --export-episodes --render-media --assemble-video --export-dir outputs
```

## Pending design decisions

- Primary RPG ruleset choice
- Campaign setting and source corpus
- Canon policy for lore conflicts
- Preferred AI style profile (gritty, heroic, comedic, etc.)
- Success criteria for DM prep scoring

## Suggested next resume step

1. Lock one target ruleset and one campaign source bundle.
2. Implement a dedicated rules engine adapter for that system.
3. Add campaign-specific pitfall metrics and pass/fail thresholds.

## Dashboard notes saved for next session

- Added class-aware party panel data to dashboard JSON generation in `src/rpg_sim/dashboard.py` under `panels.party.members`.
- Current party panel member fields: `name`, `level` (nullable), `class`, `role`, `hp`, `status`.
- Next dashboard expansion candidates requested: DM telemetry, encounter actor timelines, and quest progression over weekly sessions.
