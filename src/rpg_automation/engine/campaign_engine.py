"""Main campaign playthrough engine"""
from typing import List, Optional
from datetime import datetime
import uuid

from ..models.character import Character
from ..models.campaign import Campaign, Encounter, EncounterType
from ..models.session import SessionState, LogEntry, ActionType, ActionResult, SessionSummary
from ..systems.base import RPGSystem
from ..systems.dnd5e import DnD5eSystem
from .combat import CombatEngine
from .decision import DecisionEngine
from .narrative import NarrativeGenerator


class CampaignEngine:
    """Main engine for running automated campaign playthroughs"""
    
    def __init__(self, campaign: Campaign, party: List[Character]):
        self.campaign = campaign
        self.party = party
        
        # Initialize systems
        self.rpg_system = self._get_rpg_system(campaign.game_system)
        self.combat_engine = CombatEngine(self.rpg_system)
        self.decision_engine = DecisionEngine()
        self.narrative_generator = NarrativeGenerator()
        
        # Session tracking
        self.session: Optional[SessionState] = None
    
    def _get_rpg_system(self, system_name: str) -> RPGSystem:
        """Get RPG system implementation"""
        if system_name.lower() in ["dnd5e", "d&d5e", "dnd_5e"]:
            return DnD5eSystem()
        # Default to D&D 5e for now
        return DnD5eSystem()
    
    def run_campaign(self) -> SessionSummary:
        """Run the complete campaign"""
        # Initialize session
        session_id = str(uuid.uuid4())
        self.session = SessionState(
            session_id=session_id,
            campaign_name=self.campaign.name,
            party_members=[c.name for c in self.party]
        )
        
        # Add opening narrative
        opening_log = LogEntry(
            action_type=ActionType.EXPLORATION,
            description="Campaign begins",
            result=ActionResult.SUCCESS,
            narrative=self.narrative_generator.generate_campaign_opening(
                self.campaign, self.party
            )
        )
        self.session.add_log_entry(opening_log)
        
        # Play through encounters
        while not self.campaign.is_complete():
            encounter = self.campaign.get_current_encounter()
            if not encounter:
                break
            
            self._run_encounter(encounter)
            self.campaign.advance_encounter()
        
        # Complete session
        self.session.end_session()
        
        # Generate summary
        return self._generate_session_summary()
    
    def _run_encounter(self, encounter: Encounter):
        """Run a single encounter"""
        # Log encounter start
        self.session.current_encounter_id = encounter.id
        
        start_log = LogEntry(
            action_type=ActionType.EXPLORATION,
            description=f"Encounter: {encounter.name}",
            result=ActionResult.SUCCESS,
            narrative=self.narrative_generator.generate_encounter_intro(encounter)
        )
        self.session.add_log_entry(start_log)
        
        # Handle based on encounter type
        if encounter.encounter_type == EncounterType.COMBAT:
            self._run_combat_encounter(encounter)
        elif encounter.encounter_type == EncounterType.SOCIAL:
            self._run_social_encounter(encounter)
        elif encounter.encounter_type == EncounterType.EXPLORATION:
            self._run_exploration_encounter(encounter)
        elif encounter.encounter_type == EncounterType.REST:
            self._run_rest_encounter(encounter)
        else:
            # Generic encounter
            self._run_generic_encounter(encounter)
        
        # Award experience and loot
        self._distribute_rewards(encounter)
        
        self.session.encounters_completed += 1
    
    def _run_combat_encounter(self, encounter: Encounter):
        """Run combat encounter"""
        victory, combat_logs = self.combat_engine.resolve_combat(
            self.party, encounter
        )
        
        # Add combat logs to session
        for log in combat_logs:
            self.session.add_log_entry(log)
            
            # Update statistics
            if log.action_type == ActionType.ATTACK and log.result in [
                ActionResult.SUCCESS, ActionResult.CRITICAL_SUCCESS
            ]:
                if log.details.get("damage"):
                    if log.character_name in [c.name for c in self.party]:
                        self.session.total_damage_dealt += log.details["damage"]
                    else:
                        self.session.total_damage_taken += log.details["damage"]
        
        # Count defeated enemies
        self.session.enemies_defeated += len([e for e in encounter.enemies if not e.is_alive()])
        
        if not victory:
            # Party was defeated - campaign ends
            defeat_log = LogEntry(
                action_type=ActionType.ATTACK,
                description="Campaign ended in defeat",
                result=ActionResult.FAILURE,
                narrative="The party could not overcome this challenge..."
            )
            self.session.add_log_entry(defeat_log)
    
    def _run_social_encounter(self, encounter: Encounter):
        """Run social/dialogue encounter"""
        if encounter.choices:
            # Have party leader make choice
            leader = self.party[0] if self.party else None
            if leader:
                choice_index = self.decision_engine.choose_dialogue_option(
                    leader, encounter.choices
                )
                chosen = encounter.choices[choice_index]
                
                social_log = LogEntry(
                    character_name=leader.name,
                    action_type=ActionType.DIALOGUE,
                    description=f"Social interaction in {encounter.name}",
                    result=ActionResult.SUCCESS,
                    narrative=f"{leader.name} chooses: {chosen}"
                )
                self.session.add_log_entry(social_log)
    
    def _run_exploration_encounter(self, encounter: Encounter):
        """Run exploration encounter"""
        # Simple exploration resolution
        explorer = self.party[0] if self.party else None
        if explorer:
            action = self.decision_engine.choose_exploration_action(explorer)
            
            explore_log = LogEntry(
                character_name=explorer.name,
                action_type=ActionType.EXPLORATION,
                description=f"Exploring {encounter.name}",
                result=ActionResult.SUCCESS,
                narrative=f"{explorer.name} decides to {action.replace('_', ' ')}"
            )
            self.session.add_log_entry(explore_log)
    
    def _run_rest_encounter(self, encounter: Encounter):
        """Run rest encounter"""
        # Heal party members
        for character in self.party:
            if character.is_alive():
                healing = character.heal(character.max_hit_points)
                
                rest_log = LogEntry(
                    character_name=character.name,
                    action_type=ActionType.REST,
                    description="Party rests",
                    result=ActionResult.SUCCESS,
                    narrative=f"{character.name} recovers {healing} hit points"
                )
                self.session.add_log_entry(rest_log)
    
    def _run_generic_encounter(self, encounter: Encounter):
        """Run generic encounter"""
        generic_log = LogEntry(
            action_type=ActionType.EXPLORATION,
            description=encounter.name,
            result=ActionResult.SUCCESS,
            narrative=encounter.story_text or encounter.description
        )
        self.session.add_log_entry(generic_log)
    
    def _distribute_rewards(self, encounter: Encounter):
        """Distribute rewards from encounter"""
        # Experience
        if encounter.experience_reward > 0:
            self.session.experience_gained += encounter.experience_reward
            
            xp_log = LogEntry(
                action_type=ActionType.EXPLORATION,
                description="Experience gained",
                result=ActionResult.SUCCESS,
                narrative=f"The party gains {encounter.experience_reward} experience points"
            )
            self.session.add_log_entry(xp_log)
        
        # Loot
        if encounter.loot:
            loot_distribution = self.decision_engine.distribute_loot(
                self.party, encounter.loot
            )
            
            for character_name, items in loot_distribution.items():
                if items:
                    loot_log = LogEntry(
                        character_name=character_name,
                        action_type=ActionType.EXPLORATION,
                        description="Loot found",
                        result=ActionResult.SUCCESS,
                        narrative=f"{character_name} receives: {', '.join(items)}"
                    )
                    self.session.add_log_entry(loot_log)
            
            self.session.treasure_found += len(encounter.loot)
    
    def _generate_session_summary(self) -> SessionSummary:
        """Generate session summary"""
        duration = self.session.get_session_duration() or 0
        
        # Extract key events
        key_events = []
        critical_moments = []
        
        for log in self.session.log_entries:
            if log.result == ActionResult.CRITICAL_SUCCESS:
                critical_moments.append(log.narrative or log.description)
            
            if log.action_type in [ActionType.ATTACK, ActionType.DIALOGUE]:
                if len(key_events) < 10:  # Limit to 10 key events
                    key_events.append(log.narrative or log.description)
        
        # Determine final outcome
        alive_party = [c for c in self.party if c.is_alive()]
        if alive_party and self.campaign.is_complete():
            final_outcome = f"Victory! {len(alive_party)} heroes survived to complete the campaign."
        elif alive_party:
            final_outcome = f"Campaign incomplete. {len(alive_party)} heroes still standing."
        else:
            final_outcome = "Defeat. The party fell in battle."
        
        return SessionSummary(
            session_id=self.session.session_id,
            campaign_name=self.campaign.name,
            duration_seconds=duration,
            encounters_completed=self.session.encounters_completed,
            party_members=self.session.party_members,
            total_damage_dealt=self.session.total_damage_dealt,
            total_damage_taken=self.session.total_damage_taken,
            enemies_defeated=self.session.enemies_defeated,
            experience_gained=self.session.experience_gained,
            key_events=key_events,
            final_outcome=final_outcome,
            critical_moments=critical_moments
        )
