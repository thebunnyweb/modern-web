import os
import shutil
import argparse

def isolate_by_filename(nlu_dir, backup_dir, keywords_to_keep):
    os.makedirs(backup_dir, exist_ok=True)

    kept, moved = 0, 0

    for filename in os.listdir(nlu_dir):
        if not filename.endswith((".yml", ".yaml")):
            continue

        if any(kw.lower() in filename.lower() for kw in keywords_to_keep):
            kept += 1
        else:
            shutil.move(os.path.join(nlu_dir, filename), os.path.join(backup_dir, filename))
            print(f"Moved: {filename}")
            moved += 1

    print(f"\nIsolation complete. Kept: {kept}, Moved: {moved}")

def restore_files(nlu_dir, backup_dir):
    if not os.path.exists(backup_dir):
        print(f"No backup folder found: {backup_dir}")
        return

    files = os.listdir(backup_dir)
    for filename in files:
        shutil.move(os.path.join(backup_dir, filename), os.path.join(nlu_dir, filename))
        print(f"Restored: {filename}")

    print(f"\nRestored {len(files)} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Rasa NLU files by filename keywords.")
    parser.add_argument("--mode", choices=["isolate", "restore"], required=True, help="Operation mode")
    parser.add_argument("--nlu_dir", default="data", help="Directory with NLU YAMLs")
    parser.add_argument("--backup_dir", default="data/nlu_backup", help="Backup folder")
    parser.add_argument("--keep", nargs="*", help="List of filename keywords to keep (required for isolate)")

    args = parser.parse_args()

    if args.mode == "isolate":
        if not args.keep:
            parser.error("--keep is required in isolate mode.")
        isolate_by_filename(args.nlu_dir, args.backup_dir, args.keep)
    elif args.mode == "restore":
        restore_files(args.nlu_dir, args.backup_dir)