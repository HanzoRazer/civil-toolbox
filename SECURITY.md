# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.x (current development) | Yes |

---

## Reporting Vulnerabilities

### Security Vulnerabilities

Report traditional security vulnerabilities (injection, authentication bypass, data exposure) to:

**thetexasguitarexchange@gmail.com**

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 7 days
- **Resolution target**: Depends on severity

---

## Engineering Safety Issues

Civil Toolbox is engineering software. Calculation errors can have real-world consequences.

**Calculation errors that could materially affect engineering conclusions should be reported as safety-sensitive defects, even if they are not traditional cybersecurity vulnerabilities.**

### Examples of Safety-Sensitive Defects

- Incorrect formula implementation
- Unit conversion errors
- Missing input validation that allows unrealistic values
- Silent failures that produce plausible but wrong results
- Boundary condition errors

### Reporting Safety Issues

Report safety-sensitive calculation defects to the same email:

**thetexasguitarexchange@gmail.com**

Include:

- The calculation or method affected
- Input values that trigger the issue
- Expected vs actual output
- Reference or hand calculation showing the correct value
- Potential engineering impact

---

## Responsible Disclosure

- Do not publicly disclose serious vulnerabilities or calculation defects before maintainers have had time to review and address them.
- Coordinate disclosure timing with maintainers.
- Credit will be given to reporters in release notes (unless anonymity is preferred).

---

## Non-Security Bugs

Bugs that do not affect security or calculation correctness should be reported through GitHub Issues, not this security process.

Examples of non-security bugs:

- UI display issues
- Performance problems
- Documentation errors
- Feature requests
