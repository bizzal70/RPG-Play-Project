"""Tests for the dice rolling system."""

import pytest
from rpg_play.core.dice import DiceRoller, parse_dice_notation


class TestDiceRoller:
    """Test the DiceRoller class."""
    
    def test_basic_roll(self):
        """Test basic dice rolling."""
        roller = DiceRoller(seed=42)
        result = roller.roll(1, 6)
        assert 1 <= result <= 6
    
    def test_multiple_dice(self):
        """Test rolling multiple dice."""
        roller = DiceRoller(seed=42)
        result = roller.roll(3, 6)
        assert 3 <= result <= 18
    
    def test_modifier(self):
        """Test dice with modifier."""
        roller = DiceRoller(seed=42)
        result = roller.roll(1, 6, modifier=5)
        assert 6 <= result <= 11
    
    def test_advantage(self):
        """Test rolling with advantage."""
        roller = DiceRoller(seed=42)
        result = roller.roll_with_advantage(1, 20)
        assert 1 <= result <= 20
    
    def test_disadvantage(self):
        """Test rolling with disadvantage."""
        roller = DiceRoller(seed=42)
        result = roller.roll_with_disadvantage(1, 20)
        assert 1 <= result <= 20
    
    def test_invalid_dice(self):
        """Test that invalid dice raise errors."""
        roller = DiceRoller()
        with pytest.raises(ValueError):
            roller.roll(0, 6)
        with pytest.raises(ValueError):
            roller.roll(1, 0)
        with pytest.raises(ValueError):
            roller.roll(-1, 6)


class TestParseDiceNotation:
    """Test the parse_dice_notation function."""
    
    def test_basic_notation(self):
        """Test parsing basic dice notation."""
        num_dice, num_sides, modifier = parse_dice_notation("2d6")
        assert num_dice == 2
        assert num_sides == 6
        assert modifier == 0
    
    def test_with_positive_modifier(self):
        """Test parsing with positive modifier."""
        num_dice, num_sides, modifier = parse_dice_notation("1d20+5")
        assert num_dice == 1
        assert num_sides == 20
        assert modifier == 5
    
    def test_with_negative_modifier(self):
        """Test parsing with negative modifier."""
        num_dice, num_sides, modifier = parse_dice_notation("3d8-2")
        assert num_dice == 3
        assert num_sides == 8
        assert modifier == -2
    
    def test_uppercase(self):
        """Test parsing uppercase notation."""
        num_dice, num_sides, modifier = parse_dice_notation("2D6+3")
        assert num_dice == 2
        assert num_sides == 6
        assert modifier == 3
