# Security Policy

## Supported State

The `main` branch represents the actively maintained public state of RetailPulse.

## Reporting a Vulnerability

If you discover a security issue:

1. Do not post public exploit details in issues.
2. Open a private disclosure through repository security reporting, if enabled.
3. If private reporting is unavailable, open an issue with minimal detail and request a secure contact channel.

Please include:
- Affected files or components
- Reproduction steps
- Potential impact
- Suggested mitigation (if known)

## Secrets and Credentials

- Never commit API keys, tokens, passwords, or private certificates.
- Rotate exposed credentials immediately if accidental disclosure occurs.
- Review commits and PRs for accidental secret leakage.

## Data Handling

- Avoid uploading private or regulated retail/customer datasets to public repositories.
- Use sampled, non-sensitive data for public demonstrations when possible.

## Responsible Disclosure

Please allow maintainers reasonable time to validate and fix issues before broad public disclosure.
