# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in MyConfig, please report it to kehr.dev@gmail.com.

We take security seriously and will respond to security reports within 48 hours.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.x   | ✅        |
| < 2.0   | ❌        |

## Security Features

MyConfig includes comprehensive security features designed to protect your sensitive data:

### Automatic Sensitive File Detection
- Automatically excludes SSH keys, certificates, and password files
- Configurable exclusion patterns for custom security requirements
- Smart detection of common sensitive file types and directories

### Safe Backup Process
- Preview mode to review what will be backed up before execution
- Dry-run capability to test operations without making changes
- Automatic creation of safety backups before restore operations
- Comprehensive logging for audit trails

### Data Protection
- No network connections without explicit user consent
- All operations performed locally on your system
- Configurable security policies for enterprise environments
- Support for compliance standards (SOX, GDPR, HIPAA, PCI DSS)

### Secure Configuration
- Template system prevents code injection
- Safe file path handling with validation
- Permission preservation and validation
- Integrity verification with checksums

## Security Best Practices

When using MyConfig:

1. **Review Exclusions**: Regularly review and update sensitive file exclusion patterns
2. **Use Preview Mode**: Always preview backups in sensitive environments
3. **Secure Storage**: Store backup archives in encrypted locations
4. **Access Control**: Limit backup access to authorized users only
5. **Regular Audits**: Review backup logs and excluded files periodically

## Security Configuration

For enhanced security, configure custom exclusion patterns:

```toml
[security]
skip_sensitive = true
exclude_patterns = [
    ".*\\.key$",
    ".*\\.pem$",
    ".*password.*",
    ".*secret.*",
    "company-confidential/.*"
]
```

## Compliance

MyConfig supports security compliance requirements:
- **Audit Logging**: Comprehensive operation logging
- **Data Classification**: Automatic sensitive data detection
- **Access Controls**: Configurable security policies
- **Integrity Verification**: Backup validation and checksums

For detailed security information, see [docs/security.md](docs/security.md).

## Contact

For security-related questions or concerns:
- Email: kehr.dev@gmail.com
- GitHub Issues: Use for non-sensitive security discussions
- Private Communication: For sensitive security reports, use email

Thank you for helping keep MyConfig secure!
