import os
import importlib

def run_all_validators():
    results = []

    # Dapatkan path folder "engine"
    folder = os.path.dirname(__file__)

    for file in os.listdir(folder):
        # Lewatkan diri sendiri
        if file == "validator_master.py":
            continue

        # Hanya file Python
        if not file.endswith(".py"):
            continue

        module_name = file[:-3]  # remove .py

        try:
            # Import modul engine.<module_name>
            module = importlib.import_module(f"engine.{module_name}")

            # Harus ada validate()
            if hasattr(module, "auto_validate"):
                result = module.auto_validate()
                result["file"] = module_name
                results.append(result)
            else:
                results.append({
                    "file": module_name,
                    "ok": False,
                    "issues": ["Missing validate() function"]
                })

        except Exception as e:
            results.append({
                "file": module_name,
                "ok": False,
                "issues": [f"Import error: {e}"]
            })

    return results


if __name__ == "__main__":
    all_results = run_all_validators()

    print("\n=== MASTER VALIDATION REPORT ===\n")
    for r in all_results:
        print(f"[{r['file']}] {'OK' if r['ok'] else 'FAIL'}")
        for issue in r["issues"]:
            print("  -", issue)
        print()
