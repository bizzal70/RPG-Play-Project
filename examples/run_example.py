#!/usr/bin/env python3
"""
RPG Campaign Automation - Example Runner

This script demonstrates how to use the RPG automation system to run
a campaign playthrough.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rpg_automation.models.character import Character, Attribute, Ability, Item
from rpg_automation.campaigns.goblin_cave import create_goblin_cave_campaign
from rpg_automation.engine.campaign_engine import CampaignEngine
from rpg_automation.utils.formatter import SessionFormatter


def create_example_party():
    """Create an example adventuring party"""
    
    # Fighter
    fighter = Character(
        name="Thorin Ironforge",
        character_class="Fighter",
        race="Dwarf",
        level=2,
        hit_points=20,
        max_hit_points=20,
        armor_class=16,
        attributes=[
            Attribute(name="Strength", value=16, modifier=3),
            Attribute(name="Dexterity", value=10, modifier=0),
            Attribute(name="Constitution", value=14, modifier=2),
        ],
        abilities=[
            Ability(
                name="Second Wind",
                description="Heal yourself as a bonus action"
            )
        ],
        inventory=[
            Item(name="Longsword", description="A well-crafted sword", item_type="weapon"),
            Item(name="Shield", description="A sturdy shield", item_type="armor"),
            Item(name="Healing Potion", description="Restores 2d4+2 HP", quantity=2, item_type="consumable")
        ],
        personality_traits=["brave", "loyal", "bold"]
    )
    
    # Wizard
    wizard = Character(
        name="Elara Moonwhisper",
        character_class="Wizard",
        race="Elf",
        level=2,
        hit_points=12,
        max_hit_points=12,
        armor_class=12,
        attributes=[
            Attribute(name="Intelligence", value=16, modifier=3),
            Attribute(name="Dexterity", value=14, modifier=2),
            Attribute(name="Constitution", value=10, modifier=0),
        ],
        abilities=[
            Ability(name="Magic Missile", description="Never-miss spell attack"),
            Ability(name="Shield", description="Protective magic"),
        ],
        inventory=[
            Item(name="Spellbook", description="Contains arcane knowledge", item_type="general"),
            Item(name="Wand", description="Focus for spellcasting", item_type="weapon"),
        ],
        personality_traits=["intelligent", "cautious", "curious"]
    )
    
    # Rogue
    rogue = Character(
        name="Shadow",
        character_class="Rogue",
        race="Halfling",
        level=2,
        hit_points=14,
        max_hit_points=14,
        armor_class=15,
        attributes=[
            Attribute(name="Dexterity", value=16, modifier=3),
            Attribute(name="Charisma", value=14, modifier=2),
            Attribute(name="Intelligence", value=12, modifier=1),
        ],
        abilities=[
            Ability(name="Sneak Attack", description="Deal extra damage when hidden"),
            Ability(name="Cunning Action", description="Bonus action dash/hide"),
        ],
        inventory=[
            Item(name="Daggers", description="Twin throwing daggers", quantity=2, item_type="weapon"),
            Item(name="Thieves' Tools", description="For lockpicking", item_type="general"),
        ],
        personality_traits=["sneaky", "diplomatic", "quick-witted"]
    )
    
    return [fighter, wizard, rogue]


def main():
    """Run an example campaign playthrough"""
    print("=" * 60)
    print("RPG CAMPAIGN AUTOMATION - EXAMPLE RUN")
    print("=" * 60)
    print()
    
    # Create campaign and party
    print("Setting up campaign and party...")
    campaign = create_goblin_cave_campaign()
    party = create_example_party()
    
    print(f"Campaign: {campaign.name}")
    print(f"Party size: {len(party)}")
    print()
    
    # Run the campaign
    print("Starting automated playthrough...")
    print("-" * 60)
    
    engine = CampaignEngine(campaign, party)
    summary = engine.run_campaign()
    
    # Display results
    print("\n" + "=" * 60)
    print("PLAYTHROUGH COMPLETE")
    print("=" * 60)
    
    # Print session log
    print("\n--- SESSION LOG ---")
    session_log = SessionFormatter.format_session_log(engine.session)
    print(session_log)
    
    # Print summary
    summary_text = SessionFormatter.format_session_summary(summary)
    print(summary_text)
    
    # Optionally save to files
    save_output = input("\nSave output to files? (y/n): ").lower().strip()
    if save_output == 'y':
        SessionFormatter.save_session_to_file(engine.session, "session_log.txt")
        SessionFormatter.save_summary_to_file(summary, "session_summary.txt")
        print("Saved session_log.txt and session_summary.txt")


if __name__ == "__main__":
    main()
