# API Documentation

## Core Models

### Character (`rpg_automation.models.character`)

#### Character Class
Represents a playable character with stats, abilities, and inventory.

**Attributes:**
- `name: str` - Character name
- `character_class: str` - Class (Fighter, Wizard, etc.)
- `level: int` - Character level
- `hit_points: int` - Current HP
- `max_hit_points: int` - Maximum HP
- `armor_class: int` - Armor class for defense
- `attributes: List[Attribute]` - Character attributes (STR, DEX, etc.)
- `abilities: List[Ability]` - Special abilities and spells
- `inventory: List[Item]` - Items carried
- `personality_traits: List[str]` - For decision-making

**Methods:**
- `is_alive() -> bool` - Check if character is alive
- `take_damage(damage: int) -> int` - Apply damage
- `heal(amount: int) -> int` - Restore hit points
- `add_item(item: Item)` - Add item to inventory
- `use_item(item_name: str) -> Optional[Item]` - Use an item

### Campaign (`rpg_automation.models.campaign`)

#### Campaign Class
Represents a complete campaign with multiple encounters.

**Attributes:**
- `name: str` - Campaign name
- `description: str` - Campaign description
- `game_system: str` - RPG system ("dnd5e", etc.)
- `setting: str` - Campaign setting
- `main_objective: str` - Primary goal
- `encounters: List[Encounter]` - List of encounters
- `current_encounter_index: int` - Progress tracker

**Methods:**
- `get_current_encounter() -> Optional[Encounter]`
- `advance_encounter()` - Move to next encounter
- `is_complete() -> bool` - Check if campaign finished

#### Encounter Class
Represents a single encounter in the campaign.

**Attributes:**
- `id: str` - Unique identifier
- `name: str` - Encounter name
- `description: str` - Description
- `encounter_type: EncounterType` - COMBAT, SOCIAL, EXPLORATION, etc.
- `difficulty: Difficulty` - Difficulty level
- `enemies: List[Enemy]` - For combat encounters
- `experience_reward: int` - XP granted
- `loot: List[str]` - Rewards

### Session (`rpg_automation.models.session`)

#### SessionState Class
Tracks the current session state and logs.

**Attributes:**
- `session_id: str` - Unique session ID
- `campaign_name: str` - Campaign being played
- `party_members: List[str]` - Party member names
- `log_entries: List[LogEntry]` - Detailed action log
- `total_damage_dealt: int` - Statistics
- `enemies_defeated: int` - Statistics

**Methods:**
- `add_log_entry(entry: LogEntry)` - Add to log
- `end_session()` - Mark as complete

## Engine Components

### CampaignEngine (`rpg_automation.engine.campaign_engine`)

Main engine for running campaigns.

```python
engine = CampaignEngine(campaign, party)
summary = engine.run_campaign()
```

**Methods:**
- `run_campaign() -> SessionSummary` - Run complete campaign
- `_run_encounter(encounter)` - Process single encounter

### CombatEngine (`rpg_automation.engine.combat`)

Handles combat resolution.

```python
combat_engine = CombatEngine(rpg_system)
victory, logs = combat_engine.resolve_combat(party, encounter)
```

### DecisionEngine (`rpg_automation.engine.decision`)

Makes decisions for automated characters.

```python
decision_engine = DecisionEngine()
action = decision_engine.choose_action_in_combat(character)
```

## RPG Systems

### Base System (`rpg_automation.systems.base`)

#### RPGSystem (Abstract Base Class)

All RPG systems must implement:
- `calculate_attack_roll(bonus, target_ac) -> (hit, roll, is_crit)`
- `calculate_damage(dice, is_critical) -> int`
- `calculate_saving_throw(dc, modifier) -> (success, roll)`
- `calculate_skill_check(dc, modifier) -> (success, roll)`
- `calculate_initiative(modifier) -> int`
- `get_system_name() -> str`

### D&D 5e System (`rpg_automation.systems.dnd5e`)

Implementation of D&D 5th Edition rules.

```python
system = DnD5eSystem()
hit, roll, is_crit = system.calculate_attack_roll(5, 15)
damage = system.calculate_damage("2d6+3", is_crit)
```

## Utilities

### SessionFormatter (`rpg_automation.utils.formatter`)

Format session output for display.

```python
from rpg_automation.utils.formatter import SessionFormatter

# Format session log
log_text = SessionFormatter.format_session_log(session)

# Format summary
summary_text = SessionFormatter.format_session_summary(summary)

# Save to files
SessionFormatter.save_session_to_file(session, "log.txt")
SessionFormatter.save_summary_to_file(summary, "summary.txt")
```

## Example Usage

### Complete Example

```python
from rpg_automation.models.character import Character, Attribute
from rpg_automation.models.campaign import Campaign, Encounter, EncounterType, Enemy
from rpg_automation.engine.campaign_engine import CampaignEngine

# Create character
hero = Character(
    name="Aragorn",
    character_class="Ranger",
    level=3,
    hit_points=25,
    max_hit_points=25,
    armor_class=16,
    personality_traits=["brave", "tactical"]
)

# Create encounter
encounter = Encounter(
    id="orc_battle",
    name="Orc Ambush",
    description="Orcs attack!",
    encounter_type=EncounterType.COMBAT,
    difficulty=Difficulty.MEDIUM,
    enemies=[
        Enemy(
            name="Orc",
            hit_points=15,
            max_hit_points=15,
            armor_class=13,
            attack_bonus=5,
            damage_dice="1d12+3"
        )
    ],
    experience_reward=200
)

# Create campaign
campaign = Campaign(
    name="The Road to Mordor",
    description="An epic journey",
    game_system="dnd5e",
    setting="Middle Earth",
    main_objective="Destroy the ring",
    encounters=[encounter]
)

# Run campaign
engine = CampaignEngine(campaign, [hero])
summary = engine.run_campaign()

print(f"Result: {summary.final_outcome}")
```
