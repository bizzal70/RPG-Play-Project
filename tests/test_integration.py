"""Integration tests for campaign playthrough"""
import unittest
from rpg_automation.models.character import Character, Attribute
from rpg_automation.models.campaign import (
    Campaign, Encounter, EncounterType, Difficulty, Enemy
)
from rpg_automation.engine.campaign_engine import CampaignEngine


class TestCampaignPlaythrough(unittest.TestCase):
    """Integration tests for full campaign playthrough"""
    
    def setUp(self):
        """Set up test campaign and party"""
        # Create simple party
        self.party = [
            Character(
                name="Hero",
                character_class="Fighter",
                level=5,
                hit_points=50,
                max_hit_points=50,
                armor_class=18,
                personality_traits=["brave"]
            )
        ]
        
        # Create simple campaign
        self.campaign = Campaign(
            name="Test Quest",
            description="A simple test",
            game_system="dnd5e",
            setting="Test realm",
            main_objective="Win",
            encounters=[
                Encounter(
                    id="combat1",
                    name="Easy Fight",
                    description="A weak enemy",
                    encounter_type=EncounterType.COMBAT,
                    difficulty=Difficulty.EASY,
                    enemies=[
                        Enemy(
                            name="Weak Goblin",
                            hit_points=5,
                            max_hit_points=5,
                            armor_class=10,
                            attack_bonus=2,
                            damage_dice="1d4"
                        )
                    ],
                    experience_reward=50
                ),
                Encounter(
                    id="rest1",
                    name="Rest",
                    description="Take a break",
                    encounter_type=EncounterType.REST,
                    difficulty=Difficulty.TRIVIAL
                )
            ]
        )
    
    def test_full_playthrough(self):
        """Test complete campaign playthrough"""
        engine = CampaignEngine(self.campaign, self.party)
        summary = engine.run_campaign()
        
        # Verify summary
        self.assertIsNotNone(summary)
        self.assertEqual(summary.campaign_name, "Test Quest")
        self.assertEqual(len(summary.party_members), 1)
        self.assertGreaterEqual(summary.encounters_completed, 0)
        
        # Verify session was tracked
        self.assertIsNotNone(engine.session)
        self.assertGreater(len(engine.session.log_entries), 0)
    
    def test_party_survival(self):
        """Test that strong party survives easy encounters"""
        engine = CampaignEngine(self.campaign, self.party)
        summary = engine.run_campaign()
        
        # Strong party should survive
        self.assertTrue(self.party[0].is_alive())
        self.assertGreater(self.party[0].hit_points, 0)


if __name__ == '__main__':
    unittest.main()
