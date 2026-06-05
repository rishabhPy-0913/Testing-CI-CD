import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(16, 26))
ax.set_xlim(0, 16)
ax.set_ylim(0, 26)
ax.axis('off')
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')

# ── colour palette ──────────────────────────────────────────────────────────
C_GITHUB   = '#238636'   # green  – GitHub / Actions
C_ACR      = '#1f6feb'   # blue   – ACR
C_VM       = '#6e40c9'   # purple – VM / deploy
C_HEALTH   = '#e3b341'   # yellow – health check
C_ROLLBACK = '#da3633'   # red    – rollback
C_SUCCESS  = '#238636'   # green  – success
C_CRITICAL = '#b91c1c'   # dark red – critical
C_DECISION = '#c9a227'   # amber  – decision diamonds
C_TEXT     = '#f0f6fc'
C_SUBTEXT  = '#8b949e'
C_BORDER   = '#30363d'


def box(ax, x, y, w, h, label, sublabel='', color='#161b22', border=C_BORDER,
        text_color=C_TEXT, radius=0.3, fontsize=11):
    patch = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle=f"round,pad=0.05,rounding_size={radius}",
                           facecolor=color, edgecolor=border, linewidth=1.8, zorder=3)
    ax.add_patch(patch)
    if sublabel:
        ax.text(x, y + 0.18, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)
        ax.text(x, y - 0.28, sublabel, ha='center', va='center',
                fontsize=8.5, color=C_SUBTEXT, zorder=4)
    else:
        ax.text(x, y, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)


def diamond(ax, x, y, w, h, label, color=C_DECISION, text_color='#0d1117', fontsize=9.5):
    dx, dy = w/2, h/2
    pts = [[x, y+dy], [x+dx, y], [x, y-dy], [x-dx, y]]
    poly = plt.Polygon(pts, closed=True, facecolor=color, edgecolor='#7d6608',
                       linewidth=1.8, zorder=3)
    ax.add_patch(poly)
    ax.text(x, y, label, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)


def arrow(ax, x1, y1, x2, y2, color='#8b949e', label='', lw=1.8):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw),
                zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.12, my, label, fontsize=8.5, color=color, va='center', zorder=5)


def section_label(ax, x, y, label, color):
    ax.text(x, y, label, fontsize=8, color=color, fontweight='bold',
            ha='left', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=color+'22',
                      edgecolor=color, linewidth=1), zorder=5)


# ── Title ────────────────────────────────────────────────────────────────────
ax.text(8, 25.3, 'CI/CD Deployment & Rollback Flow',
        ha='center', va='center', fontsize=17, fontweight='bold', color=C_TEXT)
ax.text(8, 24.85, 'GitHub Actions  →  ACR  →  VM  →  Health Check  →  Rollback',
        ha='center', va='center', fontsize=9.5, color=C_SUBTEXT)

# ── SECTION: GitHub ───────────────────────────────────────────────────────────
section_label(ax, 0.3, 24.2, '  GITHUB  ', C_GITHUB)

box(ax, 8, 23.7, 5.5, 0.75, '① Developer pushes to main',
    'git push origin main', color='#0d2a14', border=C_GITHUB)

arrow(ax, 8, 23.32, 8, 22.68)

box(ax, 8, 22.3, 5.5, 0.75, '② GitHub Actions triggered',
    'build-push.yml workflow starts', color='#0d2a14', border=C_GITHUB)

arrow(ax, 8, 21.92, 8, 21.28)

box(ax, 8, 20.9, 5.5, 0.75, '③ Generate version tag',
    'e.g.  v2026.06.05.3  (date + run number)', color='#0d2a14', border=C_GITHUB)

arrow(ax, 8, 20.52, 8, 19.88)

box(ax, 8, 19.5, 5.5, 0.75, '④ Build Docker image',
    'docker build on GitHub-hosted runner', color='#0d2a14', border=C_GITHUB)

# ── SECTION: ACR ─────────────────────────────────────────────────────────────
section_label(ax, 0.3, 18.7, '  ACR  ', C_ACR)

arrow(ax, 8, 19.12, 8, 18.48)

box(ax, 8, 18.1, 5.5, 0.75, '⑤ Push image to ACR',
    'registry/dummy-app:v2026.06.05.3   +   :latest', color='#0d1a2e', border=C_ACR)

# ACR side note
ax.text(12.2, 18.1, ':v2026.06.05.3\n← permanent', fontsize=8, color=C_ACR,
        ha='left', va='center', linespacing=1.5)
ax.text(12.2, 17.55, ':latest\n← updated pointer', fontsize=8, color=C_SUBTEXT,
        ha='left', va='center', linespacing=1.5)

# ── SECTION: VM deploy.sh ────────────────────────────────────────────────────
section_label(ax, 0.3, 17.3, '  VM — deploy.sh  ', C_VM)

arrow(ax, 8, 17.72, 8, 17.08)

box(ax, 8, 16.7, 5.8, 0.75, '⑥ SSH into VM — deploy.sh starts',
    'GitHub Actions → appleboy/ssh-action → VM', color='#1a0a35', border=C_VM)

arrow(ax, 8, 16.32, 8, 15.68)

box(ax, 8, 15.3, 5.8, 0.75, '⑦ Inspect running container',
    'docker inspect → reads current tag (e.g. v2026.06.05.2)', color='#1a0a35', border=C_VM)

