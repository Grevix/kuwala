# Contributing to Kuwala

Thank you for your interest in contributing to Kuwala! Kuwala is an open-source quantitative finance library built with a Python user surface and a high-performance compiled Rust numerical core.

---

## 1. Code of Conduct

All contributors and participants are expected to adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 2. Getting Started & Development Setup

### Prerequisites
- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13, or 3.14
- **Rust & Cargo**: 1.70+ (`rustup` recommended)
- **Git**

### Clone & Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/Grevix/kuwala.git
cd kuwala

# 2. Create and activate a virtual environment
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 3. Install development dependencies & build the Rust extension
pip install -e ".[dev,cli]"
maturin develop
```

---

## 3. Running Tests & Quality Checks

Before opening a pull request, ensure all tests and quality checks pass locally:

### Run the Python Test Suite
```bash
python -m pytest -v tests/
```

### Run Rust Core Tests
```bash
cargo test --manifest-path kuwala_core/Cargo.toml
```

### Code Formatting & Linting
```bash
ruff check .
cargo fmt --manifest-path kuwala_core/Cargo.toml --check
```

---

## 4. Development Workflow

1. **Fork the repository** on GitHub.
2. **Create a feature branch**: `git checkout -b feature/my-new-feature`.
3. **Implement your changes**:
   - Write clean, type-annotated code.
   - Maintain numerical consistency and convention integrity.
   - Never vendor raw proprietary datasets in the repository.
4. **Add tests**: Every new quantitative model, signal, or adapter must include automated tests in `tests/`.
5. **Run test suite**: Verify `pytest` passes with 100% success.
6. **Submit a Pull Request**: Provide a clear description of the problem solved, mathematical citations where applicable, and verification evidence.

---

## 5. Pull Request Guidelines

- **Zero Breaking Changes Without RFC**: Substantive API modifications require prior discussion in GitHub Issues.
- **Mathematical Integrity**: New formulas must cite peer-reviewed academic literature or institutional references.
- **Security & Privacy**: Never include API keys, tokens, `.env` files, or proprietary tick archives in PR commits.

Thank you for helping build a foundational open-source quantitative stack!
