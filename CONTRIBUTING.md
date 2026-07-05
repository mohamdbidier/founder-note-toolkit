# Contributing to Founder Note Toolkit (FNT)

Thank you for showing interest in contributing to FNT! We love open-source contributions. 

To maintain code quality, readability, and consistency across the codebase, please follow the guidelines below when submitting issues, refactoring, or adding new features.

---

## 🛠️ Development Environment Setup

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/your-username/founder-note-toolkit.git
   cd founder-note-toolkit
   ```

2. **Initialize the Environment**:
   Run the automatic installer to verify prerequisites and prepare dependencies:
   ```bash
   ./install.sh
   ```
   Or set up manually:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

---

## 📐 Code Style & Architecture

This project strictly adheres to **Clean Architecture** and **SOLID** principles.

* **Domain separation**: Keep business logic inside `fnt/services/`, CLI command definitions inside `fnt/commands/`, and definitions inside `fnt/models.py`.
* **Type Hints**: Type annotations are required everywhere. Ensure that all functions and method parameters/returns have explicit type hints.

### Formatting & Linting Tools

We use `black`, `ruff`, and `mypy` to verify code quality. Before submitting a PR, make sure your code passes formatting checks:

```bash
# Run Black Formatter
black --check fnt/ tests/

# Run Ruff Linter
ruff check fnt/ tests/

# Run MyPy Strict Type Checking
mypy fnt/
```

---

## 🧪 Writing and Running Tests

All new functionality must be accompanied by relevant unit tests placed in the `/tests/` directory.

To run the test suite:
```bash
pytest --cov=fnt tests/
```

Ensure that:
* Code coverage does not drop.
* Heavy I/O or network requests (e.g. contacting YouTube or AI APIs) are properly mocked using `unittest.mock`.

---

## 🚀 Pull Request Workflow

1. Create a descriptive branch from `main`:
   ```bash
   git checkout -b feature/my-amazing-feature
   ```
2. Commit your changes with clear, semantic commit messages.
3. Verify that all tests, formatters, and type checkers pass.
4. Push to your fork and submit a Pull Request.