ax.annotate('', xy=(13.2, 15.3), xytext=(10.9, 15.3),
            arrowprops=dict(arrowstyle='->', color=C_VM, lw=1.5), zorder=2)
box(ax, 14.3, 15.3, 2.0, 0.65, '.previous_version',
    'writes  v2026.06.05.2', color='#1a0a35', border=C_VM, fontsize=9)

arrow(ax, 8, 14.92, 8, 14.28)

box(ax, 8, 13.9, 5.8, 0.75, '⑧ Pull latest image from ACR',
    'docker compose pull  →  gets v2026.06.05.3', color='#1a0a35', border=C_VM)

arrow(ax, 8, 13.52, 8, 12.88)

box(ax, 8, 12.5, 5.8, 0.75, '⑨ Start new container',
    'docker compose up -d --remove-orphans', color='#1a0a35', border=C_VM)

# ── SECTION: Health check ────────────────────────────────────────────────────
section_label(ax, 0.3, 11.7, '  HEALTH CHECK  ', C_HEALTH)

arrow(ax, 8, 12.12, 8, 11.48)

box(ax, 8, 11.1, 5.8, 0.75, '⑩ Health check loop',
    '10 attempts × 6s = 60s window   →   GET /health', color='#2a1f00', border=C_HEALTH)

arrow(ax, 8, 10.72, 8, 10.18)

diamond(ax, 8, 9.7, 3.8, 0.85, 'HTTP 200?')

# ── PASS branch ──────────────────────────────────────────────────────────────
arrow(ax, 9.9, 9.7, 13.0, 9.7, color=C_SUCCESS, label='  PASS')

box(ax, 14.3, 9.7, 2.2, 0.7, '✓  Deployed',
    'writes new tag to\n.previous_version', color='#0d2a14', border=C_SUCCESS, fontsize=9)

# ── FAIL branch ──────────────────────────────────────────────────────────────
section_label(ax, 0.3, 8.9, '  ROLLBACK — rollback.sh  ', C_ROLLBACK)

arrow(ax, 8, 9.27, 8, 8.68, color=C_ROLLBACK, label='  FAIL')

box(ax, 8, 8.3, 5.8, 0.75, '(11) rollback.sh triggered',
    'reads .previous_version → v2026.06.05.2', color='#2a0a0a', border=C_ROLLBACK)

arrow(ax, 8, 7.92, 8, 7.28, color=C_ROLLBACK)

box(ax, 8, 6.9, 5.8, 0.75, '(12) Backup + rewrite compose file',
    'pins image tag to  v2026.06.05.2  (not latest)', color='#2a0a0a', border=C_ROLLBACK)

arrow(ax, 8, 6.52, 8, 5.88, color=C_ROLLBACK)

box(ax, 8, 5.5, 5.8, 0.75, '(13) Pull previous image from ACR',
    'docker pull registry/dummy-app:v2026.06.05.2', color='#2a0a0a', border=C_ROLLBACK)

arrow(ax, 8, 5.12, 8, 4.48, color=C_ROLLBACK)

box(ax, 8, 4.1, 5.8, 0.75, '(14) Restart container with v2026.06.05.2',
    'docker compose up -d --force-recreate', color='#2a0a0a', border=C_ROLLBACK)

arrow(ax, 8, 3.72, 8, 3.18, color=C_ROLLBACK)

diamond(ax, 8, 2.7, 3.8, 0.85, 'HTTP 200?', color=C_ROLLBACK, text_color=C_TEXT)

# rollback pass
arrow(ax, 9.9, 2.7, 13.0, 2.7, color=C_SUCCESS, label='  PASS')
box(ax, 14.3, 2.7, 2.2, 0.7, '✓  Rolled back',
    'compose file restored\nto :latest for next deploy', color='#0d2a14', border=C_SUCCESS, fontsize=9)

# rollback fail
arrow(ax, 8, 2.27, 8, 1.63, color=C_CRITICAL, label='  FAIL')
box(ax, 8, 1.2, 5.8, 0.75, '⚠  CRITICAL — Manual intervention',
    'restore compose file  •  check /var/log/deploy.log', color='#3b0000', border=C_CRITICAL)

# ── Legend ───────────────────────────────────────────────────────────────────
legend_items = [
    (C_GITHUB,   'GitHub / GitHub Actions'),
    (C_ACR,      'Azure Container Registry (ACR)'),
    (C_VM,       'VM — deploy.sh'),
    (C_HEALTH,   'Health Check'),
    (C_ROLLBACK, 'Rollback — rollback.sh'),
    (C_CRITICAL, 'Critical failure'),
]
lx, ly = 0.4, 6.5
ax.text(lx, ly + 0.45, 'Legend', fontsize=9, color=C_SUBTEXT, fontweight='bold')
for i, (color, label) in enumerate(legend_items):
    y_pos = ly - i * 0.48
    patch = FancyBboxPatch((lx, y_pos - 0.14), 0.35, 0.28,
                           boxstyle='round,pad=0.03', facecolor=color+'33',
                           edgecolor=color, linewidth=1.2, zorder=3)
    ax.add_patch(patch)
    ax.text(lx + 0.5, y_pos, label, fontsize=8, color=C_TEXT, va='center')

plt.tight_layout(pad=0.5)
plt.savefig('/Users/rishabhsharma/Desktop/Work/Dex_Ninja/ci-cd-git/docs/cicd-flow.png',
            dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print("Saved: docs/cicd-flow.png")
