# SSL Certificate Setup Guide

## What is SSL?

SSL (Secure Sockets Layer) encrypts data between browser and server.

**Without SSL**: `http://yourdomain.com` ❌ (not secure)
**With SSL**: `https://yourdomain.com` ✅ (secure)

Modern browsers warn users if SSL is missing!

---

## Good News! 🎉

**SSL is AUTOMATIC on**:
- ✅ Fly.io (free, auto-generated)
- ✅ Render (free, auto-generated)
- ✅ Railway (free, auto-generated)
- ✅ PythonAnywhere (included)

**You don't need to do anything!**

---

## Check Your SSL Status

### Method 1: Browser
1. Visit your site: `https://yourdomain.com`
2. Click **🔒** lock icon
3. Click **Certificate** (or Details)
4. View certificate info

### Method 2: Online Tools
- https://www.ssllabs.com/ssltest/
- https://www.geocerts.com/ssl-checker
- Enter your domain

### Method 3: Command Line
```bash
openssl s_client -connect yourdomain.com:443 -showcerts
```

---

## For Custom Domains

When you add a custom domain to Fly.io/Render:

1. **Add domain** to your hosting
2. **Wait 24-48 hours** for DNS propagation
3. **SSL auto-generates** (usually within 1 hour)
4. **Access via HTTPS** ✅

---

## Force HTTPS (Recommended)

Redirect all HTTP traffic to HTTPS:

### Fly.io
Edit `fly.toml`:
```toml
[http_service]
  force_https = true
```

### PythonAnywhere
1. Web app settings
2. Check **Force HTTPS**

### Render
1. Service Settings
2. Auto-redirect HTTP to HTTPS: ON

---

## SSL Renewal

**Automatic!** No action needed:
- Valid for 90 days
- Auto-renews before expiry
- Works with Let's Encrypt (free certificate authority)

---

## Common SSL Issues

### "Certificate Not Trusted"
- Wait 5-10 minutes after DNS update
- Clear browser cache
- Try incognito/private mode

### "Mixed Content" Warning
- Ensure all resources load via HTTPS
- Update links in HTML from `http://` to `https://`

### "Subject Alternative Name" Missing
- Wait 1-2 hours for cert generation
- Contact your hosting provider if issue persists

---

## Verify SSL Works

Test with:
```bash
curl -I https://yourdomain.com
```

Should show:
```
HTTP/2 200
```

---

## Troubleshooting SSL

| Issue | Solution |
|-------|----------|
| No HTTPS option | Contact hosting support |
| Cert not found | Wait 24-48 hours + 1-2 hours for SSL |
| Untrusted cert | Clear cache, try private mode |
| Mixed content warning | Update HTTP to HTTPS in HTML |

---

## SSL for Development

For local testing (optional):
```bash
# Generate self-signed cert
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

Then in Flask:
```python
app.run(ssl_context=('cert.pem', 'key.pem'))
```

---

## Next Steps

1. ✅ Visit your site with `https://`
2. ✅ Click 🔒 lock icon to verify cert
3. ✅ Check certificate details
4. ✅ If using custom domain, wait 48 hours for SSL
5. ✅ Force HTTPS if available

Your site is already secure! 🔒✅
