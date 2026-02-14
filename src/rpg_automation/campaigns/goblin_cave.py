"""Example campaign: The Goblin Cave"""
from ..models.campaign import Campaign, Encounter, EncounterType, Difficulty, Enemy


def create_goblin_cave_campaign() -> Campaign:
    """Create a simple example campaign"""
    
    # Encounter 1: Forest Ambush
    encounter1 = Encounter(
        id="forest_ambush",
        name="Forest Ambush",
        description="As you travel through the forest, goblin scouts spot you and attack!",
        encounter_type=EncounterType.COMBAT,
        difficulty=Difficulty.EASY,
        enemies=[
            Enemy(
                name="Goblin Scout",
                hit_points=7,
                max_hit_points=7,
                armor_class=15,
                attack_bonus=4,
                damage_dice="1d6+2",
                challenge_rating=0.25
            ),
            Enemy(
                name="Goblin Scout",
                hit_points=7,
                max_hit_points=7,
                armor_class=15,
                attack_bonus=4,
                damage_dice="1d6+2",
                challenge_rating=0.25
            )
        ],
        environment="Dense forest with thick undergrowth",
        experience_reward=100,
        loot=["Goblin spear", "10 gold pieces"]
    )
    
    # Encounter 2: Cave Entrance
    encounter2 = Encounter(
        id="cave_entrance",
        name="Cave Entrance Discovery",
        description="You discover the entrance to a goblin cave hidden behind thick vines.",
        encounter_type=EncounterType.EXPLORATION,
        difficulty=Difficulty.EASY,
        environment="Rocky hillside with a dark cave opening",
        story_text="The tracks lead here. Inside, you hear goblin voices echoing.",
        choices=["Enter stealthily", "Charge in boldly", "Set up an ambush"],
        experience_reward=50
    )
    
    # Encounter 3: Cave Interior Battle
    encounter3 = Encounter(
        id="cave_battle",
        name="Goblin War Party",
        description="Inside the cave, you encounter a group of goblins led by a fierce warrior!",
        encounter_type=EncounterType.COMBAT,
        difficulty=Difficulty.MEDIUM,
        enemies=[
            Enemy(
                name="Goblin Warrior",
                hit_points=15,
                max_hit_points=15,
                armor_class=16,
                attack_bonus=5,
                damage_dice="1d8+3",
                challenge_rating=0.5
            ),
            Enemy(
                name="Goblin",
                hit_points=7,
                max_hit_points=7,
                armor_class=15,
                attack_bonus=4,
                damage_dice="1d6+2",
                challenge_rating=0.25
            ),
            Enemy(
                name="Goblin",
                hit_points=7,
                max_hit_points=7,
                armor_class=15,
                attack_bonus=4,
                damage_dice="1d6+2",
                challenge_rating=0.25
            )
        ],
        environment="Damp cave with stalactites and goblin debris",
        experience_reward=200,
        loot=["Silver dagger", "Healing potion", "30 gold pieces"]
    )
    
    # Encounter 4: Treasure Chamber
    encounter4 = Encounter(
        id="treasure_chamber",
        name="Hidden Treasure",
        description="Beyond the battle, you find the goblins' treasure cache!",
        encounter_type=EncounterType.EXPLORATION,
        difficulty=Difficulty.EASY,
        environment="Small chamber with stolen goods piled high",
        story_text="Among the loot, you find items stolen from nearby villages.",
        experience_reward=100,
        loot=["Ancient sword", "Magic ring", "100 gold pieces", "Village heirloom"]
    )
    
    # Encounter 5: Return Journey
    encounter5 = Encounter(
        id="return_rest",
        name="Safe Rest",
        description="With the goblins defeated, you set up camp and rest.",
        encounter_type=EncounterType.REST,
        difficulty=Difficulty.TRIVIAL,
        environment="Peaceful forest clearing",
        story_text="The party rests, tending wounds and celebrating their victory.",
        experience_reward=50
    )
    
    campaign = Campaign(
        name="The Goblin Cave",
        description="A simple adventure to clear out a goblin infestation",
        game_system="dnd5e",
        setting="A small frontier village plagued by goblin raids",
        main_objective="Clear the goblin cave and recover stolen goods",
        background_lore="Local goblins have been raiding the village for weeks. "
                       "The village elder asks brave adventurers to eliminate the threat.",
        encounters=[encounter1, encounter2, encounter3, encounter4, encounter5],
        min_level=1,
        max_level=3,
        expected_duration_hours=2.0
    )
    
    return campaign
