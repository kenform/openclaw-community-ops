#!/usr/bin/env python3
import json
import subprocess
import time
from pathlib import Path

CONFIG_PATH = Path("/home/openclawuser/.openclaw/workspace/config/autopipeline_no_gpt.json")


def run_cmd(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "cmd": " ".join(cmd),
        "code": p.returncode,
        "stdout": (p.stdout or "").strip(),
        "stderr": (p.stderr or "").strip(),
    }


def service_is_active(name):
    p = subprocess.run(["systemctl", "--user", "is-active", name], capture_output=True, text=True)
    return p.returncode == 0 and (p.stdout or "").strip() == "active"


def main():
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    ts = int(time.time())

    report = {
        "ts": ts,
        "mode": "autopipeline_no_gpt",
        "services": [],
        "cleanup_worker": None,
        "summary": {},
    }

    # 1) keep parser stack alive
    for svc in cfg.get("services", []):
        active_before = service_is_active(svc)
        restarted = False
        restart_result = None
        if not active_before:
            restart_result = run_cmd(["systemctl", "--user", "restart", svc])
            restarted = True
        active_after = service_is_active(svc)
        report["services"].append(
            {
                "service": svc,
                "active_before": active_before,
                "restarted": restarted,
                "active_after": active_after,
                "restart_result": restart_result,
            }
        )

    # 2) run telegram cleanup worker (no GPT)
    tel = cfg.get("telethon", {})
    stop_svc = tel.get("stop_service_before_run")
    start_svc = tel.get("start_service_after_run")

    pre_stop = run_cmd(["systemctl", "--user", "stop", stop_svc]) if stop_svc else None

    worker_cmd = [tel["python"], tel["worker_script"], str(CONFIG_PATH)]
    worker_raw = run_cmd(worker_cmd)

    worker_json = None
    if worker_raw["code"] == 0 and worker_raw["stdout"]:
        try:
            worker_json = json.loads(worker_raw["stdout"].splitlines()[-1])
        except Exception:
            worker_json = {"parse_error": True, "raw": worker_raw["stdout"][:2000]}

    post_start = run_cmd(["systemctl", "--user", "start", start_svc]) if start_svc else None

    report["cleanup_worker"] = {
        "pre_stop": pre_stop,
        "worker_exec": worker_raw,
        "worker_report": worker_json,
        "post_start": post_start,
    }

    reports_dir = Path(cfg.get("reports_dir", "/home/openclawuser/.openclaw/workspace/reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    out = reports_dir / f"autopipeline_no_gpt_{ts}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    state_file = Path(cfg.get("state_file", str(reports_dir / "no_gpt_autopipeline_state.json")))
    state_file.write_text(
        json.dumps({"last_run": ts, "last_report": str(out)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({"report": str(out), "worker_ok": worker_raw["code"] == 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
