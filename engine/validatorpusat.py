# engine/validator_pusat.py
import sys
import os
import importlib
from typing import Dict, Any

def validate_all_engines():
    """Validasi semua engine dengan output terstruktur"""
    results = {}
    
    # Daftar engine yang akan divalidasi
    engine_modules = [
        "battle",
        "hangman",
        "maze", 
        "runner",
        "parser",
    ]
    
    for module_name in engine_modules:
        print(f"\n🔍 Validating {module_name}...")
        
        try:
            # Import module
            module = importlib.import_module(f"engine.{module_name}")
            
            # Cari fungsi validate_engine
            if hasattr(module, 'validate_engine'):
                result = module.validate_engine()
                results[module_name] = result
                
                if result.get("ok"):
                    print(f"  ✅ {module_name}: PASS")
                    if "result" in result:
                        print(f"     Result: {result.get('result')}")
                else:
                    print(f"  ❌ {module_name}: FAIL")
                    print(f"     Error: {result.get('error', 'Unknown error')}")
            else:
                # Module tanpa validator
                results[module_name] = {
                    "module": module_name,
                    "ok": False,
                    "error": "No validate_engine() function found"
                }
                print(f"  ⚠️  {module_name}: NO VALIDATOR")
                
        except ImportError as e:
            results[module_name] = {
                "module": module_name,
                "ok": False,
                "error": f"Import failed: {e}"
            }
            print(f"  ❌ {module_name}: IMPORT FAILED")
        except Exception as e:
            results[module_name] = {
                "module": module_name,
                "ok": False,
                "error": f"Validation failed: {e}"
            }
            print(f"  ❌ {module_name}: VALIDATION ERROR")
    
    # Summary
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    
    passed = sum(1 for r in results.values() if r.get("ok"))
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    # Tampilkan yang gagal
    failures = [(name, r) for name, r in results.items() if not r.get("ok")]
    if failures:
        print(f"\n❌ Failures ({len(failures)}):")
        for name, r in failures:
            print(f"  • {name}: {r.get('error', 'Unknown')}")
    
    return {
        "ok": all(r.get("ok") for r in results.values()),
        "results": results,
        "summary": f"{passed}/{total} engines passed"
    }

def validate_specific(engine_name: str):
    """Validasi engine spesifik"""
    try:
        module = importlib.import_module(f"engine.{engine_name}")
        
        if not hasattr(module, 'validate_engine'):
            return {
                "ok": False,
                "error": f"Module {engine_name} has no validate_engine()"
            }
        
        return module.validate_engine()
        
    except ImportError:
        return {
            "ok": False,
            "error": f"Module engine.{engine_name} not found"
        }

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Game Engine Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Validasi semua engine
  %(prog)s --engine battle    # Validasi engine spesifik
        """
    )
    
    parser.add_argument('--engine', help='Nama engine spesifik (battle, maze, dll)')
    
    args = parser.parse_args()
    
    print("🚀 GAME ENGINE VALIDATOR")
    print("="*50)
    
    if args.engine:
        result = validate_specific(args.engine)
        print(f"\nResult for {args.engine}:")
        print(f"  Status: {'✅ PASS' if result.get('ok') else '❌ FAIL'}")
        if not result.get('ok'):
            print(f"  Error: {result.get('error')}")
    else:
        result = validate_all_engines()
        print(f"\nOverall: {'✅ ALL PASS' if result['ok'] else '❌ SOME FAILED'}")
    
    sys.exit(0 if result.get('ok') else 1)

if __name__ == "__main__":
    main()