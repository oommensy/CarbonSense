# 🚀 Contributing to CarbonSense

Welcome to the CarbonSense community! We're building the future of climate action tracking, and we'd love your help.

## 🌍 Our Mission

Empower individuals and corporations to make measurable climate impact through data-driven action tracking and community engagement.

## 🤝 How to Contribute

### 🐛 Bug Reports
- Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include screenshots, logs, and reproduction steps
- Check existing issues to avoid duplicates

### ✨ Feature Requests
- Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Explain the use case and expected behavior
- Consider both individual and corporate user needs

### 💻 Code Contributions
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

## 🏗️ Development Setup

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.9+ and pip
- PostgreSQL 14+
- Redis 6+
- Git

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/carbonsense.git
cd carbonsense

# Install dependencies
npm install
pip install -r backend/requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your local configuration

# Start development servers
npm run dev
```

## 📝 Code Standards

### TypeScript/JavaScript
- Use TypeScript for all new code
- Follow ESLint and Prettier configurations
- Write unit tests for new features
- Document complex functions with JSDoc

### Python
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for all public functions
- Include unit tests with pytest

### Commit Messages
Follow [Conventional Commits](https://conventionalcommits.org/):
```
feat: add carbon offset marketplace
fix: resolve GPS tracking accuracy issue
docs: update API documentation
style: format code with prettier
refactor: optimize database queries
test: add unit tests for user service
```

## 🧪 Testing Guidelines

### Frontend Testing
- **Unit Tests**: Jest and React Testing Library
- **Integration Tests**: Cypress for E2E testing
- **Coverage**: Maintain >80% test coverage

### Backend Testing
- **Unit Tests**: pytest with fixtures
- **API Tests**: FastAPI TestClient
- **Database Tests**: Test database with transactions

### Running Tests
```bash
# Frontend tests
npm test
npm run test:e2e

# Backend tests
pytest
pytest --cov=app

# Full test suite
npm run test:all
```

## 🎨 Design Guidelines

### UI/UX Principles
- **Mobile-First**: Design for mobile, enhance for desktop
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Fast loading times and smooth animations
- **Sustainability**: Dark mode and energy-efficient design

### Brand Guidelines
- **Colors**: Earth tones with vibrant accent colors
- **Typography**: Clean, readable fonts with good contrast
- **Icons**: Consistent icon style throughout the app
- **Imagery**: High-quality photos that inspire climate action

## 📊 Pull Request Process

### Before Submitting
- [ ] Code follows project standards
- [ ] All tests pass locally
- [ ] Documentation is updated
- [ ] No merge conflicts with main branch

### PR Checklist
- [ ] Clear description of changes
- [ ] Screenshots for UI changes
- [ ] Links to related issues
- [ ] Reviewer assigned

### Review Process
1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainer reviews code quality
3. **Testing**: Feature is tested manually
4. **Approval**: Two approvals required for merge

## 🏷️ Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements to docs |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `priority:high` | Critical issue |
| `mobile` | Mobile app related |
| `web` | Web dashboard related |
| `backend` | API/server related |
| `ml` | Machine learning related |

## 🌟 Recognition

### Contributors
All contributors are recognized in our:
- GitHub Contributors page
- Monthly newsletter
- Annual sustainability report
- Conference presentations

### Maintainers
Active contributors may be invited to become maintainers with:
- Commit access to the repository
- Influence on roadmap decisions
- Speaking opportunities at events
- Climate action swag and rewards

## 📞 Getting Help

### Communication Channels
- **Discord**: [CarbonSense Community](https://discord.gg/carbonsense)
- **Discussions**: GitHub Discussions for questions
- **Email**: developers@carbonsense.com
- **Office Hours**: Fridays 2-4 PM EST

### Mentorship Program
New contributors can request mentorship for:
- First-time contributions
- Complex feature development
- Career guidance in climate tech
- Open source best practices

## 🎯 Areas of Contribution

### High-Impact Areas
- **AI/ML Models**: Improve carbon footprint predictions
- **Data Integrations**: Add new satellite or IoT data sources
- **Mobile Performance**: Optimize app performance and battery usage
- **Corporate Features**: Build enterprise dashboard components
- **Accessibility**: Improve app accessibility for all users

### Good First Issues
- Documentation improvements
- UI component creation
- Test coverage expansion
- Bug fixes and performance optimizations
- Translation and internationalization

## 📈 Roadmap Participation

Contributors can influence our roadmap through:
- **Feature voting** in GitHub Discussions
- **Quarterly planning** sessions (open to all)
- **User research** participation
- **Beta testing** new features

## 🌱 Sustainability Commitment

As a climate-focused project, we commit to:
- **Carbon-neutral development**: Offset all development energy usage
- **Sustainable practices**: Efficient code, optimized resources
- **Community impact**: Support environmental causes through the project
- **Education**: Share climate knowledge and best practices

---

**Thank you for contributing to a more sustainable future! 🌍💚**

Every line of code you write helps millions of people take meaningful climate action.