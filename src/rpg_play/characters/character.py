"""Character system for RPG Play."""

from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum


class CharacterClass(Enum):
    """Available character classes."""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    CLERIC = "cleric"
    RANGER = "ranger"


@dataclass
class Stats:
    """Character statistics."""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    def get_modifier(self, stat_name: str) -> int:
        """Get the modifier for a given stat."""
        stat_value = getattr(self, stat_name)
        return (stat_value - 10) // 2


@dataclass
class Character:
    """Represents a playable or NPC character."""
    
    name: str
    character_class: CharacterClass
    level: int = 1
    stats: Stats = field(default_factory=Stats)
    
    # Combat stats
    max_hp: int = 10
    current_hp: int = 10
    armor_class: int = 10
    
    # Experience
    experience: int = 0
    
    # Inventory and abilities
    inventory: Dict[str, int] = field(default_factory=dict)
    abilities: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize character based on class."""
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
    
    def is_alive(self) -> bool:
        """Check if character is still alive."""
        return self.current_hp > 0
    
    def take_damage(self, damage: int) -> int:
        """
        Apply damage to the character.
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            Actual damage taken after reductions
        """
        if damage < 0:
            damage = 0
        
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
        
        return damage
    
    def heal(self, amount: int) -> int:
        """
        Heal the character.
        
        Args:
            amount: Amount of healing
            
        Returns:
            Actual amount healed
        """
        if amount < 0:
            amount = 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        return self.current_hp - old_hp
    
    def gain_experience(self, xp: int):
        """Add experience points to the character."""
        self.experience += xp
        
        # Simple leveling system: 100 XP per level
        xp_needed = self.level * 100
        while self.experience >= xp_needed:
            self.level_up()
            xp_needed = self.level * 100
    
    def level_up(self):
        """Level up the character."""
        self.level += 1
        # Increase max HP based on constitution
        hp_gain = 5 + self.stats.get_modifier('constitution')
        self.max_hp += max(1, hp_gain)
        self.current_hp = self.max_hp
    
    def add_item(self, item_name: str, quantity: int = 1):
        """Add an item to the character's inventory."""
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Remove an item from inventory.
        
        Returns:
            True if item was removed, False if not enough quantity
        """
        if item_name not in self.inventory or self.inventory[item_name] < quantity:
            return False
        
        self.inventory[item_name] -= quantity
        if self.inventory[item_name] == 0:
            del self.inventory[item_name]
        
        return True
    
    def __str__(self) -> str:
        """String representation of the character."""
        return (f"{self.name} - Level {self.level} {self.character_class.value.title()}\n"
                f"HP: {self.current_hp}/{self.max_hp} | AC: {self.armor_class} | XP: {self.experience}")
