"""
Example: Basic combat simulation between two teams.

This example demonstrates how to use the RPG Play system to simulate
an automated combat encounter between heroes and enemies.
"""

from rpg_play.characters import Character, CharacterClass, Stats
from rpg_play.automation import CampaignSimulator


def main():
    """Run a basic combat simulation."""
    print("=" * 60)
    print("RPG Play Project - Combat Simulation Example")
    print("=" * 60)
    print()
    
    # Create hero team
    print("Creating Hero Team...")
    hero1 = Character(
        name="Sir Galahad",
        character_class=CharacterClass.WARRIOR,
        level=3,
        stats=Stats(strength=16, constitution=14),
        max_hp=30,
        current_hp=30,
        armor_class=16
    )
    
    hero2 = Character(
        name="Merlin",
        character_class=CharacterClass.MAGE,
        level=3,
        stats=Stats(intelligence=18, dexterity=12),
        max_hp=20,
        current_hp=20,
        armor_class=12
    )
    
    hero3 = Character(
        name="Aria Swiftbow",
        character_class=CharacterClass.RANGER,
        level=3,
        stats=Stats(dexterity=16, wisdom=14),
        max_hp=25,
        current_hp=25,
        armor_class=14
    )
    
    heroes = [hero1, hero2, hero3]
    
    print(f"  - {hero1}")
    print(f"  - {hero2}")
    print(f"  - {hero3}")
    print()
    
    # Create enemy team
    print("Creating Enemy Team...")
    enemy1 = Character(
        name="Orc Warrior",
        character_class=CharacterClass.WARRIOR,
        level=2,
        stats=Stats(strength=15, constitution=13),
        max_hp=25,
        current_hp=25,
        armor_class=13
    )
    
    enemy2 = Character(
        name="Goblin Rogue",
        character_class=CharacterClass.ROGUE,
        level=2,
        stats=Stats(dexterity=15, intelligence=10),
        max_hp=18,
        current_hp=18,
        armor_class=13
    )
    
    enemy3 = Character(
        name="Dark Mage",
        character_class=CharacterClass.MAGE,
        level=2,
        stats=Stats(intelligence=16, wisdom=12),
        max_hp=16,
        current_hp=16,
        armor_class=11
    )
    
    enemies = [enemy1, enemy2, enemy3]
    
    print(f"  - {enemy1}")
    print(f"  - {enemy2}")
    print(f"  - {enemy3}")
    print()
    
    # Create simulator and add AI controllers
    print("Initializing Campaign Simulator...")
    simulator = CampaignSimulator(seed=42)
    
    for hero in heroes:
        simulator.add_ai_character(hero)
    
    for enemy in enemies:
        simulator.add_ai_character(enemy)
    
    print("AI controllers added for all characters.")
    print()
    
    # Simulate combat
    print("=" * 60)
    print("COMBAT BEGINS!")
    print("=" * 60)
    
    results = simulator.simulate_combat(heroes, enemies, max_rounds=15)
    
    # Print combat log
    for log_entry in results['combat_log']:
        print(log_entry)
    
    # Print results
    print()
    print("=" * 60)
    print("COMBAT RESULTS")
    print("=" * 60)
    print(f"Total Rounds: {results['rounds']}")
    print(f"Winner: Team {results['winner']}")
    print(f"Team 1 Survivors: {', '.join(results['team1_survivors']) if results['team1_survivors'] else 'None'}")
    print(f"Team 2 Survivors: {', '.join(results['team2_survivors']) if results['team2_survivors'] else 'None'}")
    print()
    
    # Print final character states
    print("=" * 60)
    print("FINAL CHARACTER STATES")
    print("=" * 60)
    print("\nHeroes:")
    for hero in heroes:
        status = "ALIVE" if hero.is_alive() else "DEFEATED"
        print(f"  {hero.name}: {hero.current_hp}/{hero.max_hp} HP [{status}]")
    
    print("\nEnemies:")
    for enemy in enemies:
        status = "ALIVE" if enemy.is_alive() else "DEFEATED"
        print(f"  {enemy.name}: {enemy.current_hp}/{enemy.max_hp} HP [{status}]")
    
    print()


if __name__ == "__main__":
    main()
