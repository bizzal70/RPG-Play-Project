"""Core utilities for the RPG Play system."""

import random
from typing import Optional


class DiceRoller:
    """Handles dice rolling mechanics for the RPG system."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the dice roller with an optional seed for reproducibility."""
        self.rng = random.Random(seed)
    
    def roll(self, num_dice: int, num_sides: int, modifier: int = 0) -> int:
        """
        Roll dice and return the total.
        
        Args:
            num_dice: Number of dice to roll
            num_sides: Number of sides on each die
            modifier: Modifier to add to the total
            
        Returns:
            Total of all dice rolls plus modifier
        """
        if num_dice <= 0 or num_sides <= 0:
            raise ValueError("Number of dice and sides must be positive")
        
        total = sum(self.rng.randint(1, num_sides) for _ in range(num_dice))
        return total + modifier
    
    def roll_with_advantage(self, num_dice: int, num_sides: int, modifier: int = 0) -> int:
        """Roll twice and take the higher result."""
        roll1 = self.roll(num_dice, num_sides, modifier)
        roll2 = self.roll(num_dice, num_sides, modifier)
        return max(roll1, roll2)
    
    def roll_with_disadvantage(self, num_dice: int, num_sides: int, modifier: int = 0) -> int:
        """Roll twice and take the lower result."""
        roll1 = self.roll(num_dice, num_sides, modifier)
        roll2 = self.roll(num_dice, num_sides, modifier)
        return min(roll1, roll2)


def parse_dice_notation(notation: str) -> tuple[int, int, int]:
    """
    Parse dice notation like '2d6+3' into components.
    
    Args:
        notation: Dice notation string (e.g., '2d6+3', '1d20', '3d8-2')
        
    Returns:
        Tuple of (num_dice, num_sides, modifier)
    """
    notation = notation.lower().replace(' ', '')
    
    # Handle modifier
    modifier = 0
    if '+' in notation:
        notation, mod_str = notation.split('+')
        modifier = int(mod_str)
    elif '-' in notation:
        notation, mod_str = notation.split('-')
        modifier = -int(mod_str)
    
    # Parse dice
    num_dice, num_sides = notation.split('d')
    return int(num_dice), int(num_sides), modifier
