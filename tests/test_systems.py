"""Tests for D&D 5e system"""
import unittest
from rpg_automation.systems.dnd5e import DnD5eSystem


class TestDnD5eSystem(unittest.TestCase):
    """Test D&D 5e system implementation"""
    
    def setUp(self):
        """Set up test system"""
        self.system = DnD5eSystem()
    
    def test_system_name(self):
        """Test system identification"""
        self.assertEqual(self.system.get_system_name(), "D&D 5th Edition")
    
    def test_calculate_damage(self):
        """Test damage calculation"""
        # Normal damage
        damage = self.system.calculate_damage("1d6+2", is_critical=False)
        self.assertGreaterEqual(damage, 3)  # Min: 1+2
        self.assertLessEqual(damage, 8)     # Max: 6+2
        
        # Critical damage should be higher on average
        crit_damage = self.system.calculate_damage("1d6+2", is_critical=True)
        self.assertGreaterEqual(crit_damage, 3)
    
    def test_ability_modifier(self):
        """Test ability modifier calculation"""
        self.assertEqual(self.system.calculate_ability_modifier(10), 0)
        self.assertEqual(self.system.calculate_ability_modifier(16), 3)
        self.assertEqual(self.system.calculate_ability_modifier(8), -1)
        self.assertEqual(self.system.calculate_ability_modifier(20), 5)
    
    def test_attack_roll(self):
        """Test attack roll mechanics"""
        # Test with very high bonus should usually hit AC 10
        hit_count = 0
        for _ in range(100):
            hit, roll, is_crit = self.system.calculate_attack_roll(10, 10)
            if hit:
                hit_count += 1
        
        # Should hit most of the time with +10 vs AC 10
        self.assertGreater(hit_count, 50)
    
    def test_saving_throw(self):
        """Test saving throw mechanics"""
        # Test with high modifier should usually succeed against DC 10
        success_count = 0
        for _ in range(100):
            success, roll = self.system.calculate_saving_throw(10, 5)
            if success:
                success_count += 1
        
        # Should succeed most of the time
        self.assertGreater(success_count, 50)
    
    def test_initiative(self):
        """Test initiative calculation"""
        initiative = self.system.calculate_initiative(2)
        self.assertGreaterEqual(initiative, 3)   # Min: 1+2
        self.assertLessEqual(initiative, 22)     # Max: 20+2


if __name__ == '__main__':
    unittest.main()
