# SSL Certificate Verification Configuration

This document describes SSL certificate verification settings available in `site_config.json` for Frappe Framework services that connect to external HTTPS endpoints.

## Overview

By default, Frappe Framework verifies SSL certificates when making HTTPS requests to external services. However, in some deployment scenarios (e.g., behind Traefik with self-signed certificates), you may need to disable SSL certificate verification.

> **⚠️ Security Warning**: Disabling SSL certificate verification reduces security and should only be used in controlled environments with self-signed certificates. Never disable SSL verification in production unless absolutely necessary.

## Configuration Options

### Push Notification Relay SSL Verification

**Option**: `push_relay_verify_ssl`

**Description**: Controls SSL certificate verification when connecting to the push notification relay server.

**Default**: `1` (enabled)

**Values**:
- `1` or `"1"` or `"true"`: Enable SSL certificate verification (default, recommended)
- `0` or `"0"` or `"false"`: Disable SSL certificate verification

**Example** (`site_config.json`):
```json
{
  "push_relay_server_url": "https://push.example.com",
  "push_relay_verify_ssl": 0
}
```

**Use Case**: Use when the push notification relay server uses self-signed certificates (e.g., behind Traefik reverse proxy).

---

### Frappe Mail Service SSL Verification

**Option**: `frappe_mail_verify_ssl`

**Description**: Controls SSL certificate verification when connecting to the Frappe Mail service API.

**Default**: `1` (enabled)

**Values**:
- `1` or `"1"` or `"true"`: Enable SSL certificate verification (default, recommended)
- `0` or `"0"` or `"false"`: Disable SSL certificate verification

**Example** (`site_config.json`):
```json
{
  "frappe_mail_site": "https://mail.example.com",
  "frappe_mail_verify_ssl": 0
}
```

**Use Case**: Use when the Frappe Mail service uses self-signed certificates (e.g., self-hosted Frappe Mail instance behind Traefik).

---

## Complete Example

For a deployment behind Traefik with self-signed certificates:

```json
{
  "db_name": "your_database",
  "db_password": "your_password",
  "push_relay_server_url": "https://push.example.com",
  "push_relay_verify_ssl": 0,
  "frappe_mail_verify_ssl": 0
}
```

## Implementation Details

- Both options use the `sbool()` function to parse configuration values, supporting `1/0`, `"1"/"0"`, and `"true"/"false"` formats
- If the option is not specified, SSL verification is enabled by default (`True`)
- The configuration is read from `site_config.json` using `frappe.conf.get()`
- Changes to `site_config.json` require a Frappe process restart to take effect

## Related Code

- Push Notifications: `frappe/push_notification.py` → `_send_post_request()` method
- Frappe Mail: `frappe/email/frappemail.py` → `get_client()` method

## Troubleshooting

### SSL Certificate Verification Errors

If you encounter errors like:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```

1. Verify that the external service is using a self-signed certificate
2. Add the appropriate configuration option (`push_relay_verify_ssl` or `frappe_mail_verify_ssl`) to `site_config.json`
3. Set the value to `0` to disable verification
4. Restart the Frappe processes

### Security Best Practices

1. **Use valid SSL certificates**: Whenever possible, use properly signed SSL certificates from a trusted Certificate Authority (CA)
2. **Limit scope**: Only disable SSL verification for specific services that require it
3. **Document changes**: Document why SSL verification was disabled in your deployment
4. **Monitor**: Regularly review and audit configurations that disable SSL verification
5. **Consider alternatives**: For self-signed certificates, consider adding the CA certificate to the system's trust store instead of disabling verification

