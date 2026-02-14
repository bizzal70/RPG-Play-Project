"""Campaign and encounter models"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class EncounterType(str, Enum):
    """Types of encounters"""
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    PUZZLE = "puzzle"
    REST = "rest"


class Difficulty(str, Enum):
    """Encounter difficulty levels"""
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    DEADLY = "deadly"


class Enemy(BaseModel):
    """Represents an enemy in combat"""
    name: str
    hit_points: int
    max_hit_points: int
    armor_class: int
    attack_bonus: int
    damage_dice: str
    challenge_rating: Optional[float] = None
    
    def is_alive(self) -> bool:
        return self.hit_points > 0
    
    def take_damage(self, damage: int) -> int:
        actual_damage = min(damage, self.hit_points)
        self.hit_points = max(0, self.hit_points - damage)
        return actual_damage


class Encounter(BaseModel):
    """Represents a campaign encounter"""
    id: str
    name: str
    description: str
    encounter_type: EncounterType
    difficulty: Difficulty
    
    # Combat specific
    enemies: List[Enemy] = Field(default_factory=list)
    
    # Environmental details
    environment: Optional[str] = None
    
    # Rewards
    experience_reward: int = 0
    loot: List[str] = Field(default_factory=list)
    
    # Story progression
    story_text: Optional[str] = None
    choices: List[str] = Field(default_factory=list)
    consequences: Dict[str, Any] = Field(default_factory=dict)


class Campaign(BaseModel):
    """Represents an RPG campaign"""
    name: str
    description: str
    game_system: str  # "dnd5e", "pathfinder", "shadowdark", etc.
    
    # Campaign structure
    encounters: List[Encounter] = Field(default_factory=list)
    
    # Story elements
    setting: str
    main_objective: str
    background_lore: Optional[str] = None
    
    # Campaign state
    current_encounter_index: int = 0
    completed_encounters: List[str] = Field(default_factory=list)
    
    # Metadata
    min_level: int = 1
    max_level: int = 5
    expected_duration_hours: Optional[float] = None
    
    def get_current_encounter(self) -> Optional[Encounter]:
        """Get the current encounter"""
        if self.current_encounter_index < len(self.encounters):
            return self.encounters[self.current_encounter_index]
        return None
    
    def advance_encounter(self):
        """Move to next encounter"""
        current = self.get_current_encounter()
        if current:
            self.completed_encounters.append(current.id)
        self.current_encounter_index += 1
    
    def is_complete(self) -> bool:
        """Check if campaign is complete"""
        return self.current_encounter_index >= len(self.encounters)
