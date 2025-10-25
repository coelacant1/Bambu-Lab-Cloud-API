# Contributing to Bambu Lab Cloud API

Thank you for your interest in contributing to this project! This guide will help you get started.

## How to Contribute

### Reporting Issues
- Search existing issues before creating a new one
- Provide clear reproduction steps
- Include API responses, error messages, and relevant code snippets
- Specify your Python version, printer model, and firmware version

### Suggesting Enhancements
- Check if the feature already exists in the documentation
- Describe the use case and expected behavior
- Provide examples of how the feature would be used

## Development Workflow

### 1. Fork and Clone
```bash
git clone https://github.com/YOUR_USERNAME/Bambu-Lab-Cloud-API.git
cd Bambu-Lab-Cloud-API
```

### 2. Set Up Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 4. Make Your Changes
- Follow the existing code style and structure
- Add docstrings to new functions/classes
- Update documentation if adding/modifying API endpoints
- Keep changes focused and atomic

### 5. Test Your Changes
Run the comprehensive test suite:
```bash
cd tests/
python test_comprehensive.py
```

Test specific components:
```bash
python test_mqtt.py        # MQTT functionality
python test_cloud_api.py   # Cloud API calls
python test_ftp.py         # FTP uploads
```

### 6. Commit Your Changes
Write clear, descriptive commit messages:
```bash
git commit -m "Add support for XYZ endpoint"
git commit -m "Fix temperature parsing in MQTT data"
git commit -m "Update documentation for camera streaming"
```

### 7. Submit a Pull Request
- Push your branch to your fork
- Create a pull request with a clear title and description
- Reference any related issues
- Wait for review and address feedback

## Code Style

### Python
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Keep functions focused on a single responsibility
- Add type hints where appropriate
- Use 4 spaces for indentation

### Documentation
- Update API documentation files (API_*.md) for new endpoints
- Include request/response examples with real data structure
- Document all parameters and return values
- Keep README.md up to date with new features

### File Organization
- **bambulab/**: Core API implementation
- **tests/**: Test scripts and utilities
- **docs/**: API documentation (if separate from root)
- **API_*.md**: Endpoint documentation with examples

## API Discovery Process

When documenting new endpoints:
- Include full request/response examples
- Document all known parameters
- Note any version-specific behavior
- Sanitize all personal identifiers

## Code of Conduct

- Be respectful and constructive
- Help others learn and grow
- Focus on what's best for the community
- Welcome newcomers and diverse perspectives

## Questions?

- Open an issue for general questions
- Check existing documentation and issues first
- Join discussions in open issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
