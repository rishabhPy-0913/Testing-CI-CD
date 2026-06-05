# Teams Webhook Setup

Configure Microsoft Teams to receive deployment success and failure notifications.

---

## Step 1 — Create Incoming Webhook in Teams

1. Open the Teams channel where you want notifications
2. Click `...` next to the channel name → **Connectors**
3. Find **Incoming Webhook** → click **Configure**
4. Enter a name: `CI/CD Alerts`
5. Optionally upload an icon
6. Click **Create**
7. **Copy the webhook URL** — you won't see it again after closing

The URL looks like:
```
https://askelie.webhook.office.com/webhookb2/xxx/IncomingWebhook/xxx/xxx
```

---

## Step 2 — Add Webhook URL to GitHub Secrets

Go to: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `TEAMS_WEBHOOK_URL` | the webhook URL from Step 1 |

---

## Step 3 — Verify it works

Test the webhook manually from your terminal:

```bash
curl -s -X POST "YOUR_WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d '{
    "@type": "MessageCard",
    "@context": "https://schema.org/extensions",
    "themeColor": "00CC00",
    "summary": "Test",
    "sections": [{ "activityTitle": "✅ Webhook connected successfully" }]
  }'
```

You should see a card appear in the Teams channel immediately.

---

## What you will receive

**Successful deployment** (green card):
```
✅ Deployment Succeeded
Version : v2026.06.05.12
Branch  : dev
Actor   : Rishabh
```

**Failed deployment with rollback** (red card):
```
❌ Deployment Failed — Rollback Triggered
Version : v2026.06.05.12
Branch  : dev
Actor   : Rishabh
Logs    : tail -50 ~/Testing-CI-CD/deploy.log on VM
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| No card in Teams | Check the webhook URL is correct in the secret |
| `400 Bad Request` from curl test | The webhook URL may have expired — recreate it in Teams |
| Notifications missing on failure | Confirm `TEAMS_WEBHOOK_URL` secret is set and the `if: failure()` step is present in the workflow |
| Connectors option missing in Teams | Teams admin may have disabled connectors — ask your Teams admin to enable them |
