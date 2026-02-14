# RPG Play Project

A fully automated RPG campaign test system built in Python. This framework provides tools for simulating RPG gameplay sessions with automated decision-making, combat mechanics, and narrative generation.

## Features

- **Character System**: Create and manage characters with stats, classes, and abilities
- **Combat Engine**: Automated combat with dice rolling, hit/miss mechanics, and damage calculation
- **AI Controllers**: Intelligent AI decision-making for automated gameplay
- **Campaign Simulator**: Run complete automated combat scenarios
- **Extensible Architecture**: Easy to extend with new character classes, abilities, and game mechanics

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup

1. Clone the repository:
```bash
git clone https://github.com/bizzal70/RPG-Play-Project.git
cd RPG-Play-Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Quick Start

### Running the Example

Try the included combat simulation example:

```bash
python examples/combat_simulation.py
```

This will run an automated combat encounter between a team of heroes and enemies, showing the full combat log and results.

### Basic Usage

```python
from rpg_play.characters import Character, CharacterClass, Stats
from rpg_play.automation import CampaignSimulator

# Create characters
hero = Character(
    name="Sir Galahad",
    character_class=CharacterClass.WARRIOR,
    level=3,
    stats=Stats(strength=16, constitution=14),
    max_hp=30,
    current_hp=30,
    armor_class=16
)

enemy = Character(
    name="Orc Warrior",
    character_class=CharacterClass.WARRIOR,
    level=2,
    max_hp=25,
    current_hp=25,
    armor_class=13
)

# Create simulator
simulator = CampaignSimulator(seed=42)
simulator.add_ai_character(hero)
simulator.add_ai_character(enemy)

# Run combat simulation
results = simulator.simulate_combat([hero], [enemy], max_rounds=10)
print(f"Winner: Team {results['winner']}")
```

## Architecture

### Core Components

1. **Core System** (`rpg_play/core/`)
   - `dice.py`: Dice rolling mechanics with support for advantage/disadvantage
   - Implements standard RPG dice notation (e.g., "2d6+3")

2. **Character System** (`rpg_play/characters/`)
   - `character.py`: Character management with stats, HP, inventory, and leveling
   - Supports multiple character classes: Warrior, Mage, Rogue, Cleric, Ranger

3. **Combat System** (`rpg_play/combat/`)
   - `combat.py`: Combat engine with attack resolution, damage calculation, and combat logging
   - Handles hits, misses, and critical hits

4. **Automation System** (`rpg_play/automation/`)
   - `ai.py`: AI controllers for automated character decision-making
   - Campaign simulator for running complete combat scenarios

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=rpg_play --cov-report=html
```

## Project Structure

```
RPG-Play-Project/
├── src/
│   └── rpg_play/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── dice.py
│       ├── characters/
│       │   ├── __init__.py
│       │   └── character.py
│       ├── combat/
│       │   ├── __init__.py
│       │   └── combat.py
│       ├── automation/
│       │   ├── __init__.py
│       │   └── ai.py
│       └── world/
├── tests/
│   ├── test_dice.py
│   ├── test_character.py
│   ├── test_combat.py
│   └── test_automation.py
├── examples/
│   └── combat_simulation.py
├── docs/
├── requirements.txt
├── setup.py
└── README.md
```

## Future Development Ideas

### Near-term Enhancements
- [ ] **More Character Classes**: Add Paladin, Bard, Druid, Barbarian
- [ ] **Spell System**: Implement magic spells with mana/spell slots
- [ ] **Equipment System**: Add weapons, armor, and magic items with stats
- [ ] **Status Effects**: Implement buffs, debuffs, poison, etc.
- [ ] **Initiative System**: Turn order based on character stats
- [ ] **Skill System**: Add skills and skill checks

### Advanced Features
- [ ] **World/Environment System**: Locations, terrain effects, weather
- [ ] **Quest System**: Quest generation and tracking
- [ ] **NPC Interaction**: Dialogue and relationship systems
- [ ] **Loot System**: Procedural loot generation
- [ ] **Party Management**: Party formation and synergies
- [ ] **Rest and Resource Management**: Long rests, short rests, resource recovery

### Narrative & AI
- [ ] **Story Engine**: Procedural narrative generation
- [ ] **Advanced AI**: More sophisticated decision-making strategies
- [ ] **Character Personalities**: AI behavior based on personality traits
- [ ] **Scenario Generation**: Procedurally generated encounters and campaigns

### Technical Improvements
- [ ] **Save/Load System**: Persist game state
- [ ] **Configuration Files**: YAML/JSON for character templates and scenarios
- [ ] **CLI Interface**: Command-line tool for running simulations
- [ ] **Web Interface**: Browser-based visualization
- [ ] **Logging & Analytics**: Detailed simulation metrics
- [ ] **Performance Optimization**: Parallel simulation support

## Contributing

Contributions are welcome! Areas where you can help:

1. **Add new features** from the roadmap above
2. **Write more tests** to improve coverage
3. **Create examples** showing different use cases
4. **Improve documentation** with tutorials and guides
5. **Report bugs** or suggest enhancements
6. **Optimize performance** for large-scale simulations

## License

This project is open source and available for educational and testing purposes.

## Contact

For questions, suggestions, or collaboration opportunities, please open an issue on GitHub.
