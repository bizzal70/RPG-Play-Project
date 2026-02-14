"""Combat system for RPG Play."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from ..characters.character import Character
from ..core.dice import DiceRoller


class AttackResult(Enum):
    """Outcome of an attack."""
    MISS = "miss"
    HIT = "hit"
    CRITICAL_HIT = "critical_hit"


@dataclass
class CombatAction:
    """Represents a combat action taken by a character."""
    actor: Character
    target: Character
    action_type: str
    result: AttackResult
    damage: int = 0
    description: str = ""


class CombatEngine:
    """Manages combat encounters."""
    
    def __init__(self, dice_roller: Optional[DiceRoller] = None):
        """Initialize the combat engine."""
        self.dice = dice_roller or DiceRoller()
        self.combat_log: list[CombatAction] = []
    
    def attack(self, attacker: Character, defender: Character, 
               weapon_damage: str = "1d6") -> CombatAction:
        """
        Perform an attack from one character to another.
        
        Args:
            attacker: The attacking character
            defender: The defending character
            weapon_damage: Damage dice notation (e.g., "1d6", "2d8+2")
            
        Returns:
            CombatAction describing the outcome
        """
        # Roll to hit (d20 + modifiers)
        attack_roll = self.dice.roll(1, 20)
        
        # Determine if hit
        if attack_roll == 20:
            result = AttackResult.CRITICAL_HIT
        elif attack_roll == 1:
            result = AttackResult.MISS
        elif attack_roll + attacker.stats.get_modifier('strength') >= defender.armor_class:
            result = AttackResult.HIT
        else:
            result = AttackResult.MISS
        
        # Calculate damage
        damage = 0
        if result == AttackResult.HIT:
            # Parse weapon damage
            from ..core.dice import parse_dice_notation
            num_dice, num_sides, modifier = parse_dice_notation(weapon_damage)
            damage = self.dice.roll(num_dice, num_sides, modifier)
            damage = max(1, damage)  # Minimum 1 damage
            defender.take_damage(damage)
        elif result == AttackResult.CRITICAL_HIT:
            # Critical hit: double damage dice
            from ..core.dice import parse_dice_notation
            num_dice, num_sides, modifier = parse_dice_notation(weapon_damage)
            damage = self.dice.roll(num_dice * 2, num_sides, modifier)
            damage = max(1, damage)
            defender.take_damage(damage)
        
        # Create action
        description = self._create_attack_description(attacker, defender, result, damage)
        action = CombatAction(
            actor=attacker,
            target=defender,
            action_type="attack",
            result=result,
            damage=damage,
            description=description
        )
        
        self.combat_log.append(action)
        return action
    
    def _create_attack_description(self, attacker: Character, defender: Character,
                                   result: AttackResult, damage: int) -> str:
        """Create a description of the attack."""
        if result == AttackResult.MISS:
            return f"{attacker.name} attacks {defender.name} but misses!"
        elif result == AttackResult.HIT:
            return f"{attacker.name} hits {defender.name} for {damage} damage!"
        else:  # CRITICAL_HIT
            return f"{attacker.name} critically hits {defender.name} for {damage} damage!"
    
    def is_combat_over(self, team1: list[Character], team2: list[Character]) -> bool:
        """Check if combat is over (one team is defeated)."""
        team1_alive = any(char.is_alive() for char in team1)
        team2_alive = any(char.is_alive() for char in team2)
        return not (team1_alive and team2_alive)
    
    def get_winner(self, team1: list[Character], team2: list[Character]) -> Optional[int]:
        """
        Get the winning team.
        
        Returns:
            1 if team1 wins, 2 if team2 wins, None if combat is still ongoing
        """
        if not self.is_combat_over(team1, team2):
            return None
        
        team1_alive = any(char.is_alive() for char in team1)
        return 1 if team1_alive else 2
    
    def clear_log(self):
        """Clear the combat log."""
        self.combat_log.clear()
