import sys
from pathlib import Path
import config
import bank_manager


def run_comparisons():
    print("=" * 55)
    print("  MODE: TECH COMPARISONS")
    print("=" * 55)

    from upload_youtube import upload
    import comparisons_video

    out_path, data = comparisons_video.main()
    print("\nUploading with viral SEO...")
    upload(str(out_path), mode="comparisons", playlist_key="comparisons", script_data=data)
    print("Comparison video done!")
    bank_manager.ensure_refilled("comparisons")


def run_loop():
    import time, random
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
    modes = ["comparisons"]
    print(f"\n{'='*55}")
    print(f"  LOOP MODE — generating every {interval}s")
    print(f"  Modes: {', '.join(modes)}")
    print(f"{'='*55}\n")
    while True:
        mode = random.choice(modes)
        runner = {"comparisons": run_comparisons}[mode]
        try:
            runner()
        except Exception as e:
            print(f"  {mode} failed: {e}")
        print(f"\n  Sleeping {interval}s... (Ctrl+C to stop)")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n  Loop stopped.")
            break


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "comparisons"
    if mode == "loop":
        run_loop()
    elif mode == "comparisons":
        run_comparisons()
    else:
        print(f"Unknown mode: {mode}. Use 'comparisons' or 'loop'.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"PIPELINE CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
