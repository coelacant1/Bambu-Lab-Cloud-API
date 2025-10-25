# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, report them via:
- **Email:** Create a security advisory through GitHub's private vulnerability reporting
- **GitHub:** Use the "Security" tab -> "Report a vulnerability"

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial response:** Within 48 hours
- **Status update:** Within 7 days
- **Fix timeline:** Varies by severity

## Security Best Practices

### Token Management

**DO:**
- Store tokens in config files (gitignored)
- Use environment variables for production
- Rotate tokens regularly

**DON'T:**
- Commit tokens to repositories
- Share tokens in public channels
- Hardcode tokens in source code
- Log tokens in application logs

### Proxy Server Usage
- **Strict mode (port 5001):** Read-only operations - recommended for untrusted environments
- **Full mode (port 5003):** Complete access - use only in secure, controlled environments
- Always use custom token mapping to avoid exposing real Bambu Lab tokens

### API Rate Limiting

- Respect Bambu Lab's API rate limits
- Implement exponential backoff for retries
- Cache responses when appropriate

### Local Network Security

- MQTT and local FTP use access codes - treat these as passwords
- Use TLS/SSL when available
- Isolate printer network when possible

## Known Considerations

- **Developer Mode Removal:** This library uses Cloud API as Bambu Lab removed local developer mode
- **Access Codes:** Local printer access codes provide full control - protect them
- **MQTT:** Messages may contain sensitive printer information

## Scope

This project documents public API endpoints. Security issues should focus on:
- Authentication handling in the library
- Token exposure risks
- Server proxy vulnerabilities
- Dependency vulnerabilities

Out of scope:
- Vulnerabilities in Bambu Lab's services (report to Bambu Lab directly)
- Physical printer security

---

**Last Updated:** October 2025
