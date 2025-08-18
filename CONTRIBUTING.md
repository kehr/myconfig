# Contributing to MyConfig

Thank you for your interest in contributing to MyConfig! We welcome contributions from the community and are excited to see what you'll bring to the project.

## How to Contribute

### 1. Ways to Contribute

- **🐛 Bug Reports**: Found a bug? Let us know!
- **💡 Feature Requests**: Have an idea for a new feature?
- **Documentation**: Help improve our documentation
- **Code Contributions**: Submit bug fixes or new features
- **Templates**: Contribute new template designs
- **Plugins**: Create plugins for additional functionality

### 2. Getting Started

#### Fork and Clone
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/myconfig.git
cd myconfig

# Add upstream remote
git remote add upstream https://github.com/kehr/myconfig.git
```

#### Development Setup
```bash
# Install in development mode
pip install -e ".[dev]"

# Or install manually
pip install -e .

# Verify installation
myconfig --version
myconfig doctor
```

#### Development Dependencies
```bash
# Install development tools (optional)
pip install black flake8 mypy pytest
```

### 3. Development Workflow

#### Create a Feature Branch
```bash
# Update your fork
git checkout main
git pull upstream main

# Create a new branch
git checkout -b feature/amazing-feature
```

#### Make Your Changes
- Write clean, readable code
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

#### Test Your Changes
```bash
# Run basic tests
python -m py_compile myconfig/**/*.py

# Test functionality
myconfig --dry-run export test-backup
myconfig --preview export test-backup

# Run with verbose logging
myconfig -v doctor
```

#### Commit Your Changes
```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add amazing new feature

- Implement feature X with Y functionality
- Add comprehensive tests and documentation
- Update configuration examples"
```

## 📝 Code Standards

### Python Style Guidelines
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to new functions and classes
- Keep line length under 88 characters (Black default)

### Code Structure
- Use the existing modular architecture
- Add new components to `myconfig/core/components/`
- Follow the `BackupComponent` interface for new backup types
- Use the centralized logging system

### Example Code Structure
```python
import logging
from typing import Dict, Any
from ..base import BackupComponent
from ..executor import CommandExecutor

class MyNewComponent(BackupComponent):
    """Description of what this component does."""
    
    def __init__(self, config: Dict[str, Any], executor: CommandExecutor):
        super().__init__("my-component", config, executor)
        self.logger = logging.getLogger(__name__)
    
    def can_backup(self) -> bool:
        """Check if this component can perform backup."""
        return self.executor.which("required-tool") is not None
    
    def backup(self, output_dir: str) -> bool:
        """Perform the backup operation."""
        try:
            # Implementation here
            self.logger.info("Backup completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
```

### Commit Message Format
Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or fixing tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```bash
feat(core): add PostgreSQL backup component
fix(cli): resolve argument parsing for --compress flag
docs: update installation guide with troubleshooting
style: format code with Black
refactor(utils): improve error handling in file operations
```

##  Testing Guidelines

### Manual Testing
```bash
# Test basic functionality
myconfig --help
myconfig doctor
myconfig --preview export test-backup

# Test with different configurations
myconfig profile use minimal
myconfig --dry-run export minimal-test

# Test restore functionality
myconfig --preview restore test-backup
```

### Test New Components
- Test with and without required dependencies
- Test error handling and edge cases
- Verify security exclusions work correctly
- Test with different macOS versions when possible

## 📖 Documentation

### Update Documentation
When adding new features:
- Update relevant documentation in `docs/`
- Add usage examples
- Update configuration references
- Add security considerations if applicable

### Documentation Style
- Use clear, concise language
- Include practical examples
- Organize with clear headings and structure
- Test all code examples

##  Security Considerations

### Security Guidelines
- Never commit sensitive data (keys, passwords, etc.)
- Follow the existing sensitive file detection patterns
- Test security exclusions with your changes
- Document any security implications

### Security Testing
```bash
# Test sensitive file detection
echo "password123" > test-password.txt
myconfig --preview export test-backup
# Verify password file is excluded

# Clean up
rm test-password.txt
```

##  Pull Request Process

### Before Submitting
1. **Update your branch** with latest upstream changes
2. **Test thoroughly** on your local system
3. **Update documentation** if needed
4. **Run pre-commit checks** (if available)

### Pull Request Guidelines
- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Link issues** that the PR addresses
- **Screenshots** for UI changes (if applicable)
- **Test instructions** for reviewers

### Pull Request Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tested on macOS [version]
- [ ] Manual testing completed
- [ ] Documentation updated

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No sensitive data included
```

##  Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different opinions and approaches

### Getting Help
- **Documentation**: Check `docs/` directory first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Email**: kehr.dev@gmail.com for private questions

### Recognition
Contributors will be:
- Added to the contributors list
- Mentioned in release notes for significant contributions
- Given credit in documentation for major features

##  Issue Guidelines

### Bug Reports
Include:
- MyConfig version (`myconfig --version`)
- macOS version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output

### Feature Requests
Include:
- Clear description of the feature
- Use case and motivation
- Possible implementation approach
- Any security considerations

## 🎉 First-Time Contributors

Welcome! Here are some good first issues:
- Documentation improvements
- Adding new defaults domains
- Creating new template designs
- Improving error messages
- Adding configuration examples

Don't hesitate to ask questions in issues or discussions!

## 📞 Contact

- **Project Maintainer**: Kyle (kehr.dev@gmail.com)
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community discussion

Thank you for contributing to MyConfig! 🙏
