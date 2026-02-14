"""Base RPG system interface"""
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
import random


class DiceRoller:
    """Handles dice rolling for RPG systems"""
    
    @staticmethod
    def roll(dice_notation: str) -> Tuple[int, List[int]]:
        """
        Roll dice using standard notation (e.g., "2d6+3", "1d20")
        Returns: (total, individual_rolls)
        """
        try:
            # Parse dice notation
            modifier = 0
            if '+' in dice_notation:
                dice_part, mod_str = dice_notation.split('+')
                modifier = int(mod_str)
            elif '-' in dice_notation:
                dice_part, mod_str = dice_notation.split('-')
                modifier = -int(mod_str)
            else:
                dice_part = dice_notation
            
            # Parse dice
            num_dice, die_size = dice_part.lower().split('d')
            num_dice = int(num_dice) if num_dice else 1
            die_size = int(die_size)
            
            # Roll dice
            rolls = [random.randint(1, die_size) for _ in range(num_dice)]
            total = sum(rolls) + modifier
            
            return total, rolls
        except Exception as e:
            # Default to 1d6 if parsing fails
            roll = random.randint(1, 6)
            return roll, [roll]
    
    @staticmethod
    def d20() -> int:
        """Roll a d20"""
        return random.randint(1, 20)
    
    @staticmethod
    def advantage() -> int:
        """Roll with advantage (2d20, take highest)"""
        return max(random.randint(1, 20), random.randint(1, 20))
    
    @staticmethod
    def disadvantage() -> int:
        """Roll with disadvantage (2d20, take lowest)"""
        return min(random.randint(1, 20), random.randint(1, 20))


class RPGSystem(ABC):
    """Base class for RPG system implementations"""
    
    def __init__(self):
        self.dice = DiceRoller()
    
    @abstractmethod
    def calculate_attack_roll(self, attacker_bonus: int, target_ac: int) -> Tuple[bool, int, bool]:
        """
        Calculate if attack hits
        Returns: (hit, roll_result, is_critical)
        """
        pass
    
    @abstractmethod
    def calculate_damage(self, damage_dice: str, is_critical: bool = False) -> int:
        """Calculate damage from dice notation"""
        pass
    
    @abstractmethod
    def calculate_saving_throw(self, dc: int, modifier: int) -> Tuple[bool, int]:
        """
        Calculate saving throw
        Returns: (success, roll_result)
        """
        pass
    
    @abstractmethod
    def calculate_skill_check(self, dc: int, modifier: int) -> Tuple[bool, int]:
        """
        Calculate skill check
        Returns: (success, roll_result)
        """
        pass
    
    @abstractmethod
    def calculate_initiative(self, modifier: int) -> int:
        """Calculate initiative roll"""
        pass
    
    @abstractmethod
    def get_system_name(self) -> str:
        """Return the name of this RPG system"""
        pass
