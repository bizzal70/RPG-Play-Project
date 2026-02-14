# Development Guide

## Overview

This guide provides detailed information for developers who want to contribute to or extend the RPG Play Project.

## Development Setup

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/bizzal70/RPG-Play-Project.git
cd RPG-Play-Project
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with dependencies:
```bash
pip install -e .
pip install -r requirements.txt
```

### Running Tests

The project uses pytest for testing:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_character.py

# Run with coverage report
pytest --cov=rpg_play --cov-report=html
```

## Code Architecture

### Module Overview

#### `rpg_play.core`
Core utilities and mechanics used throughout the system.

- **DiceRoller**: Handles all dice rolling mechanics
  - Standard rolls (e.g., 2d6+3)
  - Advantage/disadvantage rolls
  - Seeded random for reproducibility

#### `rpg_play.characters`
Character creation and management.

- **Character**: Main character class with stats, HP, inventory
- **CharacterClass**: Enum of available classes
- **Stats**: Character statistics (STR, DEX, CON, INT, WIS, CHA)

#### `rpg_play.combat`
Combat mechanics and battle resolution.

- **CombatEngine**: Manages combat encounters
- **CombatAction**: Records individual combat actions
- **AttackResult**: Enum for attack outcomes (hit/miss/critical)

#### `rpg_play.automation`
AI and automation systems.

- **AIController**: Makes decisions for individual characters
- **CampaignSimulator**: Runs automated combat simulations

### Design Patterns

1. **Composition over Inheritance**: Characters compose Stats rather than inherit
2. **Dataclasses**: Used for clean, immutable-style data structures
3. **Dependency Injection**: Combat engine accepts DiceRoller for testability
4. **Strategy Pattern**: AI controllers can be extended with different strategies

## Extending the System

### Adding a New Character Class

1. Add to the CharacterClass enum in `characters/character.py`:
```python
class CharacterClass(Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    # ... existing classes
    PALADIN = "paladin"  # New class
```

2. Optionally customize character creation in `Character.__post_init__()`:
```python
def __post_init__(self):
    if self.character_class == CharacterClass.PALADIN:
        self.armor_class += 2  # Paladins get bonus AC
```

### Adding New Abilities

1. Add to character's abilities list:
```python
char = Character("Hero", CharacterClass.WARRIOR)
char.abilities.append("Second Wind")
char.abilities.append("Action Surge")
```

2. Implement ability logic in combat or AI controller:
```python
def use_ability(self, ability_name: str):
    if ability_name == "Second Wind":
        self.heal(self.level * 5)
```

### Creating Custom AI Strategies

Extend AIController to implement different decision-making:

```python
class AggressiveAI(AIController):
    def choose_target(self, possible_targets):
        # Always target highest HP enemy
        alive_targets = [t for t in possible_targets if t.is_alive()]
        return max(alive_targets, key=lambda t: t.current_hp)

class DefensiveAI(AIController):
    def decide_action(self, combat_engine, enemies):
        # More likely to heal
        if self.character.current_hp < self.character.max_hp * 0.5:
            if self._attempt_heal():
                return f"{self.character.name} heals!"
        return super().decide_action(combat_engine, enemies)
```

### Adding New Mechanics

Example: Adding a spell system

1. Create `rpg_play/spells/spell.py`:
```python
from dataclasses import dataclass

@dataclass
class Spell:
    name: str
    mana_cost: int
    damage_dice: str
    effect: str
```

2. Extend Character to track mana:
```python
@dataclass
class Character:
    # ... existing fields
    max_mana: int = 0
    current_mana: int = 0
    known_spells: list[Spell] = field(default_factory=list)
```

3. Add spell casting to combat engine:
```python
def cast_spell(self, caster: Character, target: Character, spell: Spell):
    if caster.current_mana < spell.mana_cost:
        return  # Not enough mana
    
    caster.current_mana -= spell.mana_cost
    # Implement spell effects
```

## Testing Guidelines

### Writing Tests

Follow these principles:

1. **Test one thing at a time**: Each test should verify a single behavior
2. **Use descriptive names**: Test names should describe what they verify
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use fixtures for setup**: Reuse common test setup

Example test structure:

```python
def test_character_levels_up_with_enough_xp():
    """Test that a character levels up when gaining sufficient XP."""
    # Arrange
    char = Character("Hero", CharacterClass.WARRIOR, level=1)
    initial_level = char.level
    
    # Act
    char.gain_experience(100)
    
    # Assert
    assert char.level == initial_level + 1
    assert char.current_hp == char.max_hp  # HP restored on level up
```

### Test Coverage Goals

- Maintain >80% code coverage
- 100% coverage for core mechanics (dice, combat)
- Test edge cases (death, overflow, empty lists)

## Performance Considerations

### Optimization Tips

1. **Use seeded random for reproducibility**: Helps with debugging and testing
2. **Batch simulations**: Run multiple combats in parallel for statistics
3. **Profile before optimizing**: Use cProfile to find bottlenecks

Example profiling:

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run simulation
simulator.simulate_combat(team1, team2)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Common Development Tasks

### Adding a New Test

```bash
# Create test file
touch tests/test_new_feature.py

# Write tests
# Run to verify
pytest tests/test_new_feature.py -v
```

### Running Examples

```bash
# Run existing example
python examples/combat_simulation.py

# Create new example
touch examples/my_scenario.py
python examples/my_scenario.py
```

### Code Style

The project follows PEP 8 style guidelines:
- Use 4 spaces for indentation
- Maximum line length of 88 characters (Black formatter)
- Use type hints where possible
- Document public APIs with docstrings

## Debugging Tips

### Common Issues

1. **Characters not taking damage**: Check armor class vs attack roll
2. **Combat never ends**: Set max_rounds to prevent infinite loops
3. **Inconsistent results**: Use seeded random for reproducibility

### Debugging Example

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use seeded random for reproducibility
roller = DiceRoller(seed=42)
simulator = CampaignSimulator(seed=42)

# Print combat log
results = simulator.simulate_combat(team1, team2)
for entry in results['combat_log']:
    print(entry)
```

## Contributing Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make changes and add tests**
4. **Run tests**: `pytest`
5. **Commit changes**: `git commit -m "Add my feature"`
6. **Push to fork**: `git push origin feature/my-feature`
7. **Create Pull Request**

## Resources

### Useful Links
- Python Type Hints: https://docs.python.org/3/library/typing.html
- Pytest Documentation: https://docs.pytest.org/
- RPG Mechanics Reference: Various RPG rulebooks

### Additional Reading
- *Game Programming Patterns* by Robert Nystrom
- *The Art of Game Design* by Jesse Schell

## Questions?

If you have questions or need help:
1. Check existing issues on GitHub
2. Review the examples in `examples/`
3. Open a new issue with your question
