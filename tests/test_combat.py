"""Tests for the combat system."""

import pytest
from rpg_play.characters import Character, CharacterClass, Stats
from rpg_play.combat import CombatEngine, AttackResult
from rpg_play.core.dice import DiceRoller


class TestCombatEngine:
    """Test the CombatEngine class."""
    
    def test_combat_initialization(self):
        """Test combat engine initialization."""
        engine = CombatEngine()
        assert engine.dice is not None
        assert len(engine.combat_log) == 0
    
    def test_attack_hit(self):
        """Test a successful attack."""
        engine = CombatEngine(DiceRoller(seed=42))
        
        attacker = Character(
            name="Hero",
            character_class=CharacterClass.WARRIOR,
            stats=Stats(strength=16)
        )
        
        defender = Character(
            name="Enemy",
            character_class=CharacterClass.ROGUE,
            max_hp=20,
            current_hp=20,
            armor_class=10
        )
        
        initial_hp = defender.current_hp
        action = engine.attack(attacker, defender)
        
        # Check that an action was created
        assert action.actor == attacker
        assert action.target == defender
        assert len(engine.combat_log) == 1
    
    def test_combat_over(self):
        """Test checking if combat is over."""
        engine = CombatEngine()
        
        team1 = [
            Character("Hero1", CharacterClass.WARRIOR, current_hp=10),
            Character("Hero2", CharacterClass.MAGE, current_hp=10)
        ]
        
        team2 = [
            Character("Enemy1", CharacterClass.ROGUE, current_hp=0),
            Character("Enemy2", CharacterClass.WARRIOR, current_hp=0)
        ]
        
        assert engine.is_combat_over(team1, team2)
        assert engine.get_winner(team1, team2) == 1
    
    def test_combat_ongoing(self):
        """Test that combat continues when both teams are alive."""
        engine = CombatEngine()
        
        team1 = [Character("Hero", CharacterClass.WARRIOR, current_hp=10)]
        team2 = [Character("Enemy", CharacterClass.ROGUE, current_hp=10)]
        
        assert not engine.is_combat_over(team1, team2)
        assert engine.get_winner(team1, team2) is None
    
    def test_clear_log(self):
        """Test clearing the combat log."""
        engine = CombatEngine(DiceRoller(seed=42))
        
        attacker = Character("Hero", CharacterClass.WARRIOR)
        defender = Character("Enemy", CharacterClass.ROGUE)
        
        engine.attack(attacker, defender)
        assert len(engine.combat_log) > 0
        
        engine.clear_log()
        assert len(engine.combat_log) == 0
