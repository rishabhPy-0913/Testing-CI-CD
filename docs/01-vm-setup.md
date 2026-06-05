# VM Setup Guide

Everything that needs to be done on the VM — one time only.  
No file copying needed — the repo has everything, just clone it.

---

## Prerequisites

- A running Ubuntu 22.04 VM
- Port **22** (SSH) and **80** (app) open in firewall / security group
- You can SSH into it as a user with sudo access

---

## Step 1 — SSH into the VM

```bash
ssh -i ~/.ssh/your-key.pem azureuser@<VM-PUBLIC-IP>
```

---

## Step 2 — Install Docker and Git

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin curl git
sudo usermod -aG docker $USER
newgrp docker
```

Verify:
```bash
docker --version
docker compose version
```

---

## Step 3 — Generate a deploy SSH key pair

This key is what GitHub Actions will use to SSH into the VM:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key -N ""
cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Copy the private key — you will paste this into the GitHub secret `VM_SSH_KEY`:
```bash
cat ~/.ssh/deploy_key
```

---

## Step 4 — Clone the repo

Store your GitHub PAT as an env variable first — never hardcode it in any file:

```bash
echo 'export GH_PAT_RISHABH="ghp_xxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

Then clone using the token from the env variable:

```bash
git clone https://$GH_PAT_RISHABH@github.com/rishabhPy-0913/Testing-CI-CD.git
```

Cache credentials so future `git pull` calls inside deploy scripts work without a token:

```bash
git config --global credential.helper store
cd Testing-CI-CD && git pull
```

The repo already contains everything needed:
```
~/Testing-CI-CD/
├── scripts/
│   ├── deploy.sh
│   └── rollback.sh
├── docker-compose.yml
└── dummy-app/
```

Make the scripts executable:
```bash
chmod +x ~/Testing-CI-CD/scripts/deploy.sh ~/Testing-CI-CD/scripts/rollback.sh
```

---

## Step 5 — Log the VM into ACR

```bash
docker login <your-acr>.azurecr.io -u <acr-username> -p <acr-password>
```

---

## Step 7 — Verify everything is in place

```bash
ls ~/Testing-CI-CD/scripts/
# deploy.sh  rollback.sh

ls ~/Testing-CI-CD/
# docker-compose.yml  dummy-app  scripts  docs  ...

ls ~/Testing-CI-CD/deploy.log 2>/dev/null || echo "created on first deploy run"
```

---

## On future deploys

GitHub Actions will SSH in and run:
```bash
bash ~/Testing-CI-CD/scripts/deploy.sh
```

No manual pulls needed — `deploy.sh` handles everything from there.

---

## VM is ready

Next: complete the GitHub setup → see `02-github-setup.md`
