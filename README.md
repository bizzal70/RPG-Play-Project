# RPG-Play-Project

Fully automated RPG campaign playthrough system for modeling and wargaming various RPG scenarios.

## Overview

This project provides an automated system for playing through Fantasy RPG campaigns (D&D, Pathfinder, Dragonbane, Shadowdark, etc.) in a structured and creative way. The system simulates character decisions, resolves combat encounters, handles social interactions, and produces detailed playthrough logs.

## Features

- **Multi-System Support**: Extensible architecture supporting multiple RPG rule systems
  - D&D 5th Edition (currently implemented)
  - Framework for adding Pathfinder, Shadowdark, Dragonbane, and others

- **Complete Campaign Automation**:
  - Combat encounters with dice rolling and damage calculation
  - Social/dialogue encounters with decision-making
  - Exploration and puzzle-solving
  - Rest and recovery mechanics
  - Experience and loot distribution

- **Intelligent Decision Making**:
  - Character personality-based decisions
  - Combat tactics based on health and abilities
  - Strategic resource management

- **Detailed Logging**:
  - Complete session logs with narrative descriptions
  - Combat statistics and outcomes
  - Session summaries with key events
  - Export capabilities for analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/bizzal70/RPG-Play-Project.git
cd RPG-Play-Project

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Quick Start

Run the example campaign:

```bash
python examples/run_example.py
```

This will run "The Goblin Cave" campaign with a pre-made party of three adventurers.

## Usage

### Creating a Custom Campaign

```python
from rpg_automation.models.campaign import Campaign, Encounter, EncounterType, Difficulty, Enemy

# Define encounters
combat_encounter = Encounter(
    id="goblin_fight",
    name="Goblin Ambush",
    description="You encounter goblins on the road!",
    encounter_type=EncounterType.COMBAT,
    difficulty=Difficulty.MEDIUM,
    enemies=[
        Enemy(
            name="Goblin",
            hit_points=7,
            max_hit_points=7,
            armor_class=15,
            attack_bonus=4,
            damage_dice="1d6+2"
        )
    ],
    experience_reward=100,
    loot=["Gold coins", "Rusty dagger"]
)

# Create campaign
campaign = Campaign(
    name="My Adventure",
    description="An exciting quest",
    game_system="dnd5e",
    setting="Fantasy realm",
    main_objective="Defeat the evil wizard",
    encounters=[combat_encounter]
)
```

### Creating a Party

```python
from rpg_automation.models.character import Character, Attribute, Ability, Item

fighter = Character(
    name="Conan",
    character_class="Fighter",
    level=3,
    hit_points=30,
    max_hit_points=30,
    armor_class=16,
    attributes=[
        Attribute(name="Strength", value=16, modifier=3),
        Attribute(name="Constitution", value=14, modifier=2)
    ],
    personality_traits=["brave", "bold"]
)

party = [fighter]
```

### Running the Campaign

```python
from rpg_automation.engine.campaign_engine import CampaignEngine
from rpg_automation.utils.formatter import SessionFormatter

# Initialize and run
engine = CampaignEngine(campaign, party)
summary = engine.run_campaign()

# Display results
print(SessionFormatter.format_session_summary(summary))
```

## Project Structure

```
RPG-Play-Project/
├── src/rpg_automation/
│   ├── models/           # Data models
│   │   ├── character.py  # Character, abilities, inventory
│   │   ├── campaign.py   # Campaigns, encounters, enemies
│   │   └── session.py    # Session tracking and logging
│   ├── systems/          # RPG system implementations
│   │   ├── base.py       # Base system interface
│   │   └── dnd5e.py      # D&D 5e implementation
│   ├── engine/           # Core automation engine
│   │   ├── campaign_engine.py  # Main campaign runner
│   │   ├── combat.py     # Combat resolution
│   │   ├── decision.py   # AI decision making
│   │   └── narrative.py  # Story generation
│   ├── campaigns/        # Campaign definitions
│   │   └── goblin_cave.py
│   └── utils/            # Utilities
│       └── formatter.py  # Output formatting
├── examples/             # Example scripts
│   └── run_example.py
└── tests/                # Test suite

```

## Use Cases

1. **Campaign Testing**: Test campaign balance and difficulty before running with real players
2. **Outcome Modeling**: Simulate multiple playthroughs to analyze different outcomes
3. **AI Research**: Study decision-making in complex game scenarios
4. **Content Generation**: Generate narrative content and example playthroughs
5. **Game Design**: Validate encounter design and progression

## Extending the System

### Adding a New RPG System

1. Create a new file in `src/rpg_automation/systems/`
2. Inherit from `RPGSystem` base class
3. Implement required methods (attack rolls, damage, saving throws, etc.)
4. Register the system in `campaign_engine.py`

### Adding New Encounter Types

1. Add to `EncounterType` enum in `models/campaign.py`
2. Implement handler in `campaign_engine.py`
3. Add decision logic in `decision.py`

## Future Enhancements

- [ ] Additional RPG system implementations (Pathfinder, Shadowdark, etc.)
- [ ] More sophisticated AI decision making with machine learning
- [ ] Web interface for campaign creation and viewing
- [ ] Multi-threaded parallel campaign execution
- [ ] Statistical analysis and visualization tools
- [ ] Import/export for popular campaign formats
- [ ] Natural language campaign description parsing

## Contributing

Contributions are welcome! Areas of interest:
- New RPG system implementations
- Enhanced decision-making algorithms
- Additional example campaigns
- Visualization tools
- Documentation improvements

## License

MIT License - See LICENSE file for details

## Author

RPG Play Project Team
