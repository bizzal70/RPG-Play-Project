"""Combat resolution engine"""
from typing import List, Dict, Tuple, Optional
import random
from ..models.character import Character
from ..models.campaign import Enemy, Encounter
from ..models.session import LogEntry, ActionType, ActionResult
from ..systems.base import RPGSystem


class CombatEngine:
    """Handles combat encounters"""
    
    def __init__(self, rpg_system: RPGSystem):
        self.system = rpg_system
    
    def resolve_combat(
        self, 
        party: List[Character], 
        encounter: Encounter
    ) -> Tuple[bool, List[LogEntry]]:
        """
        Resolve a combat encounter
        Returns: (party_victory, log_entries)
        """
        log_entries = []
        
        # Initialize combat
        active_enemies = [e for e in encounter.enemies]
        
        log_entries.append(LogEntry(
            action_type=ActionType.ATTACK,
            description=f"Combat begins! {len(party)} heroes vs {len(active_enemies)} enemies",
            result=ActionResult.SUCCESS,
            narrative=f"The party encounters {', '.join([e.name for e in active_enemies])}"
        ))
        
        round_number = 1
        max_rounds = 20  # Prevent infinite loops
        
        while round_number <= max_rounds:
            # Check victory conditions
            alive_party = [c for c in party if c.is_alive()]
            alive_enemies = [e for e in active_enemies if e.is_alive()]
            
            if not alive_enemies:
                log_entries.append(LogEntry(
                    action_type=ActionType.ATTACK,
                    description="All enemies defeated!",
                    result=ActionResult.SUCCESS,
                    narrative="The party emerges victorious!"
                ))
                return True, log_entries
            
            if not alive_party:
                log_entries.append(LogEntry(
                    action_type=ActionType.ATTACK,
                    description="The party has been defeated",
                    result=ActionResult.FAILURE,
                    narrative="The party falls in battle..."
                ))
                return False, log_entries
            
            # Combat round
            round_entries = self._execute_combat_round(alive_party, alive_enemies, round_number)
            log_entries.extend(round_entries)
            
            round_number += 1
        
        # Timeout - consider it a party victory if they're still alive
        return len(alive_party) > 0, log_entries
    
    def _execute_combat_round(
        self,
        party: List[Character],
        enemies: List[Enemy],
        round_number: int
    ) -> List[LogEntry]:
        """Execute one round of combat"""
        log_entries = []
        
        log_entries.append(LogEntry(
            action_type=ActionType.ATTACK,
            description=f"--- Round {round_number} ---",
            result=ActionResult.SUCCESS
        ))
        
        # Party attacks
        for character in party:
            if not character.is_alive():
                continue
            
            # Choose a random alive enemy
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                break
            
            target = random.choice(alive_enemies)
            entry = self._character_attacks_enemy(character, target)
            log_entries.append(entry)
        
        # Enemy attacks
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            
            # Choose a random alive party member
            alive_party = [c for c in party if c.is_alive()]
            if not alive_party:
                break
            
            target = random.choice(alive_party)
            entry = self._enemy_attacks_character(enemy, target)
            log_entries.append(entry)
        
        return log_entries
    
    def _character_attacks_enemy(
        self,
        character: Character,
        enemy: Enemy
    ) -> LogEntry:
        """Resolve character attacking enemy"""
        # Simple attack calculation
        attack_bonus = 5  # Default attack bonus
        hit, roll, is_critical = self.system.calculate_attack_roll(
            attack_bonus, enemy.armor_class
        )
        
        if hit:
            # Calculate damage
            damage_dice = "1d8+3"  # Default damage
            damage = self.system.calculate_damage(damage_dice, is_critical)
            actual_damage = enemy.take_damage(damage)
            
            result = ActionResult.CRITICAL_SUCCESS if is_critical else ActionResult.SUCCESS
            
            status = ""
            if not enemy.is_alive():
                status = f" {enemy.name} is defeated!"
            
            return LogEntry(
                character_name=character.name,
                action_type=ActionType.ATTACK,
                description=f"{character.name} attacks {enemy.name}",
                result=result,
                details={
                    "roll": roll,
                    "damage": actual_damage,
                    "target_ac": enemy.armor_class,
                    "is_critical": is_critical
                },
                narrative=f"{character.name} strikes {enemy.name} for {actual_damage} damage!{status}"
            )
        else:
            return LogEntry(
                character_name=character.name,
                action_type=ActionType.ATTACK,
                description=f"{character.name} attacks {enemy.name}",
                result=ActionResult.FAILURE,
                details={"roll": roll, "target_ac": enemy.armor_class},
                narrative=f"{character.name}'s attack misses {enemy.name}"
            )
    
    def _enemy_attacks_character(
        self,
        enemy: Enemy,
        character: Character
    ) -> LogEntry:
        """Resolve enemy attacking character"""
        hit, roll, is_critical = self.system.calculate_attack_roll(
            enemy.attack_bonus,
            character.armor_class or 10
        )
        
        if hit:
            damage = self.system.calculate_damage(enemy.damage_dice, is_critical)
            actual_damage = character.take_damage(damage)
            
            result = ActionResult.CRITICAL_SUCCESS if is_critical else ActionResult.SUCCESS
            
            status = ""
            if not character.is_alive():
                status = f" {character.name} falls unconscious!"
            
            return LogEntry(
                character_name=enemy.name,
                action_type=ActionType.ATTACK,
                description=f"{enemy.name} attacks {character.name}",
                result=result,
                details={
                    "roll": roll,
                    "damage": actual_damage,
                    "target_ac": character.armor_class,
                    "is_critical": is_critical
                },
                narrative=f"{enemy.name} hits {character.name} for {actual_damage} damage!{status}"
            )
        else:
            return LogEntry(
                character_name=enemy.name,
                action_type=ActionType.ATTACK,
                description=f"{enemy.name} attacks {character.name}",
                result=ActionResult.FAILURE,
                details={"roll": roll, "target_ac": character.armor_class},
                narrative=f"{enemy.name}'s attack misses {character.name}"
            )
