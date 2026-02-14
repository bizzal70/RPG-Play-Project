"""Tests for campaign model"""
import unittest
from rpg_automation.models.campaign import (
    Campaign, Encounter, EncounterType, Difficulty, Enemy
)


class TestCampaign(unittest.TestCase):
    """Test campaign model"""
    
    def setUp(self):
        """Set up test campaign"""
        self.encounter1 = Encounter(
            id="enc1",
            name="First Encounter",
            description="Test encounter",
            encounter_type=EncounterType.COMBAT,
            difficulty=Difficulty.EASY
        )
        
        self.encounter2 = Encounter(
            id="enc2",
            name="Second Encounter",
            description="Another test",
            encounter_type=EncounterType.EXPLORATION,
            difficulty=Difficulty.MEDIUM
        )
        
        self.campaign = Campaign(
            name="Test Campaign",
            description="A test campaign",
            game_system="dnd5e",
            setting="Test setting",
            main_objective="Complete tests",
            encounters=[self.encounter1, self.encounter2]
        )
    
    def test_campaign_creation(self):
        """Test basic campaign creation"""
        self.assertEqual(self.campaign.name, "Test Campaign")
        self.assertEqual(len(self.campaign.encounters), 2)
        self.assertFalse(self.campaign.is_complete())
    
    def test_get_current_encounter(self):
        """Test getting current encounter"""
        current = self.campaign.get_current_encounter()
        self.assertIsNotNone(current)
        self.assertEqual(current.id, "enc1")
    
    def test_advance_encounter(self):
        """Test advancing through encounters"""
        self.campaign.advance_encounter()
        self.assertEqual(self.campaign.current_encounter_index, 1)
        self.assertIn("enc1", self.campaign.completed_encounters)
        
        current = self.campaign.get_current_encounter()
        self.assertEqual(current.id, "enc2")
    
    def test_campaign_completion(self):
        """Test campaign completion"""
        self.campaign.advance_encounter()
        self.campaign.advance_encounter()
        self.assertTrue(self.campaign.is_complete())
        self.assertIsNone(self.campaign.get_current_encounter())


class TestEnemy(unittest.TestCase):
    """Test enemy model"""
    
    def test_enemy_creation(self):
        """Test basic enemy creation"""
        enemy = Enemy(
            name="Goblin",
            hit_points=7,
            max_hit_points=7,
            armor_class=15,
            attack_bonus=4,
            damage_dice="1d6+2"
        )
        
        self.assertEqual(enemy.name, "Goblin")
        self.assertTrue(enemy.is_alive())
    
    def test_enemy_damage(self):
        """Test enemy taking damage"""
        enemy = Enemy(
            name="Goblin",
            hit_points=7,
            max_hit_points=7,
            armor_class=15,
            attack_bonus=4,
            damage_dice="1d6+2"
        )
        
        enemy.take_damage(5)
        self.assertEqual(enemy.hit_points, 2)
        self.assertTrue(enemy.is_alive())
        
        enemy.take_damage(5)
        self.assertEqual(enemy.hit_points, 0)
        self.assertFalse(enemy.is_alive())


if __name__ == '__main__':
    unittest.main()
