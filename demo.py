import os
import shutil
import yaml
import argparse

def isolate_files(nlu_dir, backup_dir, intents_to_keep):
    os.makedirs(backup_dir, exist_ok=True)

    for filename in os.listdir(nlu_dir):
        if not filename.endswith((".yml", ".yaml")):
            continue

        file_path = os.path.join(nlu_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            examples = data.get("nlu", [])
            if not examples:
                shutil.move(file_path, os.path.join(backup_dir, filename))
                print(f"Moved {filename} (no NLU examples)")
                continue

            file_intents = {e.get("intent") for e in examples if "intent" in e}
            if not any(i in intents_to_keep for i in file_intents):
                shutil.move(file_path, os.path.join(backup_dir, filename))
                print(f"Moved {filename} (intents: {file_intents})")
        except Exception as e:
            print(f"Skipped {filename} due to error: {e}")

    print("\nIsolation complete.")


def restore_files(nlu_dir, backup_dir):
    if not os.path.exists(backup_dir):
        print(f"No backup directory found: {backup_dir}")
        return

    for filename in os.listdir(backup_dir):
        shutil.move(os.path.join(backup_dir, filename), os.path.join(nlu_dir, filename))
        print(f"Restored {filename}")

    print("\nRestoration complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Isolate or restore Rasa NLU files by intent.")

    parser.add_argument("--mode", choices=["isolate", "restore"], required=True, help="Mode: isolate or restore")
    parser.add_argument("--nlu_dir", default="data/nlu", help="NLU directory")
    parser.add_argument("--backup_dir", default="data/nlu_backup", help="Backup directory for moved files")
    parser.add_argument("--intents", nargs="*", help="List of intents to keep (only needed for isolate)")

    args = parser.parse_args()

    if args.mode == "isolate":
        if not args.intents:
            parser.error("You must provide --intents when using isolate mode.")
        isolate_files(args.nlu_dir, args.backup_dir, set(args.intents))
    elif args.mode == "restore":
        restore_files(args.nlu_dir, args.backup_dir)