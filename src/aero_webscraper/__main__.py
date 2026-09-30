# MMA FILE SUMMARY
# Purpose: Enables python -m aero_webscraper as the operator CLI.
# Public interface: Module execution; delegates to adapters.cli without owning policy.
from aero_webscraper.adapters.cli import main
raise SystemExit(main())