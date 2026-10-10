# SPDX-License-Identifier: MIT
"""Entry point used to build the standalone executable (see construir_exe.bat)."""
import sys

from markitdown._gui import main, convert_path

if __name__ == "__main__":
    # Hidden self-test used to verify a built executable without opening a window.
    if len(sys.argv) == 3 and sys.argv[1] == "--selftest":
        ok, out = convert_path(sys.argv[2])
        print(("OK: " if ok else "ERROR: ") + out[:200])
        sys.exit(0 if ok else 1)
    main()
