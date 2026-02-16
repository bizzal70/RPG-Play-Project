# RPG-Play-Project

Fully automated RPG campaign test idea.

This repository now contains a ruleset-agnostic MVP framework for running automated RPG sessions. You can plug in your own campaign setting, rules, and AI models later.

It is also designed as a DM prep assistant: run many simulated sessions against the same source material to reveal brittle encounter pacing, dead-end progression, and high-failure branches.

## What this MVP does

- Runs a full session loop: scene setup → party action selection → rules resolution → state update → log output.
- Keeps outcomes deterministic when needed using a random seed.
- Supports multi-run simulation and pitfall summaries for prep analysis.
- Separates responsibilities into interchangeable modules:
	- `Ruleset`: resolves actions and outcomes.
	- `Director`: generates scene context and available options.
	- `Actor`: chooses actions for party members.

## Project structure

- `main.py` - CLI entrypoint.
- `src/rpg_sim/models.py` - core data structures.
- `src/rpg_sim/interfaces.py` - abstract interfaces.
- `src/rpg_sim/session.py` - session orchestration engine.
- `src/rpg_sim/analysis.py` - DM-focused risk/pitfall analysis.
- `src/rpg_sim/rules/generic.py` - sample generic d20-like ruleset.
- `src/rpg_sim/agents.py` - default heuristic actor + simple director.
- `src/rpg_sim/ai_agents.py` - AI DM wrapper + per-character policy actor.
- `data/campaign_template.json` - editable campaign seed data.

## Run

1. Create and activate a Python 3.11+ environment.
2. Run:

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7
```

Use merged D&D 5e 2024 SRD as active content source (auto-enabled if the default SRD file exists):

```bash
python main.py --campaign data/campaign_template.json --srd-json data/srd/srd_5e_2024_merged.json --use-srd --turns 8 --seed 7
```

Ingest an SRD PDF into chunked source JSON:

```bash
python scripts/ingest_pdf.py --pdf data/sources/pdf/SRD_CC_v5.2.1.pdf --out data/sources/srd_5e_2024_chunks.json --chunk-words 220 --chunk-overlap 40
```

Use source chunks in simulation prompts:

```bash
python main.py --campaign data/campaign_template.json --use-srd --srd-json data/srd/srd_5e_2024_merged.json --use-source-chunks --source-chunks-json data/sources/srd_5e_2024_chunks.json --turns 8 --seed 7
```

Generate a full adventuring party JSON:

```bash
python scripts/generate_party.py --out data/parties/generated_party.json --size 4 --seed 13 --srd-json data/srd/srd_5e_2024_merged.json
```

Generate per-character AI policy profile from your party:

```bash
python scripts/generate_policy_profile.py --party-json data/parties/party_cos_survival.json --out data/policies/character_policies.json --preset balanced
```

Archetype presets:

```bash
# Balanced default party
python scripts/generate_party.py --out data/parties/party_balanced.json --preset balanced --size 4 --seed 13

# Tougher survival-oriented composition
python scripts/generate_party.py --out data/parties/party_hardcore.json --preset hardcore --size 4 --seed 13

# Story-forward composition with social/arcane emphasis
python scripts/generate_party.py --out data/parties/party_story.json --preset story-heavy --size 4 --seed 13

# Curse of Strahd survival-leaning composition
python scripts/generate_party.py --out data/parties/party_cos_survival.json --preset cos-survival --size 4 --seed 13
```

Run with generated party override:

```bash
python main.py --campaign data/campaign_template.json --party-json data/parties/generated_party.json --source-profile cos --turns 8 --seed 7
```

Enable per-character policy actors (deterministic fallback, no API key required):

```bash
python main.py \
	--campaign data/campaign_cos.json \
	--source-profile cos \
	--party-json data/parties/party_cos_survival.json \
	--policy-actors \
	--ai-policy-json data/policies/character_policies.json \
	--turns 8 --seed 7
```

Enable true AI DM + true AI actors (requires OpenAI API key):

```bash
export OPENAI_API_KEY="your_api_key_here"
python main.py \
	--campaign data/campaign_cos.json \
	--source-profile cos \
	--party-json data/parties/party_cos_survival.json \
	--policy-actors \
	--ai-director \
	--ai-actors \
	--ai-model gpt-4o-mini \
	--turns 8 --seed 7
