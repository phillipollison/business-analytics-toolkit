import argparse
import sys
from pathlib import Path

from automation.workflow import run_configured_automation, make_client_summary


LOCK_FILE = Path("automation/locks/clean0ps_automation.lock")


def acquire_lock():
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    if LOCK_FILE.exists():
        raise RuntimeError(
            "Automation lock file exists. Another run may still be active. "
            "Delete automation/locks/clean0ps_automation.lock only if no run is active."
        )

    LOCK_FILE.write_text("locked", encoding="utf-8")


def release_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Run Clean0ps local API automation."
    )

    parser.add_argument(
        "--config",
        default="automation/configs/config.example.json"
    )

    args = parser.parse_args()

    acquire_lock()

    try:
        result = run_configured_automation(args.config)

        print("")
        print("=" * 80)
        print(make_client_summary(result))
        print("=" * 80)
        print("")

        print("Run Summary:")
        print(result["summary"].to_string(index=False))

        print("")
        print("Output Files:")
        for key, value in result["output_paths"].items():
            print(f"{key}: {value}")

        return 0

    finally:
        release_lock()


if __name__ == "__main__":
    sys.exit(main())
