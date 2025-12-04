import yaml
import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEDULE_FILE = BASE_DIR / "schedule.yml"
PYTHON = sys.executable


JOB_MAP = {
    "housekeeper": "from jobs.housekeeper_job import HousekeeperJob; HousekeeperJob().run()"
}


def load_schedule():
    if not SCHEDULE_FILE.exists():
        print("❌ schedule.yml not found")
        sys.exit(1)

    with open(SCHEDULE_FILE) as f:
        return yaml.safe_load(f)


def build_cron_entry(schedule, job_name):
    if job_name not in JOB_MAP:
        raise ValueError(f"Unknown job command: {job_name}")

    command = JOB_MAP[job_name]
    return f'{schedule} cd {BASE_DIR} && {PYTHON} -c "{command}"'


def install_crontab(entries):
    cron_existing = os.popen("crontab -l 2>/dev/null").read()

    new_cron = cron_existing.strip() + "\n\n# OpenLP scheduler\n" + "\n".join(entries) + "\n"

    with open("/tmp/cronfile", "w") as f:
        f.write(new_cron)

    os.system("crontab /tmp/cronfile")

    print("✅ Cron installed successfully")


def dry_run(entries):
    print("\nGenerated cron entries:\n")
    for e in entries:
        print(e)


def main():
    config = load_schedule()
    jobs = config.get("jobs", {})

    entries = []

    for name, job in jobs.items():
        schedule = job.get("schedule")
        command = job.get("command")

        if not schedule or not command:
            raise ValueError(f"Invalid job config: {name}")

        entry = build_cron_entry(schedule, command)
        entries.append(entry)

    if "--install" in sys.argv:
        install_crontab(entries)
    else:
        dry_run(entries)


if __name__ == "__main__":
    main()
