# Contributing to OpenGov-X

Thank you for your interest in contributing to OpenGov-X! This document outlines the process for contributing to any of the OpenGov-X repositories.

## Getting Started

1. **Fork the repository** you want to contribute to
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/repository-name.git
   cd repository-name
   ```
3. **Set up the development environment**:
   ```bash
   uv venv
   uv sync --extra dev
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

- Follow PEP 8 guidelines
- Use `black` for code formatting
- Use `isort` for import sorting
- Use `ruff` for linting
- Use `mypy` for type checking

### Testing

- Write tests for new features
- Ensure all tests pass: `uv run pytest`
- Maintain test coverage above 85%
- Run tests with coverage: `uv run pytest --cov`

### Documentation

- Update docstrings for new functions/classes
- Update README.md if adding new features
- Add examples for complex functionality

## Making Changes

1. **Make your changes** following the coding standards
2. **Add tests** for your changes
3. **Update documentation** as needed
4. **Run tests** to ensure nothing is broken:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy src/
   ```
5. **Format your code**:
   ```bash
   uv run black src/
   uv run isort src/
   ```
6. **Commit your changes** with a descriptive message:
   ```bash
   git add .
   git commit -m "Add: descriptive commit message"
   ```

## Pull Request Process

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. **Create a Pull Request** on GitHub
3. **Fill out the PR template** with:
   - Description of changes
   - Testing performed
   - Screenshots (if applicable)
   - Related issues (if any)
4. **Address review feedback** and update your PR as needed
5. **Wait for approval** from maintainers

## Code Review Process

- All submissions require review from maintainers
- Reviews focus on code quality, functionality, and adherence to standards
- Address all review comments before approval
- Maintainers will merge approved changes

## Reporting Bugs

- Use GitHub Issues to report bugs
- Include detailed reproduction steps
- Include expected vs actual behavior
- Include environment information (Python version, OS, etc.)

## Feature Requests

- Use GitHub Discussions for feature requests
- Clearly describe the feature and use case
- Explain why it would benefit the project

## Security Issues

- Report security issues directly to nikjois@llamasearch.ai
- Do not create public GitHub issues for security vulnerabilities
- Include detailed information about the vulnerability

## License

By contributing, you agree that your contributions will be licensed under the same license as the original project (MIT License).

## Acknowledgments

- Thank you for contributing to OpenGov-X!
- Your efforts help improve government technology and public services
- Contributors will be recognized in project documentation

---

**For questions or support, please contact: nikjois@llamasearch.ai**