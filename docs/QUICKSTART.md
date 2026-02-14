# Quick Start Guide

## Welcome to RPG Play Project!

This guide will get you up and running with the RPG Play Project in 5 minutes.

## Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/bizzal70/RPG-Play-Project.git
cd RPG-Play-Project

# Install the package
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

## Your First Simulation (1 minute)

Run the included example:

```bash
python examples/combat_simulation.py
```

You'll see an automated combat between heroes and enemies!

## Create Your Own Simulation (2 minutes)

Create a file called `my_battle.py`:

```python
from rpg_play.characters import Character, CharacterClass, Stats
from rpg_play.automation import CampaignSimulator

# Create your hero
hero = Character(
    name="Aragorn",
    character_class=CharacterClass.WARRIOR,
    level=5,
    stats=Stats(strength=18, constitution=16),
    max_hp=50,
    current_hp=50,
    armor_class=17
)

# Create an enemy
dragon = Character(
    name="Smaug",
    character_class=CharacterClass.WARRIOR,
    level=10,
    stats=Stats(strength=20, constitution=18),
    max_hp=100,
    current_hp=100,
    armor_class=18
)

# Set up the simulator
simulator = CampaignSimulator(seed=42)
simulator.add_ai_character(hero)
simulator.add_ai_character(dragon)

# Run the battle!
results = simulator.simulate_combat([hero], [dragon], max_rounds=20)

# Print results
print(f"Combat lasted {results['rounds']} rounds")
print(f"Winner: Team {results['winner']}")

# Show the battle log
for log_entry in results['combat_log']:
    print(log_entry)
```

Run it:
```bash
python my_battle.py
```

## What's Next?

### Explore Examples
Look at `examples/combat_simulation.py` for more complex scenarios

### Read Documentation
- `README.md` - Full project overview
- `docs/DEVELOPMENT.md` - How to extend the system
- `docs/IDEAS_AND_GUIDANCE.md` - Future features and ideas

### Run Tests
```bash
pytest
```

### Modify Characters

Try creating different character classes:

```python
# A powerful mage
mage = Character(
    name="Gandalf",
    character_class=CharacterClass.MAGE,
    level=8,
    stats=Stats(intelligence=20, wisdom=18),
    max_hp=40,
    current_hp=40,
    armor_class=12
)

# A sneaky rogue
rogue = Character(
    name="Robin Hood",
    character_class=CharacterClass.ROGUE,
    level=6,
    stats=Stats(dexterity=18, intelligence=14),
    max_hp=35,
    current_hp=35,
    armor_class=15
)

# A healing cleric
cleric = Character(
    name="Elrond",
    character_class=CharacterClass.CLERIC,
    level=7,
    stats=Stats(wisdom=18, constitution=14),
    max_hp=45,
    current_hp=45,
    armor_class=14
)
```

### Create Team Battles

```python
# Heroes
heroes = [
    Character("Knight", CharacterClass.WARRIOR, max_hp=50),
    Character("Wizard", CharacterClass.MAGE, max_hp=30),
    Character("Ranger", CharacterClass.RANGER, max_hp=40)
]

# Enemies
enemies = [
    Character("Orc Chief", CharacterClass.WARRIOR, max_hp=60),
    Character("Goblin", CharacterClass.ROGUE, max_hp=20),
    Character("Goblin", CharacterClass.ROGUE, max_hp=20),
    Character("Shaman", CharacterClass.MAGE, max_hp=25)
]

# Add AI to all characters
simulator = CampaignSimulator()
for char in heroes + enemies:
    simulator.add_ai_character(char)

# Battle!
results = simulator.simulate_combat(heroes, enemies)
```

## Common Tasks

### Give a Character Items

```python
hero = Character("Hero", CharacterClass.WARRIOR)

# Add items to inventory
hero.add_item("healing_potion", 3)
hero.add_item("sword", 1)
hero.add_item("gold", 100)

# Check inventory
print(hero.inventory)  # {'healing_potion': 3, 'sword': 1, 'gold': 100}

# Use an item
hero.remove_item("healing_potion", 1)
```

### Level Up a Character

```python
hero = Character("Hero", CharacterClass.WARRIOR, level=1)

# Gain experience
hero.gain_experience(100)  # Auto-levels up at 100 XP
print(hero.level)  # 2

# Manual level up
hero.level_up()
print(hero.level)  # 3
```

### Custom Dice Rolls

```python
from rpg_play.core import DiceRoller, parse_dice_notation

roller = DiceRoller(seed=42)

# Roll different dice
print(roller.roll(1, 20))      # d20
print(roller.roll(2, 6, 3))    # 2d6+3
print(roller.roll(4, 8))       # 4d8

# Parse notation
num_dice, num_sides, modifier = parse_dice_notation("3d6+2")
result = roller.roll(num_dice, num_sides, modifier)
```

### Track Combat Statistics

```python
# Run multiple simulations
wins_team1 = 0
total_rounds = []

for i in range(100):
    # Create fresh characters
    hero = Character("Hero", CharacterClass.WARRIOR, max_hp=30)
    enemy = Character("Enemy", CharacterClass.ROGUE, max_hp=25)
    
    simulator = CampaignSimulator(seed=i)
    simulator.add_ai_character(hero)
    simulator.add_ai_character(enemy)
    
    results = simulator.simulate_combat([hero], [enemy])
    
    if results['winner'] == 1:
        wins_team1 += 1
    total_rounds.append(results['rounds'])

# Print statistics
print(f"Team 1 win rate: {wins_team1}%")
print(f"Average combat duration: {sum(total_rounds)/len(total_rounds):.1f} rounds")
```

## Tips for Success

1. **Use Seeds**: Set `seed=42` for reproducible results when debugging
2. **Start Small**: Begin with 1v1 combat, then scale up
3. **Read Logs**: Combat logs show exactly what happened
4. **Experiment**: Try different character builds and team compositions
5. **Check Stats**: Balance is key - adjust HP, AC, and stats for fairness

## Troubleshooting

### Combat Never Ends
Set a reasonable `max_rounds`:
```python
results = simulator.simulate_combat(team1, team2, max_rounds=20)
```

### One Side Always Wins
Balance the teams by adjusting:
- Character levels
- HP and AC values
- Stats (especially strength for attacks)
- Team sizes

### Need More Detail
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

You're ready to:
1. ✅ Create custom characters
2. ✅ Run automated combat simulations
3. ✅ Analyze battle outcomes
4. 🚀 Extend the system with new features!

Check out `docs/IDEAS_AND_GUIDANCE.md` for inspiration on what to build next.

Happy adventuring! ⚔️🛡️🐉
