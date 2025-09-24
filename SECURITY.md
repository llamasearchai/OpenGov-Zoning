# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please follow these steps:

### Private Disclosure Process

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. **Email us directly** at: nikjois@llamasearch.ai
3. **Include detailed information** about the vulnerability:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
   - Your name/handle (for credit in our security acknowledgments)

### What to Expect

- **Response time**: We will acknowledge receipt within 24 hours
- **Investigation**: We will investigate the issue within 72 hours
- **Resolution**: We will work to resolve the issue as quickly as possible
- **Disclosure**: We will coordinate public disclosure with you

### Security Acknowledgments

We would like to thank the following individuals for responsibly disclosing security vulnerabilities:

- *None yet - be the first!*

## Security Best Practices

### For Users

1. **Keep dependencies updated**: Regularly update your dependencies using `pip install --upgrade -r requirements.txt`
2. **Use environment variables**: Never commit secrets to version control
3. **Enable HTTPS**: Always use HTTPS in production
4. **Monitor logs**: Regularly review application logs for suspicious activity
5. **Use rate limiting**: Configure appropriate rate limits for your use case

### For Developers

1. **Follow secure coding practices**: Always validate input and use parameterized queries
2. **Use HTTPS**: Always use HTTPS for all endpoints in production
3. **Implement proper authentication**: Use strong authentication mechanisms
4. **Keep secrets secure**: Use environment variables or secure secret management systems
5. **Regular security audits**: Run security scans regularly using the provided tools

## Security Tools

This project includes several security tools that are automatically run:

- **Bandit**: Static Application Security Testing (SAST)
- **Safety**: Dependency vulnerability scanning
- **CodeQL**: Code analysis for security vulnerabilities
- **Dependabot**: Automated dependency updates

### Running Security Scans Locally

```bash
# Install security tools
pip install bandit safety

# Run security scans
bandit -r src/
safety check

# Run tests with security markers
pytest -m security
```

## Contact

- **Security Email**: nikjois@llamasearch.ai
- **Project Homepage**: https://github.com/llamasearchai/OpenGov-Zoning
- **Documentation**: https://llamasearchai.github.io/OpenGov-Zoning

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.