from pathlib import Path

LOG_FILES = [
    Path("logs/clean0ps_errors.log"),
    Path("logs/clean0ps_events.log"),
]

def show_tail(path: Path, lines: int = 80):
    print("\n" + "=" * 80)
    print(path)
    print("=" * 80)

    if not path.exists():
        print("No log file found yet.")
        return

    content = path.read_text(errors="replace").splitlines()

    if not content:
        print("Log file is empty.")
        return

    for line in content[-lines:]:
        print(line)

def main():
    for log_file in LOG_FILES:
        show_tail(log_file)

if __name__ == "__main__":
    main()
