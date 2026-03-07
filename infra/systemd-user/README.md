# OpenClaw multi-agent systemd (user) scaffold

## 1) Configure real commands
```bash
cp /home/openclawuser/.openclaw/workspace/config/agent-commands.env.example \
   /home/openclawuser/.openclaw/workspace/config/agent-commands.env
nano /home/openclawuser/.openclaw/workspace/config/agent-commands.env
```

## 2) Install unit files
```bash
mkdir -p ~/.config/systemd/user
cp /home/openclawuser/.openclaw/workspace/infra/systemd-user/*.service ~/.config/systemd/user/
systemctl --user daemon-reload
```

## 3) Start always-on agents
```bash
systemctl --user enable --now oc-orchestrator.service oc-mom.service oc-telegram.service
```

## 4) Start on-demand agents
```bash
systemctl --user start oc-dev.service
systemctl --user start oc-youtube.service
systemctl --user start oc-news.service
systemctl --user start oc-study.service
systemctl --user start oc-english.service
```

## 5) Verify
```bash
systemctl --user status oc-orchestrator.service oc-mom.service oc-telegram.service
journalctl --user -u oc-telegram.service -n 100 --no-pager
```

> Note: this scaffold intentionally avoids hardcoding uncertain OpenClaw launch commands.
> Fill `config/agent-commands.env` with commands verified in your environment.
