# Final Setup & Rollback Test Guide

Combined checklist to confirm everything is wired up, followed by a step-by-step rollback test.

---

## Pre-flight Checklist

Complete both guides before starting this one.

### VM
- [ ] Docker and docker-compose-plugin installed
- [ ] Deploy SSH key generated, public key added to `authorized_keys`
- [ ] `/opt/scripts/deploy.sh` and `rollback.sh` present and executable
- [ ] `/opt/deployment/docker-compose.yml` present
- [ ] `/var/log/deploy.log` exists and is writable
- [ ] VM logged into ACR (`docker login`)
- [ ] Port 80 open in firewall / security group

### GitHub
- [ ] Code pushed to `rishabhPy-0913/Testing-CI-CD` on branch `main`
- [ ] All 6 secrets added: `ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`, `VM_SSH_HOST`, `VM_SSH_USER`, `VM_SSH_KEY`
- [ ] GitHub Actions enabled on the repo
- [ ] `.github/workflows/build-push.yml` visible in the repo

---

## Phase 1 — Deploy v1 (stable baseline)

**1. Confirm `FORCE_UNHEALTHY` is false in docker-compose.yml on the VM:**
```bash
grep FORCE_UNHEALTHY ~/Testing-CI-CD/docker-compose.yml
# - FORCE_UNHEALTHY=false
```

**2. Push any change to trigger the pipeline:**
```bash
# On your local machine
git commit --allow-empty -m "deploy v1 baseline"
git push origin main
```

**3. Watch Actions tab on GitHub — all steps should go green.**

**4. Verify on the VM:**
```bash
curl http://localhost/health
# {"status":"ok","version":"v2026.06.05.1"}

docker ps
# dummy-app   dexninja.azurecr.io/dummy-app:v2026.06.05.1   Up (healthy)

cat /opt/deployment/.previous_version
# v2026.06.05.1
```

**v1 is live and the version file is written. This is your rollback baseline.**

---

## Phase 2 — Deploy v2 (intentional failure — rollback test)

**5. Simulate a broken deployment — set `FORCE_UNHEALTHY=true` on the VM:**
```bash
sudo nano ~/Testing-CI-CD/docker-compose.yml
```
Change:
```yaml
- FORCE_UNHEALTHY=true
```
Save and exit.

**6. Push a change to trigger v2 deployment:**
```bash
# On your local machine — make any edit to dummy-app/main.py
git add dummy-app/main.py
git commit -m "deploy v2 - broken build for rollback test"
git push origin main
```

**7. Watch Actions tab — the deploy job will turn red (expected).**

The pipeline SSH'd into the VM, started v2, health check hit `/health` → got 500 ten times → triggered `rollback.sh`.

---

## Phase 3 — Verify rollback succeeded

**8. Check the deploy log on the VM:**
```bash
tail -60 /var/log/deploy.log
```

You should see:
```
[2026-06-05 10:05:00] === Starting deployment ===
[2026-06-05 10:05:01] Current running image tag: v2026.06.05.1
[2026-06-05 10:05:10] Deploying new container...
[2026-06-05 10:05:20] Health check attempt 1/10...
[2026-06-05 10:05:26] Health check attempt 2/10...
...
[2026-06-05 10:06:50] Health check failed after 10 attempts.
[2026-06-05 10:06:50] Deployment unhealthy. Triggering rollback...
[2026-06-05 10:06:50] [ROLLBACK] === Starting rollback ===
[2026-06-05 10:06:50] [ROLLBACK] Rolling back to image tag: v2026.06.05.1
[2026-06-05 10:06:55] [ROLLBACK] Health check passed.
[2026-06-05 10:06:55] [ROLLBACK] Rollback to v2026.06.05.1 successful.
```

**9. Confirm the app is still serving traffic on v1:**
```bash
curl http://localhost/health
# {"status":"ok","version":"v2026.06.05.1"}

docker ps
# dummy-app   dexninja.azurecr.io/dummy-app:v2026.06.05.1   Up (healthy)
```

**10. Confirm the compose file was restored to `latest`:**
```bash
grep image ~/Testing-CI-CD/docker-compose.yml
# image: dexninja.azurecr.io/dummy-app:latest
```

---

## Phase 4 — Fix and re-deploy cleanly

**11. Revert `FORCE_UNHEALTHY` back to false on the VM:**
```bash
sudo nano ~/Testing-CI-CD/docker-compose.yml
```
Change back:
```yaml
- FORCE_UNHEALTHY=false
```

**12. Push a fix commit:**
```bash
git commit --allow-empty -m "fix: revert broken build - deploy v3"
git push origin main
```

**13. Watch Actions — all green. Verify on VM:**
```bash
curl http://localhost/health
# {"status":"ok","version":"v2026.06.05.3"}

cat /opt/deployment/.previous_version
# v2026.06.05.3
```

---

## Summary — What was tested

| Scenario | Result |
|---|---|
| First deploy (no previous version) | Fresh install, `.previous_version` written |
| Healthy deploy (v1 → v2 passing) | Container updated, version file updated |
| Broken deploy (v2 → v3 failing health check) | Auto-rollback to v2, compose file restored |
| Fixed deploy after rollback (v3 clean) | Deployed cleanly, new baseline set |

---

## Ongoing — every push to main

```
git push origin main
      │
      ▼
GitHub Actions builds image → tags v2026.MM.DD.N + latest → pushes to ACR
      │
      ▼
SSH into VM → deploy.sh → health check
      ├─ PASS  → live ✓
      └─ FAIL  → rollback to previous stable version automatically
```

No manual steps required after initial setup.
