# Git Setup and Hooks

## 📋 Table of Contents

- [Git Configuration](#git-configuration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Development Workflow](#development-workflow)
- [Branch Management](#branch-management)
- [Code Quality Checks](#code-quality-checks)
- [Release Process](#release-process)

## Git Configuration

### Initial Setup

Configure Git for MyConfig development:

```bash
# Clone the repository
git clone https://github.com/your-org/myconfig.git
cd myconfig

# Configure Git user information
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Set up upstream tracking
git remote add upstream https://github.com/original-org/myconfig.git

# Configure push behavior
git config push.default simple
git config push.autoSetupRemote true
```

### Git Hooks Setup

MyConfig includes pre-commit hooks for code quality assurance:

```bash
# Install pre-commit hooks
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Or use the provided hook
cp contrib/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Repository Configuration

Configure repository-specific settings:

```bash
# Set line ending handling
git config core.autocrlf input
git config core.eol lf

# Enable file mode checking
git config core.filemode true

# Configure merge strategy
git config merge.tool vimdiff
git config merge.conflictstyle diff3
```

## Pre-commit Hooks

### Hook Features

The pre-commit hook performs the following checks:

1. **🔒 Sensitive File Detection**: Prevents accidental commit of sensitive files
2. **🐍 Python Syntax Check**: Validates Python syntax
3. **🐛 Debug Code Detection**: Identifies debugging code
4. **📦 Large File Check**: Prevents large files from being committed
5. **🔐 File Permission Check**: Validates file permissions

### Hook Configuration

Configure hook behavior in `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# MyConfig Pre-commit Hook

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Running pre-commit checks...${NC}"

# Check 1: Sensitive Files
echo -e "${BLUE}🔒 Checking sensitive files...${NC}"
if git diff --cached --name-only | grep -E '\.(key|pem|p12|password|secret)$'; then
    echo -e "${RED}❌ Sensitive files detected in commit${NC}"
    echo "Please review and exclude sensitive files"
    exit 1
fi

# Check 2: Python Syntax
echo -e "${BLUE}🐍 Checking Python syntax...${NC}"
for file in $(git diff --cached --name-only | grep '\.py$'); do
    if [ -f "$file" ]; then
        python3 -m py_compile "$file"
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Python syntax error in $file${NC}"
            exit 1
        fi
    fi
done

# Check 3: Debug Code
echo -e "${BLUE}🐛 Checking debug code...${NC}"
for file in $(git diff --cached --name-only | grep '\.py$'); do
    if [ -f "$file" ]; then
        if grep -n 'print\(' "$file"; then
            echo -e "${YELLOW}⚠️  Detected possible debug code: print\(${NC}"
            echo "Please confirm if debug code should be removed"
        fi
        if grep -n 'pdb\.set_trace\(\|breakpoint\(' "$file"; then
            echo -e "${RED}❌ Debug breakpoints detected${NC}"
            exit 1
        fi
    fi
done

# Check 4: Large Files
echo -e "${BLUE}📦 Checking large files...${NC}"
for file in $(git diff --cached --name-only); do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        if [ $size -gt 1048576 ]; then  # 1MB
            echo -e "${YELLOW}⚠️  Large file detected: $file ($(($size/1024))KB)${NC}"
            echo "Consider using Git LFS for large files"
        fi
    fi
done

# Check 5: File Permissions
echo -e "${BLUE}🔐 Checking file permissions...${NC}"
for file in $(git diff --cached --name-only); do
    if [ -f "$file" ]; then
        if [[ "$file" == bin/* ]] || [[ "$file" == *.sh ]]; then
            if [ ! -x "$file" ]; then
                echo -e "${YELLOW}⚠️  Script file not executable: $file${NC}"
                echo "Run: chmod +x $file"
            fi
        fi
    fi
done

echo -e "${GREEN}✅ Pre-commit checks completed${NC}"
```

### Bypassing Hooks

In exceptional cases, bypass hooks with:

```bash
# Skip pre-commit hooks (use with caution)
git commit --no-verify -m "Emergency fix"

# Skip specific checks by modifying the hook temporarily
```

## Development Workflow

### Feature Development

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-component
   ```

2. **Make Changes**:
   ```bash
   # Edit files
   vim src/core/components/new_component.py
   
   # Add tests
   vim tests/test_new_component.py
   ```

3. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Add new backup component
   
   - Implement database backup component
   - Add PostgreSQL and MySQL support
   - Include component tests and documentation"
   ```

4. **Push and Create PR**:
   ```bash
   git push origin feature/new-component
   # Create pull request on GitHub
   ```

### Commit Message Standards

Use conventional commit format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/maintenance tasks

**Examples**:
```bash
git commit -m "feat(core): add template system

- Implement template engine with Mustache-like syntax
- Add template directory structure
- Support for variables and conditional sections
- Include fallback mechanisms for template failures"

git commit -m "fix(cli): resolve argument parsing error

- Fix issue with --compress argument not being recognized
- Add proper argument validation
- Update help text for clarity"

git commit -m "docs: update installation guide

- Add troubleshooting section
- Include macOS-specific instructions
- Update system requirements"
```

## Branch Management

### Branch Strategy

MyConfig uses a simplified Git flow:

```
main
├── develop
├── feature/template-system
├── feature/compression-support
├── hotfix/critical-bug
└── release/v2.1.0
```

### Branch Types

1. **`main`**: Production-ready code
2. **`develop`**: Integration branch for features
3. **`feature/*`**: New features and enhancements
4. **`hotfix/*`**: Critical bug fixes
5. **`release/*`**: Release preparation

### Branch Commands

```bash
# Create and switch to feature branch
git checkout -b feature/my-feature develop

# Merge feature back to develop
git checkout develop
git merge --no-ff feature/my-feature
git branch -d feature/my-feature

# Create release branch
git checkout -b release/v2.1.0 develop

# Merge release to main
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release version 2.1.0"
```

## Code Quality Checks

### Automated Checks

Set up automated code quality checks:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run code formatting
black src/ tests/

# Run linting
flake8 src/ tests/

# Run type checking
mypy src/

# Run tests
pytest tests/
```

### Quality Configuration

#### `.flake8`
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    .venv
```

#### `pyproject.toml` (Black configuration)
```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### `mypy.ini`
```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

[mypy-tests.*]
disallow_untyped_defs = False
```

### Pre-push Hook

Create a pre-push hook for additional checks:

```bash
#!/bin/bash
# .git/hooks/pre-push

protected_branch='main'
current_branch=$(git symbolic-ref HEAD | sed 's!refs\/heads\/!!')

if [ $protected_branch = $current_branch ]; then
    echo "🚫 Direct push to main branch is not allowed"
    echo "Please create a pull request instead"
    exit 1
fi

# Run tests before push
echo "🧪 Running tests before push..."
pytest
if [ $? -ne 0 ]; then
    echo "❌ Tests failed, push aborted"
    exit 1
fi

echo "✅ Pre-push checks passed"
```

## Release Process

### Version Management

Update version information:

```bash
# Update version in _version.py
echo "__version__ = '2.1.0'" > src/_version.py

# Update version in pyproject.toml
sed -i 's/version = ".*"/version = "2.1.0"/' pyproject.toml
```

### Release Checklist

1. **Prepare Release**:
   ```bash
   # Create release branch
   git checkout -b release/v2.1.0 develop
   
   # Update version numbers
   vim src/_version.py
   vim pyproject.toml
   
   # Update CHANGELOG.md
   vim CHANGELOG.md
   ```

2. **Test Release**:
   ```bash
   # Run full test suite
   pytest
   
   # Test installation
   pip install -e .
   myconfig --version
   ```

3. **Create Release**:
   ```bash
   # Merge to main
   git checkout main
   git merge --no-ff release/v2.1.0
   
   # Create tag
   git tag -a v2.1.0 -m "Release version 2.1.0"
   
   # Push to remote
   git push origin main
   git push origin v2.1.0
   ```

### Release Notes Template

```markdown
# Release v2.1.0

## 🆕 New Features
- Template system for customizable file generation
- Compression support for backup archives
- Auto-generated backup manifests

## 🔧 Improvements  
- Enhanced CLI with preview modes
- Better error handling and logging
- Performance optimizations

## 🐛 Bug Fixes
- Fixed argument parsing issues
- Resolved permission handling bugs
- Corrected template rendering edge cases

## 🏗️ Architecture Changes
- Migrated to class-based component system
- Modularized core functionality
- Improved plugin architecture

## 📦 Dependencies
- Updated minimum Python version to 3.8
- Added template engine dependencies
- Removed deprecated dependencies

## 🔄 Migration Notes
- Configuration files remain compatible
- Plugin API has breaking changes (see migration guide)
- New template directory structure
```

### GitHub Release

Create GitHub release with:

1. **Release Title**: `v2.1.0 - Template System and Compression`
2. **Tag**: `v2.1.0`
3. **Description**: Include release notes
4. **Assets**: Include built packages

```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

For more information about contributing and development workflows, see the project's contributing guidelines.
