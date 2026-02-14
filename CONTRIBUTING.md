# Contributing to RPG-Play-Project

Thank you for your interest in contributing to the RPG automation project!

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:
1. Check if the issue already exists
2. Create a new issue with a clear description
3. Include steps to reproduce (for bugs)
4. Add examples or use cases (for features)

### Code Contributions

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python tests/run_tests.py`)
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

### Areas for Contribution

#### New RPG Systems
Add support for other RPG systems:
- Pathfinder 2e
- Shadowdark
- Dragonbane
- Old School Essentials
- Others

Create a new file in `src/rpg_automation/systems/` implementing the `RPGSystem` interface.

#### Enhanced AI Decision Making
Improve the decision-making logic in `src/rpg_automation/engine/decision.py`:
- More sophisticated combat tactics
- Better personality-driven choices
- Learning from past encounters

#### New Campaign Content
Create example campaigns in `src/rpg_automation/campaigns/`:
- Different difficulty levels
- Various themes and settings
- Multi-session campaigns

#### Visualization Tools
- Web-based campaign viewer
- Statistics graphs
- Combat flow diagrams

#### Testing
- Additional unit tests
- Performance tests
- Edge case coverage

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write clear docstrings
- Keep functions focused and small
- Add comments for complex logic

## Testing

Run tests before submitting:
```bash
python tests/run_tests.py
```

## Questions?

Open an issue for questions or discussion!
