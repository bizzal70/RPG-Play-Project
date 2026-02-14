"""Tests for character model"""
import unittest
from rpg_automation.models.character import Character, Attribute, Ability, Item


class TestCharacter(unittest.TestCase):
    """Test character model"""
    
    def setUp(self):
        """Set up test character"""
        self.character = Character(
            name="Test Hero",
            character_class="Fighter",
            level=1,
            hit_points=10,
            max_hit_points=10,
            armor_class=15
        )
    
    def test_character_creation(self):
        """Test basic character creation"""
        self.assertEqual(self.character.name, "Test Hero")
        self.assertEqual(self.character.character_class, "Fighter")
        self.assertEqual(self.character.level, 1)
        self.assertTrue(self.character.is_alive())
    
    def test_take_damage(self):
        """Test damage application"""
        damage = self.character.take_damage(5)
        self.assertEqual(damage, 5)
        self.assertEqual(self.character.hit_points, 5)
        self.assertTrue(self.character.is_alive())
    
    def test_fatal_damage(self):
        """Test character death"""
        damage = self.character.take_damage(15)
        self.assertEqual(damage, 10)  # Can't take more than current HP
        self.assertEqual(self.character.hit_points, 0)
        self.assertFalse(self.character.is_alive())
    
    def test_healing(self):
        """Test healing"""
        self.character.take_damage(5)
        healed = self.character.heal(3)
        self.assertEqual(healed, 3)
        self.assertEqual(self.character.hit_points, 8)
    
    def test_overheal(self):
        """Test healing beyond max HP"""
        self.character.take_damage(5)
        healed = self.character.heal(10)
        self.assertEqual(healed, 5)  # Can only heal up to max
        self.assertEqual(self.character.hit_points, 10)
    
    def test_add_item(self):
        """Test adding items to inventory"""
        item = Item(name="Sword", description="A sharp blade", item_type="weapon")
        self.character.add_item(item)
        self.assertEqual(len(self.character.inventory), 1)
        self.assertEqual(self.character.inventory[0].name, "Sword")
    
    def test_stack_items(self):
        """Test item stacking"""
        item1 = Item(name="Potion", description="Healing", quantity=1, item_type="consumable")
        item2 = Item(name="Potion", description="Healing", quantity=2, item_type="consumable")
        
        self.character.add_item(item1)
        self.character.add_item(item2)
        
        self.assertEqual(len(self.character.inventory), 1)
        self.assertEqual(self.character.inventory[0].quantity, 3)
    
    def test_use_item(self):
        """Test using items"""
        item = Item(name="Potion", description="Healing", quantity=3, item_type="consumable")
        self.character.add_item(item)
        
        used = self.character.use_item("Potion")
        self.assertIsNotNone(used)
        self.assertEqual(used.quantity, 1)
        self.assertEqual(self.character.inventory[0].quantity, 2)


if __name__ == '__main__':
    unittest.main()
