"""Narrative generation for campaign events"""
from typing import List
from ..models.character import Character
from ..models.campaign import Campaign, Encounter


class NarrativeGenerator:
    """Generates narrative text for campaign events"""
    
    def generate_campaign_opening(
        self,
        campaign: Campaign,
        party: List[Character]
    ) -> str:
        """Generate opening narrative for campaign"""
        party_names = ", ".join([c.name for c in party])
        
        narrative = f"""
=== {campaign.name} ===

{campaign.description}

Setting: {campaign.setting}

Objective: {campaign.main_objective}

Our brave adventurers - {party_names} - stand ready to begin their quest.
The party consists of:
"""
        for character in party:
            narrative += f"\n  • {character.name}, a level {character.level} {character.character_class}"
            if character.race:
                narrative += f" ({character.race})"
        
        narrative += f"\n\nTheir journey begins now...\n"
        
        return narrative.strip()
    
    def generate_encounter_intro(self, encounter: Encounter) -> str:
        """Generate intro narrative for an encounter"""
        base = f"\n=== {encounter.name} ===\n\n{encounter.description}"
        
        if encounter.environment:
            base += f"\n\nEnvironment: {encounter.environment}"
        
        if encounter.story_text:
            base += f"\n\n{encounter.story_text}"
        
        return base
    
    def generate_combat_description(
        self,
        attacker_name: str,
        target_name: str,
        damage: int,
        is_critical: bool
    ) -> str:
        """Generate combat action description"""
        if is_critical:
            return f"{attacker_name} lands a devastating critical strike on {target_name} for {damage} damage!"
        else:
            return f"{attacker_name} strikes {target_name} for {damage} damage."
    
    def generate_victory_narrative(self, encounter: Encounter) -> str:
        """Generate victory narrative"""
        return f"The {encounter.name} encounter is complete! The party emerges victorious."
    
    def generate_defeat_narrative(self) -> str:
        """Generate defeat narrative"""
        return "The party has been defeated. Their adventure ends here..."
