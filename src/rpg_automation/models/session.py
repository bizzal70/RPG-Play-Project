"""Session tracking and logging models"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """Types of actions in a session"""
    ATTACK = "attack"
    DEFEND = "defend"
    CAST_SPELL = "cast_spell"
    USE_ITEM = "use_item"
    DIALOGUE = "dialogue"
    EXPLORATION = "exploration"
    REST = "rest"
    DECISION = "decision"


class ActionResult(str, Enum):
    """Result of an action"""
    SUCCESS = "success"
    FAILURE = "failure"
    CRITICAL_SUCCESS = "critical_success"
    CRITICAL_FAILURE = "critical_failure"
    PARTIAL_SUCCESS = "partial_success"


class LogEntry(BaseModel):
    """A single log entry in a session"""
    timestamp: datetime = Field(default_factory=datetime.now)
    character_name: Optional[str] = None
    action_type: ActionType
    description: str
    result: ActionResult
    details: Dict[str, Any] = Field(default_factory=dict)
    narrative: Optional[str] = None


class SessionState(BaseModel):
    """Tracks the state of a play session"""
    session_id: str
    campaign_name: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Party state
    party_members: List[str] = Field(default_factory=list)
    
    # Session progress
    current_encounter_id: Optional[str] = None
    encounters_completed: int = 0
    
    # Session log
    log_entries: List[LogEntry] = Field(default_factory=list)
    
    # Statistics
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    enemies_defeated: int = 0
    treasure_found: int = 0
    experience_gained: int = 0
    
    def add_log_entry(self, entry: LogEntry):
        """Add a log entry to the session"""
        self.log_entries.append(entry)
    
    def get_session_duration(self) -> Optional[float]:
        """Get session duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def end_session(self):
        """Mark session as ended"""
        self.end_time = datetime.now()


class SessionSummary(BaseModel):
    """Summary of a completed session"""
    session_id: str
    campaign_name: str
    duration_seconds: float
    encounters_completed: int
    party_members: List[str]
    
    # Key statistics
    total_damage_dealt: int
    total_damage_taken: int
    enemies_defeated: int
    experience_gained: int
    
    # Narrative summary
    key_events: List[str] = Field(default_factory=list)
    final_outcome: str
    
    # Session highlights
    critical_moments: List[str] = Field(default_factory=list)
