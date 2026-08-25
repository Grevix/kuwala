# Security Policy & Vulnerability Disclosure

Kuwala takes the security and integrity of its codebase and user data seriously.

---

## 1. Supported Versions

Security updates are actively provided for the following versions:

| Version | Supported | Notes |
| :--- | :--- | :--- |
| **0.1.x** | :white_check_mark: | Active Release Line |
| **< 0.1.0** | :x: | Pre-release / Deprecated |

---

## 2. Reporting a Vulnerability

If you discover a security vulnerability or potential credential exposure within Kuwala:

1. **Do NOT open a public issue** on GitHub.
2. **Email the security team**: `security@kuwala.org` (or submit a Private Vulnerability Advisory via GitHub Security Advisories).
3. **Include the following details**:
   - Description of the vulnerability or flaw.
   - Steps to reproduce or proof-of-concept script.
   - Potential impact on users or systems.

### Response Timeline
- **Initial Response**: Within 48 hours.
- **Triage & Patch**: Within 7 business days for critical issues.
- **Public Disclosure**: Coordinated disclosure after a patch is released to PyPI.

---

## 3. Credential & Data Security Rules

- **API Keys & Tokens**: Always load credentials via environment variables (`.env`). Never commit credentials to source control.
- **Data Protection**: Kuwala runs strictly client-side. No telemetry, market data, or user trading signals are transmitted to external servers.
