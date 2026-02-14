"""Tests for the character system."""

import pytest
from rpg_play.characters import Character, CharacterClass, Stats


class TestStats:
    """Test the Stats class."""
    
    def test_default_stats(self):
        """Test default stat values."""
        stats = Stats()
        assert stats.strength == 10
        assert stats.dexterity == 10
    
    def test_stat_modifiers(self):
        """Test stat modifier calculation."""
        stats = Stats(strength=16, dexterity=8)
        assert stats.get_modifier('strength') == 3
        assert stats.get_modifier('dexterity') == -1


class TestCharacter:
    """Test the Character class."""
    
    def test_character_creation(self):
        """Test creating a character."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.WARRIOR,
            level=1
        )
        assert char.name == "Test Hero"
        assert char.level == 1
        assert char.is_alive()
    
    def test_take_damage(self):
        """Test taking damage."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.WARRIOR,
            max_hp=20,
            current_hp=20
        )
        damage = char.take_damage(5)
        assert damage == 5
        assert char.current_hp == 15
        assert char.is_alive()
    
    def test_death(self):
        """Test character death."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.WARRIOR,
            max_hp=10,
            current_hp=10
        )
        char.take_damage(15)
        assert char.current_hp == 0
        assert not char.is_alive()
    
    def test_healing(self):
        """Test healing."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.CLERIC,
            max_hp=20,
            current_hp=10
        )
        healed = char.heal(5)
        assert healed == 5
        assert char.current_hp == 15
    
    def test_healing_cap(self):
        """Test that healing doesn't exceed max HP."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.CLERIC,
            max_hp=20,
            current_hp=18
        )
        healed = char.heal(10)
        assert healed == 2
        assert char.current_hp == 20
    
    def test_experience_gain(self):
        """Test gaining experience."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.WARRIOR
        )
        char.gain_experience(50)
        assert char.experience == 50
        assert char.level == 1
    
    def test_level_up(self):
        """Test leveling up."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.WARRIOR,
            max_hp=10
        )
        initial_max_hp = char.max_hp
        char.gain_experience(100)
        assert char.level == 2
        assert char.max_hp > initial_max_hp
        assert char.current_hp == char.max_hp
    
    def test_inventory(self):
        """Test inventory management."""
        char = Character(
            name="Test Hero",
            character_class=CharacterClass.ROGUE
        )
        
        # Add items
        char.add_item("sword", 1)
        char.add_item("potion", 3)
        assert char.inventory["sword"] == 1
        assert char.inventory["potion"] == 3
        
        # Remove items
        assert char.remove_item("potion", 2)
        assert char.inventory["potion"] == 1
        
        # Try to remove more than available
        assert not char.remove_item("potion", 5)
        assert char.inventory["potion"] == 1
