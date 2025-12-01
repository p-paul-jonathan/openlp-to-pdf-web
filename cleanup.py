import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")

def cleanup_tmp():
    if not os.path.exists(TMP_DIR):
        print(f"❌ tmp directory does not exist: {TMP_DIR}")
        return

    print(f"🧹 Cleaning directory: {TMP_DIR}\n")

    for item in os.listdir(TMP_DIR):
        item_path = os.path.join(TMP_DIR, item)

        # Skip .gitkeep
        if item == ".gitkeep":
            print(f"⏭️  Skipping {item}")
            continue

        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"✅ Removed directory: {item}")
            else:
                os.remove(item_path)
                print(f"✅ Removed file: {item}")

        except Exception as e:
            print(f"❌ Failed to remove {item}: {e}")

    print("\n✨ Cleanup complete")


if __name__ == "__main__":
    cleanup_tmp()
