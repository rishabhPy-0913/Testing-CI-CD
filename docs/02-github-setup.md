# GitHub Setup Guide

Everything that needs to be configured on GitHub — repository, secrets, and Actions.

---

## Prerequisites

- GitHub account with access to the repo `rishabhPy-0913/Testing-CI-CD`
- Azure Container Registry (ACR) created and admin credentials available
- VM deploy SSH private key from Step 3 of `01-vm-setup.md`

---

## Step 1 — Push the project to GitHub

From your local machine inside the project root:

```bash
git add .
git commit -m "initial ci/cd setup"
git push -u origin main
```

Verify on GitHub that all files are present:
```
Testing-CI-CD/
├── dummy-app/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .github/workflows/build-push.yml
├── scripts/
│   ├── deploy.sh
│   └── rollback.sh
├── docker-compose.yml
└── docs/
```

---

## Step 2 — Create ACR in Azure (if not done yet)

1. Go to [portal.azure.com](https://portal.azure.com)
2. Create a resource → Container Registry
3. Name: `dexninja` (becomes `dexninja.azurecr.io`)
4. SKU: **Basic**
5. Click Create

Enable admin credentials:
- Go to ACR → Settings → Access Keys
- Toggle **Admin user** ON
- Note down:
  - Login server: `dexninja.azurecr.io`
  - Username: `dexninja`
  - Password: (copy either password shown)

---

## Step 3 — Add GitHub repository secrets

Go to:
**GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

Add each secret exactly as named below:

| Secret name | Value |
|---|---|
| `ACR_LOGIN_SERVER` | `dexninja.azurecr.io` |
| `ACR_USERNAME` | `dexninja` |
| `ACR_PASSWORD` | password from ACR Access Keys page |
| `VM_SSH_HOST` | public IP address of your VM |
| `VM_SSH_USER` | `azureuser` (or your VM's SSH username) |
| `VM_SSH_KEY` | full contents of `~/.ssh/deploy_key` from the VM (the private key, including the `-----BEGIN` and `-----END` lines) |
| `GH_PAT_RISHABH` | GitHub Personal Access Token with `repo` read access |

---

## Step 4 — Verify the workflow file

Confirm `.github/workflows/build-push.yml` exists inside `dummy-app/` and the trigger is set to your branch:

```yaml
on:
  push:
    branches: [main]
```

If your default branch is `master`, change `main` to `master`.

---

## Step 5 — Enable GitHub Actions

Go to:
**GitHub repo → Settings → Actions → General**

- Set to: **Allow all actions and reusable workflows**
- Click Save

---

## Step 6 — Trigger the first pipeline run

Make a small change and push:

```bash
# Edit dummy-app/main.py — change the message in root()
git add dummy-app/main.py
git commit -m "trigger first pipeline run"
git push origin main
```

---

## Step 7 — Monitor the pipeline

Go to: **GitHub repo → Actions tab**

You will see the workflow `Build, Push & Deploy` running. Click it to see live logs for each step:

```
✓ Log — pipeline started
✓ Checkout code
✓ Generate version tag       ← e.g. v2026.06.05.1
✓ Log in to Azure Container Registry
✓ Build Docker image
✓ Push Docker image
✓ Log — build-and-push complete
✓ Log — deploy job started
✓ SSH into VM and run deploy script
✓ Log — deployment result
```

---

## Step 8 — Verify deployment succeeded

On the VM:
```bash
# App is responding
curl http://localhost/health
# {"status":"ok","version":"v2026.06.05.1"}

# Container is running
docker ps
# NAMES        IMAGE                              STATUS
# dummy-app    dexninja.azurecr.io/dummy-app:...  Up 2 minutes (healthy)

# Deploy log
tail -20 /var/log/deploy.log
# [2026-06-05 10:01:00] === Starting deployment ===
# [2026-06-05 10:01:35] Deployment successful. Running image tag: v2026.06.05.1
```

---

## GitHub is ready

Pipeline is live. Every push to `main` will build, push to ACR, and deploy to the VM automatically.  
Next: see `03-final-setup.md` for the combined checklist and rollback test.
