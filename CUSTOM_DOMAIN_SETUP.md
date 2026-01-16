# Custom Domain Setup Guide

## What is a Custom Domain?

Instead of `mgbric.fly.dev`, use your own domain like `mgbric.com` or `tournaments.yoursite.com`

---

## Option 1: Fly.io Custom Domain

### Step 1: Get Your Domain
- Buy from: GoDaddy, Namecheap, Google Domains, etc.
- Cost: ~$10-15/year

### Step 2: Add Domain to Fly.io

```bash
flyctl certs create yourdomain.com
flyctl certs create www.yourdomain.com
```

### Step 3: Update DNS Records

Fly.io will show you nameservers. In your domain registrar:

1. Go to DNS settings
2. Change nameservers to Fly.io's
3. Wait 24-48 hours for propagation

### Verify It Works
```bash
flyctl certs show yourdomain.com
```

---

## Option 2: PythonAnywhere Custom Domain

### Step 1: Buy Domain
Same as above

### Step 2: Configure in PythonAnywhere

1. Login to PythonAnywhere
2. Go to **Web** tab
3. Find your app
4. Scroll to **Web app security**
5. Add your domain

### Step 3: Update DNS

**In your domain registrar**, add A record:

```
Type: A
Name: @ (or yourdomain.com)
Value: 82.94.136.177 (PythonAnywhere IP - check current in docs)
TTL: 3600
```

For www subdomain:
```
Type: CNAME
Name: www
Value: yourdomain.com
```

### Step 4: Force HTTPS

In PythonAnywhere:
- Web app settings
- Check **Force HTTPS**

---

## Option 3: Railway/Render Custom Domain

### Railway

1. Dashboard → Your app → Settings
2. Custom Domain → Add domain
3. Follow DNS instructions
4. SSL auto-generates

### Render

1. Dashboard → Your service
2. Settings → Custom Domain
3. Add your domain
4. Follow DNS guide

---

## Step-by-Step: GoDaddy Example

1. **Buy domain**: godaddy.com → Search → Buy
2. **Get DNS info from Fly.io**: `flyctl certs create yourdomain.com`
3. **In GoDaddy**:
   - My Products → Domains
   - Click your domain
   - DNS → Nameservers → Change
   - Enter Fly.io nameservers
4. **Wait 24-48 hours**
5. **Verify**: `nslookup yourdomain.com`

---

## Common DNS Records

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| A | @ | IP address | Main domain |
| CNAME | www | yourdomain.com | www subdomain |
| MX | @ | mail server | Email (if needed) |
| TXT | @ | verification code | SSL verification |

---

## Troubleshooting

### Domain Not Working
- Check DNS propagation: `nslookup yourdomain.com`
- May take 24-48 hours
- Try different DNS checker: mxtoolbox.com

### SSL Certificate Error
- Wait 5-10 minutes after DNS update
- Clear browser cache
- Try HTTPS again

### Subdomain Not Working
- Ensure CNAME record is correct
- Check TTL (should be 3600 or less)

---

## Costs

- Domain: $10-15/year
- SSL: FREE (auto-generated)
- Hosting: FREE (Fly.io) or $5+/month (other services)

---

## Next Steps

1. Choose domain registrar
2. Buy domain
3. Add to your hosting (Fly.io, PythonAnywhere, etc.)
4. Update DNS records
5. Wait for propagation
6. Visit your custom domain! ✅

**Popular registrars**:
- GoDaddy: godaddy.com
- Namecheap: namecheap.com
- Google Domains: domains.google.com
- Route53: aws.amazon.com
