"""D&D 5th Edition system implementation"""
from typing import Tuple, List
from .base import RPGSystem


class DnD5eSystem(RPGSystem):
    """D&D 5th Edition rules implementation"""
    
    def get_system_name(self) -> str:
        return "D&D 5th Edition"
    
    def calculate_attack_roll(self, attacker_bonus: int, target_ac: int) -> Tuple[bool, int, bool]:
        """
        D&D 5e attack roll
        Returns: (hit, roll_result, is_critical)
        """
        roll = self.dice.d20()
        total = roll + attacker_bonus
        
        # Natural 20 is always a critical hit
        if roll == 20:
            return True, total, True
        
        # Natural 1 is always a miss
        if roll == 1:
            return False, total, False
        
        # Normal hit check
        hit = total >= target_ac
        return hit, total, False
    
    def calculate_damage(self, damage_dice: str, is_critical: bool = False) -> int:
        """
        D&D 5e damage calculation
        Critical hits double the dice rolled
        """
        if is_critical:
            # Double the dice for critical hits
            damage1, _ = self.dice.roll(damage_dice)
            damage2, _ = self.dice.roll(damage_dice)
            return damage1 + damage2
        else:
            damage, _ = self.dice.roll(damage_dice)
            return max(0, damage)
    
    def calculate_saving_throw(self, dc: int, modifier: int) -> Tuple[bool, int]:
        """
        D&D 5e saving throw
        Returns: (success, roll_result)
        """
        roll = self.dice.d20()
        total = roll + modifier
        
        # Natural 20 always succeeds
        if roll == 20:
            return True, total
        
        # Natural 1 always fails
        if roll == 1:
            return False, total
        
        success = total >= dc
        return success, total
    
    def calculate_skill_check(self, dc: int, modifier: int) -> Tuple[bool, int]:
        """
        D&D 5e skill check (same as saving throw)
        Returns: (success, roll_result)
        """
        return self.calculate_saving_throw(dc, modifier)
    
    def calculate_initiative(self, modifier: int) -> int:
        """D&D 5e initiative (d20 + DEX modifier)"""
        roll = self.dice.d20()
        return roll + modifier
    
    def calculate_ability_modifier(self, ability_score: int) -> int:
        """Calculate ability modifier from score"""
        return (ability_score - 10) // 2
