"""Tests for the automation system."""

import pytest
from rpg_play.characters import Character, CharacterClass
from rpg_play.automation import AIController, CampaignSimulator


class TestAIController:
    """Test the AIController class."""
    
    def test_choose_target(self):
        """Test target selection."""
        hero = Character("Hero", CharacterClass.WARRIOR)
        controller = AIController(hero, seed=42)
        
        enemies = [
            Character("Enemy1", CharacterClass.ROGUE, current_hp=20),
            Character("Enemy2", CharacterClass.MAGE, current_hp=5),
            Character("Enemy3", CharacterClass.WARRIOR, current_hp=15)
        ]
        
        target = controller.choose_target(enemies)
        # Should target the enemy with lowest HP
        assert target.name == "Enemy2"
    
    def test_no_valid_targets(self):
        """Test when there are no valid targets."""
        hero = Character("Hero", CharacterClass.WARRIOR)
        controller = AIController(hero, seed=42)
        
        enemies = [
            Character("Enemy1", CharacterClass.ROGUE, current_hp=0)
        ]
        
        target = controller.choose_target(enemies)
        assert target is None


class TestCampaignSimulator:
    """Test the CampaignSimulator class."""
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        sim = CampaignSimulator(seed=42)
        assert sim.combat_engine is not None
        assert len(sim.ai_controllers) == 0
    
    def test_add_ai_character(self):
        """Test adding AI-controlled characters."""
        sim = CampaignSimulator(seed=42)
        char = Character("Hero", CharacterClass.WARRIOR)
        
        sim.add_ai_character(char)
        assert "Hero" in sim.ai_controllers
    
    def test_simulate_combat(self):
        """Test simulating a combat encounter."""
        sim = CampaignSimulator(seed=42)
        
        team1 = [
            Character("Hero1", CharacterClass.WARRIOR, max_hp=30, current_hp=30),
            Character("Hero2", CharacterClass.MAGE, max_hp=20, current_hp=20)
        ]
        
        team2 = [
            Character("Enemy1", CharacterClass.ROGUE, max_hp=15, current_hp=15),
            Character("Enemy2", CharacterClass.WARRIOR, max_hp=15, current_hp=15)
        ]
        
        # Add AI controllers
        for char in team1 + team2:
            sim.add_ai_character(char)
        
        # Simulate combat
        results = sim.simulate_combat(team1, team2, max_rounds=10)
        
        # Check results
        assert 'rounds' in results
        assert 'winner' in results
        assert 'team1_survivors' in results
        assert 'team2_survivors' in results
        assert 'combat_log' in results
        assert results['rounds'] > 0
        assert results['winner'] in [1, 2]
