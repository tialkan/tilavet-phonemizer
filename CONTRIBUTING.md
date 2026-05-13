# Contributing to Tilavet Phonemizer

Thank you for your interest in contributing to Tilavet Phonemizer!

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/tilavet-phonemizer
   cd tilavet-phonemizer
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

We use the following tools to maintain code quality:

- **Black** for formatting: `black src/ tests/`
- **isort** for import sorting: `isort src/ tests/`
- **Ruff** for linting: `ruff check src/ tests/`
- **MyPy** for type checking: `mypy src/`

Run all checks:
```bash
black src/ tests/
isort src/ tests/
ruff check src/ tests/
mypy src/
```

## Testing

Run the test suite:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

With pytest (recommended):
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=src/tilavet_phonemizer --cov-report=html
```

## Adding New Rules

When adding new tajwid rules:

1. Implement the rule in `src/tilavet_phonemizer/phonemizer.py`
2. Add unit tests in `tests/test_phonemizer.py`
3. Update `docs/phoneme-spec.md` if new symbols are introduced
4. Run the full test suite
5. Update `CHANGELOG.md`

## Hafiz Review Process

This project uses a multi-LLM hafiz review process for validation:

1. Generate candidate phoneme sequences
2. Submit to LLMs with hafiz expertise prompts
3. Aggregate reviews in `data/validation/`
4. Resolve disputes according to protocol in `docs/hafiz-validation.md`
5. Promote validated sequences to gold standard

See `docs/hafiz-validation.md` for details.

## Submitting Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests and code quality checks
4. Commit with descriptive messages
5. Push to your fork
6. Open a pull request

### Pull Request Guidelines

- Describe the purpose of your PR
- Reference related issues
- Ensure all tests pass
- Update documentation if needed
- Add tests for new features

## Documentation

- Architecture: `docs/architecture.md`
- Phoneme spec: `docs/phoneme-spec.md`
- Hafiz validation: `docs/hafiz-validation.md`
- Roadmap: `orkestra.md`

## Questions?

Open an issue on GitHub for questions or discussions.
