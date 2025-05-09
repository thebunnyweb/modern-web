import os
import shutil
import argparse

def isolate_matching_files(folder, backup_folder, keywords):
    os.makedirs(backup_folder, exist_ok=True)
    kept, moved = 0, 0

    for filename in os.listdir(folder):
        if not filename.endswith((".yml", ".yaml")):
            continue

        if any(kw.lower() in filename.lower() for kw in keywords):
            kept += 1
        else:
            shutil.move(os.path.join(folder, filename), os.path.join(backup_folder, filename))
            print(f"Moved: {filename}")
            moved += 1

    print(f"[{folder}] Isolation complete. Kept: {kept}, Moved: {moved}")

def restore_files(backup_folder, target_folder):
    if not os.path.exists(backup_folder):
        print(f"No backup folder found: {backup_folder}")
        return

    files = os.listdir(backup_folder)
    for filename in files:
        shutil.move(os.path.join(backup_folder, filename), os.path.join(target_folder, filename))
        print(f"Restored: {filename}")

    print(f"[{target_folder}] Restored {len(files)} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Isolate or restore NLU and domain files by filename.")
    parser.add_argument("--mode", choices=["isolate", "restore"], required=True, help="Mode to run: isolate or restore")
    parser.add_argument("--keep", nargs="*", help="Keywords to keep (required for isolate)")
    parser.add_argument("--nlu_dir", default="data", help="Folder containing NLU files")
    parser.add_argument("--domain_dir", default="domains", help="Folder containing domain files")

    args = parser.parse_args()

    nlu_backup = os.path.join(args.nlu_dir, "backup")
    domain_backup = os.path.join(args.domain_dir, "backup")

    if args.mode == "isolate":
        if not args.keep:
            parser.error("--keep is required when using isolate mode.")
        isolate_matching_files(args.nlu_dir, nlu_backup, args.keep)
        isolate_matching_files(args.domain_dir, domain_backup, args.keep)
    elif args.mode == "restore":
        restore_files(nlu_backup, args.nlu_dir)
        restore_files(domain_backup, args.domain_dir)