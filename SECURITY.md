# Security Policy

## Supported Versions

The following versions of the API Gateway are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Yes             |
| 0.x.x   | ⚠️ End of Life    |

## Reporting a Vulnerability

If you discover a security vulnerability within the API Gateway, please send an e-mail to the maintainers. All security vulnerabilities will be promptly addressed.

Please include the following information:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Best Practices

### Authentication

- All endpoints (except `/auth/v1/login`, `/auth/v1/login-badge`) require JWT authentication
- Tokens are validated by the Security API
- Use secure token storage on client side

### Request Validation

- Request size is limited to 10MB by default
- Content-Type validation is enforced
- JSON structure validation returns 400 for malformed requests

### CORS Configuration

For production deployments, configure specific allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Not "*"
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Environment Variables

Ensure production environment variables are properly secured:

- Do not commit `.env` files to version control
- Use secrets management for API keys and URLs
- Rotate credentials periodically

```env
# Example production configuration
URL_BACKEND=https://backend-production:8000
SECURITY_API_URL=https://security-api-production:8000
CHECK_UPSTREAM_SERVICES=true
```

### Logging Security

- Avoid logging sensitive data (passwords, tokens, PII)
- Logs are written in JSON format for security monitoring
- Monitor log files for suspicious activity

### Network Security

- Run behind a load balancer or API gateway in production
- Use HTTPS for all external traffic
- Implement rate limiting at the infrastructure level
- Restrict access to internal services

### Dependencies

Keep dependencies up to date to receive security patches:

```bash
pip install --upgrade -r requirements.txt
```

## Security Headers

The gateway includes the following security features:

- `X-Request-ID` for request tracing
- Standard error response format for consistent error handling
- No sensitive data exposure in error messages

## Incident Response

In case of a security incident:

1. **Acknowledge** the report within 24 hours
2. **Assess** the vulnerability and its impact
3. **Develop** a fix and test it
4. **Release** the fix with a security advisory
5. **Communicate** with users about the vulnerability and fix

## Third-Party Security

This project uses the following third-party libraries:

- **FastAPI** - Web framework
- **HTTPX** - HTTP client
- **Pydantic** - Data validation
- **Prometheus Client** - Metrics

Ensure you monitor and update these dependencies for security vulnerabilities.

## Compliance

For specific compliance requirements (GDPR, SOC2, etc.), please contact the maintainers.

---

Thank you for helping keep the API Gateway secure!