```

Shortcut profile for Curse of Strahd sources:

```bash
python main.py --campaign data/campaign_cos.json --source-profile cos --turns 8 --seed 7
```

Shortcut profile for Lost Mine of Phandelver sources:

```bash
python main.py --campaign data/campaign_lmop.json --source-profile lmop --turns 8 --seed 7
```

Profile-aware campaign seed behavior:

- If `--campaign data/campaign_template.json` is passed, the selected `--source-profile` may override it via `campaign_json` in `data/source_profiles.json`.
- This enables each imported campaign profile to carry its own default campaign seed while keeping a single stable CLI command.

Register any campaign PDF as a reusable source profile (one-time setup):

```bash
python scripts/register_campaign_source.py \
	--profile my_campaign \
	--pdf data/sources/pdf/My-Campaign.pdf \
	--chunks-out data/sources/my_campaign_chunks.json \
	--campaign-json data/campaign_template.json \
	--campaign-id my_campaign_weekly \
	--party-json data/parties/generated_party.json \
	--source-profiles-json data/source_profiles.json \
	--srd-json data/srd/srd_5e_2024_merged.json

# Generate campaign-specific AI tone/policy and bind to profile
python scripts/generate_campaign_tuning.py --source-profile my_campaign --apply-profile
```

Run with a registered profile:

```bash
python main.py --campaign data/campaign_template.json --source-profile my_campaign --turns 8 --seed 7
```

Automatic campaign AI tuning process (theme/tone aware):

```bash
# Build/update AI policy for currently focused profile and write ai_policy_json into profile
python scripts/generate_campaign_tuning.py --source-profile cos --apply-profile

# Optional: override party for tuning synthesis
python scripts/generate_campaign_tuning.py --source-profile cos --party-json data/parties/party_cos_survival.json --apply-profile
```

`generate_campaign_tuning.py` now always performs AI drafting (requires `OPENAI_API_KEY`).

When the profile is focused, `main.py` and `weekly_scheduler.py` now auto-resolve:

- `campaign_json`
- `source_chunks_json`
- `ai_policy_json`

...from `data/source_profiles.json` whenever CLI defaults are left unchanged.

Weekly autonomous session mode with persistent checkpoints:

```bash
# Start or continue campaign and save session checkpoint
python main.py \
	--campaign data/campaign_cos.json \
	--source-profile cos \
	--party-json data/parties/party_cos_survival.json \
	--use-ledger \
	--campaign-id strahd_weekly \
	--ledger-dir data/ledger \
	--turns 8 \
	--seed 7

# Resume next week's session from latest checkpoint
python main.py \
	--campaign data/campaign_cos.json \
	--source-profile cos \
	--party-json data/parties/party_cos_survival.json \
	--use-ledger \
	--resume \
	--campaign-id strahd_weekly \
	--ledger-dir data/ledger \
	--turns 8 \
	--seed 8
```

Automated weekly scheduler (auto seed + auto resume + recap briefing):

```bash
# Preview next scheduled run without executing
python scripts/weekly_scheduler.py --campaign-id strahd_weekly --dry-run

# Execute next weekly session
python scripts/weekly_scheduler.py --campaign-id strahd_weekly

# Explicitly disable AI DM/actors if needed
python scripts/weekly_scheduler.py --campaign-id strahd_weekly --no-ai-director --no-ai-actors
```

Scheduler with automatic publishing:

```bash
# Export episode package/text assets each weekly run
python scripts/weekly_scheduler.py --campaign-id strahd_weekly --publish

# Full publish (requires media API keys and ffmpeg)
python scripts/weekly_scheduler.py --campaign-id strahd_weekly --publish --render-media --assemble-video

# Disable weekly report file generation if needed
python scripts/weekly_scheduler.py --campaign-id strahd_weekly --no-weekly-report

# Disable dashboard refresh if needed
python scripts/weekly_scheduler.py --campaign-id strahd_weekly --no-update-dashboard
```

Profile-driven scheduler behavior:

- `weekly_scheduler.py` now resolves `campaign_json`, `campaign_id`, `ai_policy_json`, and optional `party_json` from the selected `--source-profile` when CLI defaults are unchanged.
- This enables plug-and-play onboarding: add/update a source profile entry and the production line routes to the correct campaign automatically.

Build/refresh campaign dashboard manually:

```bash
python scripts/build_campaign_dashboard.py --campaign-id strahd_weekly --ledger-dir data/ledger --weekly-outputs-root outputs/weekly
```

The command above writes:

- `data/ledger/strahd_weekly/dashboard.json`
- `data/ledger/strahd_weekly/dashboard.html`

Scheduler runs also refresh both dashboard files by default (disable HTML with `--no-dashboard-html`).

Serve dashboard locally in browser:

```bash
# Print URL/path and exit
python scripts/serve_dashboard.py --campaign-id strahd_weekly --dry-run

