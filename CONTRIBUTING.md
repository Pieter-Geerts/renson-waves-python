# Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add or update tests as needed
5. Run tests: `pytest`
6. Format code: `black renson_waves_python`
7. Check types: `mypy renson_waves_python`
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Pietergeerts/renson-waves-python.git
cd renson-waves-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black renson_waves_python

# Check types
mypy renson_waves_python
```

## Code Standards

- Use type hints for all functions and methods
- Write docstrings for all public classes and methods
- Keep functions small and focused
- Add tests for new features
- Format with `black` (line length 100)
- Sort imports with `isort`

## Reporting Issues

When reporting issues, please include:

- Python version (`python --version`)
- Device model and firmware version
- Library version (`pip show renson-waves-python`)
- Minimal code example to reproduce the issue
- Full traceback if applicable
