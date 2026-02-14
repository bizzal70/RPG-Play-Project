"""Decision making engine for character actions"""
import random
from typing import List, Optional
from ..models.character import Character
from ..models.campaign import Encounter, EncounterType


class DecisionEngine:
    """Makes decisions for automated character actions"""
    
    def choose_action_in_combat(self, character: Character) -> str:
        """Decide what action to take in combat"""
        # Simple decision logic based on character state
        if character.hit_points < character.max_hit_points * 0.3:
            # Low health - try to use healing item or defensive action
            healing_items = [
                item for item in character.inventory 
                if "potion" in item.name.lower() or "healing" in item.name.lower()
            ]
            if healing_items:
                return f"use_item:{healing_items[0].name}"
            return "defend"
        
        # Check for special abilities
        if character.abilities and random.random() > 0.5:
            ability = random.choice(character.abilities)
            return f"use_ability:{ability.name}"
        
        # Default to attack
        return "attack"
    
    def choose_dialogue_option(
        self,
        character: Character,
        options: List[str]
    ) -> int:
        """Choose a dialogue option"""
        # Simple personality-based selection
        if "aggressive" in character.personality_traits:
            # Prefer confrontational options
            for i, option in enumerate(options):
                if any(word in option.lower() for word in ["fight", "attack", "threaten"]):
                    return i
        
        if "diplomatic" in character.personality_traits:
            # Prefer peaceful options
            for i, option in enumerate(options):
                if any(word in option.lower() for word in ["talk", "negotiate", "peace"]):
                    return i
        
        # Random choice as fallback
        return random.randint(0, len(options) - 1)
    
    def choose_exploration_action(self, character: Character) -> str:
        """Decide exploration action"""
        actions = ["investigate", "search", "proceed_carefully", "rush_forward"]
        
        # Bias based on personality
        if "cautious" in character.personality_traits:
            return random.choice(["investigate", "search", "proceed_carefully"])
        elif "bold" in character.personality_traits:
            return random.choice(["rush_forward", "proceed_carefully"])
        
        return random.choice(actions)
    
    def should_rest(self, party: List[Character]) -> bool:
        """Decide if party should rest"""
        # Rest if any party member is below 50% health
        for character in party:
            if character.is_alive() and character.hit_points < character.max_hit_points * 0.5:
                return True
        return False
    
    def distribute_loot(
        self,
        party: List[Character],
        loot: List[str]
    ) -> dict:
        """Distribute loot among party members"""
        distribution = {character.name: [] for character in party}
        
        for item_name in loot:
            # Randomly assign to party member
            character = random.choice(party)
            distribution[character.name].append(item_name)
        
        return distribution