# Start local server (Ctrl+C to stop)
python scripts/serve_dashboard.py --campaign-id strahd_weekly --host 127.0.0.1 --port 8765

# If the port is busy, auto-select the next open port
python scripts/serve_dashboard.py --campaign-id strahd_weekly --host 127.0.0.1 --port 8765 --auto-port

```

Shortcut profile for SRD-only baseline (no campaign PDF chunks):

```bash
python main.py --campaign data/campaign_template.json --source-profile srd --turns 8 --seed 7
```

Run multiple seeds to stress-test campaign paths:

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 30
```

Generate episode-ready content artifacts (narration + prompts):

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 3 --export-episodes --export-dir outputs
```

Render direct media outputs (TTS + images) from exported scenes using OpenAI:

```bash
export OPENAI_API_KEY="your_api_key_here"
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 1 --export-episodes --render-media --export-dir outputs
```

Mix providers (ElevenLabs TTS + OpenAI images):

```bash
export ELEVENLABS_API_KEY="your_elevenlabs_key_here"
export OPENAI_API_KEY="your_openai_key_here"
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 1 --export-episodes --render-media --tts-provider elevenlabs --image-provider openai --export-dir outputs
```

Assemble a full MP4 episode from generated scene media:

```bash
python main.py --campaign data/campaign_template.json --turns 8 --seed 7 --runs 1 --export-episodes --render-media --assemble-video --export-dir outputs
```

Optional model controls:

```bash
python main.py \
	--campaign data/campaign_template.json \
	--turns 8 \
	--seed 7 \
	--runs 1 \
	--export-episodes \
	--render-media \
	--assemble-video \
	--tts-provider openai \
	--image-provider openai \
	--video-filename episode.mp4 \
	--video-fps 24 \
	--video-resolution 1280x720 \
	--openai-tts-model gpt-4o-mini-tts \
	--openai-tts-voice alloy \
	--openai-image-model gpt-image-1 \
	--openai-image-size 1024x1024
```

ElevenLabs-specific controls:

```bash
python main.py \
	--campaign data/campaign_template.json \
	--turns 8 \
	--seed 7 \
	--runs 1 \
	--export-episodes \
	--render-media \
	--tts-provider elevenlabs \
	--image-provider openai \
	--elevenlabs-voice-id EXAVITQu4vr4xnSDxMaL \
	--elevenlabs-model-id eleven_multilingual_v2
```

Output includes:

- `active_content_source` - indicates `5e_srd_2024` when SRD-backed mode is active.
- `source_profile` - named preset used to select source configuration.
- `source_profiles_json` - profile registry file that lets you add campaigns without code changes.
- `use_ledger` / `campaign_id` / `resume` - weekly checkpoint-resume campaign continuity controls.
- `party_json` - optional generated/curated party file used by the run.
- `srd_json` - path to the active merged SRD source file.
- `source_chunks_json` - path to active source chunk JSON when enabled.
- `source_chunks_loaded` - number of loaded source chunks used for prompt grounding.
- `ai_mode` - active AI/policy runtime configuration and key-presence status.
- `summary.tpk_rate` - percentage of runs ending with total party defeat.
- `summary.avg_stalled_turns` - how often turns degrade into passive play (`defend`/`rest`).
- `common_recommendations` - repeated prep advice from simulation patterns.

When `--export-episodes` is enabled, each run also creates:

- `episode_package.json` - structured scene cards for downstream tools.
- `tts_script.txt` - narration script ready for voice generation.
- `image_prompts.txt` - per-scene prompts for image generation.

When `--render-media` is enabled and API access is configured, each run also creates:

- `audio/*.mp3` - narrated audio per scene.
- `images/*.png` - generated visual per scene.
- `media` status block in JSON output for success/failure diagnostics.

When `--assemble-video` is enabled and `ffmpeg` plus scene media are available, each run also creates:

- `episode.mp4` (or your selected filename) in the run output directory.
- `videos` status block in JSON output for success/failure diagnostics.

Supported providers right now:

- TTS: `openai`, `elevenlabs`
- Images: `openai`, `none`

## Next customization points

- Replace `HeuristicActor` with an LLM-backed actor that decides actions from structured prompts.
- Replace `SimpleDirector` with a narrative GM model.
- Implement your chosen rule system by subclassing `BaseRuleset`.
- Expand state with inventories, quests, factions, and long-term memory.
- Add campaign-specific pitfall checks in `analysis.py` (for example: clue gating, economy collapse, boss spike).
- Add adapters to push `tts_script.txt` and `image_prompts.txt` directly into your preferred TTS/image APIs.
