# Production Webhook Server Deployment on Windows

## Using Task Scheduler

```powershell
# 1. Set webhook secret
$env:GITHUB_WEBHOOK_SECRET = '1440e61bb914225c5e80bb0e5aba7fec'

# 2. Create scheduled task
$action = New-ScheduledTaskAction -Execute "C:\Python310\python.exe" -Argument "C:\path\to\BRIC\webhook_server.py"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName "GitHub-Webhook-Server" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Description "GitHub Webhook Server for auto-updates"

# 3. Start service
Start-ScheduledTask -TaskName "GitHub-Webhook-Server"

# 4. Check logs
Get-EventLog -LogName System | Where-Object {$_.Source -eq "Task Scheduler"}
```

## Using NSSM (Non-Sucking Service Manager)

```powershell
# Download NSSM from: https://nssm.cc/download

# 1. Install NSSM service
nssm install GitHub-Webhook-Server "C:\Python310\python.exe" "C:\path\to\BRIC\webhook_server.py"

# 2. Set environment variable
nssm set GitHub-Webhook-Server AppEnvironmentExtra GITHUB_WEBHOOK_SECRET=1440e61bb914225c5e80bb0e5aba7fec

# 3. Set working directory
nssm set GitHub-Webhook-Server AppDirectory "C:\path\to\BRIC"

# 4. Start service
nssm start GitHub-Webhook-Server

# 5. View logs
nssm query GitHub-Webhook-Server
```

## Using Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location /webhook {
        proxy_pass http://localhost:5000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 30s;
    }
}
```

## Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY webhook_server.py .
COPY vugraph_fetcher.py .
COPY auto_update_vugraph.py .

ENV GITHUB_WEBHOOK_SECRET=your-secret-here
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["python", "webhook_server.py"]
```

```bash
# Build and run
docker build -t github-webhook-server .
docker run -d -p 5000:5000 \
    -e GITHUB_WEBHOOK_SECRET=your-secret \
    -v /path/to/repo:/app/repo \
    github-webhook-server
```

## Troubleshooting

### Service won't start
```powershell
# Check Event Viewer
Get-EventLog -LogName System -Source "Task Scheduler" | Select-Object TimeGenerated, Message | Format-List

# Or with NSSM
nssm query GitHub-Webhook-Server Events
```

### Connection refused
```
Check if port 5000 is open: netstat -ano | findstr :5000
Check firewall: netsh advfirewall firewall show rule name="Python"
```

### Python module not found
```
Make sure virtual environment is activated
Check PYTHONPATH environment variable
```
