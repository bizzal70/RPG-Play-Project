"""Automation and AI decision-making for characters."""

from typing import Optional
import random
from ..characters.character import Character
from ..combat.combat import CombatEngine


class AIController:
    """Basic AI controller for automated character decisions."""
    
    HEALING_THRESHOLD = 0.3  # Heal when HP drops below 30%
    
    def __init__(self, character: Character, seed: Optional[int] = None):
        """Initialize the AI controller for a character."""
        self.character = character
        self.rng = random.Random(seed)
    
    def choose_target(self, possible_targets: list[Character]) -> Optional[Character]:
        """
        Choose a target from available enemies.
        
        Args:
            possible_targets: List of potential targets
            
        Returns:
            Selected target or None if no valid targets
        """
        # Filter for alive targets
        alive_targets = [t for t in possible_targets if t.is_alive()]
        
        if not alive_targets:
            return None
        
        # Simple strategy: target lowest HP enemy
        return min(alive_targets, key=lambda t: t.current_hp)
    
    def decide_action(self, combat_engine: CombatEngine, 
                     enemies: list[Character]) -> str:
        """
        Decide what action to take in combat.
        
        Args:
            combat_engine: The combat engine managing the battle
            enemies: List of enemy characters
            
        Returns:
            Action description
        """
        # Check if healing is needed
        if self.character.current_hp < self.character.max_hp * self.HEALING_THRESHOLD:
            if self._attempt_heal():
                return f"{self.character.name} heals themselves!"
        
        # Choose attack target
        target = self.choose_target(enemies)
        if target:
            action = combat_engine.attack(self.character, target)
            return action.description
        
        return f"{self.character.name} has no valid targets."
    
    def _attempt_heal(self) -> bool:
        """
        Attempt to heal the character.
        
        Returns:
            True if healing was successful
        """
        # Check if character has healing potions
        if self.character.remove_item("healing_potion", 1):
            heal_amount = 10
            self.character.heal(heal_amount)
            return True
        
        return False


class CampaignSimulator:
    """Simulates automated RPG campaign sessions."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the campaign simulator."""
        self.seed = seed
        self.combat_engine = CombatEngine()
        self.ai_controllers: dict[str, AIController] = {}
    
    def add_ai_character(self, character: Character):
        """Add a character with AI control to the simulation."""
        controller = AIController(character, self.seed)
        self.ai_controllers[character.name] = controller
    
    def simulate_combat(self, team1: list[Character], 
                       team2: list[Character], 
                       max_rounds: int = 20) -> dict:
        """
        Simulate a combat encounter between two teams.
        
        Args:
            team1: First team of characters
            team2: Second team of characters
            max_rounds: Maximum number of combat rounds
            
        Returns:
            Dictionary with combat results
        """
        self.combat_engine.clear_log()
        round_num = 0
        combat_log = []
        
        while round_num < max_rounds:
            round_num += 1
            combat_log.append(f"\n--- Round {round_num} ---")
            
            # Team 1 actions
            for char in team1:
                if not char.is_alive():
                    continue
                
                if char.name in self.ai_controllers:
                    controller = self.ai_controllers[char.name]
                    action_desc = controller.decide_action(self.combat_engine, team2)
                    combat_log.append(action_desc)
            
            # Check if combat is over
            if self.combat_engine.is_combat_over(team1, team2):
                break
            
            # Team 2 actions
            for char in team2:
                if not char.is_alive():
                    continue
                
                if char.name in self.ai_controllers:
                    controller = self.ai_controllers[char.name]
                    action_desc = controller.decide_action(self.combat_engine, team1)
                    combat_log.append(action_desc)
            
            # Check if combat is over
            if self.combat_engine.is_combat_over(team1, team2):
                break
        
        # Determine winner
        winner = self.combat_engine.get_winner(team1, team2)
        
        return {
            'rounds': round_num,
            'winner': winner,
            'team1_survivors': [c.name for c in team1 if c.is_alive()],
            'team2_survivors': [c.name for c in team2 if c.is_alive()],
            'combat_log': combat_log
        }
