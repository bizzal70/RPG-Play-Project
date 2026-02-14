"""Character model for RPG automation"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Attribute(BaseModel):
    """Represents a character attribute (STR, DEX, CON, etc.)"""
    name: str
    value: int
    modifier: Optional[int] = None


class Ability(BaseModel):
    """Represents a character ability or skill"""
    name: str
    description: str
    cost: Optional[int] = None
    cooldown: Optional[int] = None


class Item(BaseModel):
    """Represents an item in inventory"""
    name: str
    description: str
    quantity: int = 1
    item_type: str = "general"  # weapon, armor, consumable, general


class Character(BaseModel):
    """Represents a playable character"""
    name: str
    character_class: str
    level: int = 1
    race: Optional[str] = None
    
    # Core stats
    hit_points: int
    max_hit_points: int
    armor_class: Optional[int] = 10
    
    # Attributes
    attributes: List[Attribute] = Field(default_factory=list)
    
    # Abilities and skills
    abilities: List[Ability] = Field(default_factory=list)
    
    # Inventory
    inventory: List[Item] = Field(default_factory=list)
    
    # Character state
    status_effects: List[str] = Field(default_factory=list)
    
    # Background and personality
    background: Optional[str] = None
    personality_traits: List[str] = Field(default_factory=list)
    
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.hit_points > 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to character"""
        actual_damage = min(damage, self.hit_points)
        self.hit_points = max(0, self.hit_points - damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal character"""
        actual_healing = min(amount, self.max_hit_points - self.hit_points)
        self.hit_points = min(self.max_hit_points, self.hit_points + amount)
        return actual_healing
    
    def add_item(self, item: Item):
        """Add item to inventory"""
        # Check if item already exists and stack
        for inv_item in self.inventory:
            if inv_item.name == item.name and inv_item.item_type == item.item_type:
                inv_item.quantity += item.quantity
                return
        self.inventory.append(item)
    
    def use_item(self, item_name: str) -> Optional[Item]:
        """Use/remove item from inventory"""
        for item in self.inventory:
            if item.name == item_name:
                if item.quantity > 1:
                    item.quantity -= 1
                    return Item(name=item.name, description=item.description, 
                              quantity=1, item_type=item.item_type)
                else:
                    self.inventory.remove(item)
                    return item
        return None
