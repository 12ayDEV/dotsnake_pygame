import unittest
from unittest.mock import MagicMock, patch
import sys

# Define a dummy Sprite class to avoid MagicMock inheritance issues
class MockSprite:
    def __init__(self):
        self.rect = MagicMock()
        self.image = MagicMock()
    def kill(self):
        pass

# Mock pygame
mock_pygame = MagicMock()
mock_pygame.sprite.Sprite = MockSprite
# We need to import pygame to get Rect if we want to use real Rect, 
# but we can't import it if we are mocking it in sys.modules.
# So we can either rely on the user environment having pygame and import it before mocking,
# or mock Rect as well.
# Since the previous run showed pygame is installed, let's try to use real pygame.Rect.
try:
    import pygame
    mock_pygame.Rect = pygame.Rect
    mock_pygame.time.Clock = MagicMock()
    mock_pygame.font.Font = MagicMock()
    mock_pygame.display.set_mode = MagicMock()
except ImportError:
    # If pygame is not found (unlikely), mock Rect too
    mock_pygame.Rect = MagicMock

sys.modules['pygame'] = mock_pygame

import dotsnake

class TestPlayer(unittest.TestCase):
    def setUp(self):
        # Mock pygame.time.set_timer to avoid errors
        dotsnake.pygame.time.set_timer = MagicMock()
        dotsnake.pygame.time.get_ticks.return_value = 0
        
        # Mock ParticleSystem
        mock_particle_system = MagicMock()
        self.player = dotsnake.Player(mock_particle_system)

    def test_initialization(self):
        self.assertEqual(len(self.player.body), 3)
        self.assertEqual(self.player.lives, 3)
        self.assertEqual(self.player.dx, 0)
        self.assertEqual(self.player.dy, -1)

    def test_movement(self):
        initial_head = self.player.get_head().copy()
        self.player.dx = 1
        self.player.dy = 0
        self.player.move()
        new_head = self.player.get_head()
        self.assertEqual(new_head.x, initial_head.x + 1)
        self.assertEqual(new_head.y, initial_head.y)

    def test_grow(self):
        initial_length = self.player.get_body_length()
        self.player.grow("standard")
        self.assertEqual(self.player.get_body_length(), initial_length + 1)
        self.assertEqual(self.player.body[-1]["type"], "standard")

    def test_shoot_standard(self):
        # Add a standard dot to body
        self.player.grow("standard")
        initial_length = self.player.get_body_length()
        
        all_sprites = MagicMock()
        standard_bullets = MagicMock()
        charge_bullets = MagicMock()
        all_bullets = MagicMock()
        
        self.player.shoot(all_sprites, standard_bullets, charge_bullets, all_bullets)
        
        # Should consume the standard dot
        self.assertEqual(self.player.get_body_length(), initial_length - 1)
        # Should add to standard_bullets
        self.assertTrue(standard_bullets.add.called)

    def test_hit_lives(self):
        initial_lives = self.player.lives
        self.player.hit()
        self.assertEqual(self.player.lives, initial_lives - 1)

    def test_hit_shield(self):
        # Add shield
        self.player.grow("shield")
        initial_lives = self.player.lives
        self.player.hit()
        # Should lose shield, not life
        self.assertEqual(self.player.lives, initial_lives)
        # Check if shield is gone (last element was shield)
        # Note: hit() removes shield from end? 
        # Code says: for i in range(len(self.body) - 1, 0, -1): if type == "shield": pop
        # So it removes the last added shield if it's at the end?
        # Let's check the code logic in dotsnake.py:
        # for i in range(len(self.body) - 1, 0, -1): if self.body[i]["type"] == "shield": ...
        # Yes, it searches from end to start.
        
        has_shield = any(seg["type"] == "shield" for seg in self.player.body)
        self.assertFalse(has_shield)

class TestBullet(unittest.TestCase):
    def test_initialization_standard(self):
        bullet = dotsnake.Bullet(100, 100, 1, 0, "standard")
        self.assertEqual(bullet.penetration, 1)
        self.assertEqual(bullet.vx, 900)

    def test_initialization_charge(self):
        bullet = dotsnake.Bullet(100, 100, 1, 0, "charge")
        self.assertEqual(bullet.penetration, 999)

if __name__ == '__main__':
    unittest.main()
