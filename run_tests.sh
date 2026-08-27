#!/usr/bin/env bash
# Run every test suite. No external dependencies required.
set -u
cd "$(dirname "$0")"
fail=0
echo "=== SOT gate ==="
PYTHONPATH=src python3 tests/test_sot_gate.py || fail=1
echo
echo "=== calibration regression ==="
PYTHONPATH=src python3 tests/test_calibration_regression.py || fail=1
echo
if [ $fail -eq 0 ]; then echo "ALL SUITES PASSED"; else echo "SOME SUITES FAILED"; fi
exit $fail
