# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in AIVersus, please report it responsibly:

1. **Email**: Open an issue on the [GitHub repository](https://github.com/Godstaf/AIVersus/issues) with the label `security`
2. **Do not** disclose the vulnerability publicly until it has been addressed

## Security Best Practices

When deploying AIVersus:

- **Never commit your `.env` file** — it contains API keys and database passwords
- **Change the default database password** in `docker-compose.yml` for production deployments
- **Use HTTPS** behind a reverse proxy (e.g., Nginx) in production
- **Keep dependencies updated** — run `pip install --upgrade` periodically
