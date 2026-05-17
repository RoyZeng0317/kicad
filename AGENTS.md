# AGENTS.md — KiCad Projects Repository

## Structure

Each top-level directory (except `Documents/`) is an **independent KiCad project** with its own `.kicad_pro`, `.kicad_sch`, `.kicad_pcb` files.

| Directory | Description |
|-----------|-------------|
| `Atmega 2560/` | Arduino Mega 2560 PCB |
| `New_Atmega 2560/` | Revised Mega 2560 with sub-sheets (`usb.kicad_sch`) |
| `CPLD_Digital_Clock_Battrery/` | CPLD digital clock, battery-powered |
| `New_CPLD_Digtal_Clock_type-c_Battery/` | Revised CPLD clock with USB-C + TP4056 charger, multiple sub-sheets (`Children_board`, `Charging_board`) |
| `ESP32/` | ESP32 module with Wi-Fi sub-sheet |
| `ESP32 nano/` | ESP32 nano variant |
| `ESP32-WROOM-32-footprint/` | Footprint-only library |
| `ESP32-WROOM-32-symbol/` | Symbol-only library |
| `Flash Light/` | Flashlight PCB |
| `Digital Picture Frame/` | Digital picture frame PCB |
| `USB-BSSB-TH-footprint/` | USB-BSSB-TH footprint library |
| `USB-BSSB-TH-symbol/` | USB-BSSB-TH symbol library |
| `Documents/` | BOM CSVs, datasheets, reference images |

There is **no build system, package manager, or CI pipeline** — these are KiCad EDA projects edited in the KiCad GUI.

## Project format

All projects use KiCad v8+ format (`.kicad_pro` version 3, `.kicad_prl`). Each project is self-contained.

## Auto-generated KiCad artifacts (should be gitignored)

- `*-backups/` — KiCad auto-backup directories
- `fp-info-cache` — footprint library cache

Consider adding a root `.gitignore` with:
```
*-backups/
fp-info-cache
.history/
```

## Notable conventions

- Some project directories contain **spaces** (e.g., `Atmega 2560/`, `Flash Light/`). Quote paths when scripting.
- `New_Atmega 2560/` has a **nested sub-project** (`New_Atmega 2560/New_Atmega 2560/`) — likely a duplicate or work-in-progress.
- Custom symbols (`.kicad_sym`) live inside individual project directories, not shared centrally.
- There is **no `sym-lib-table`** at root — each project references its local symbols directly.
- `fp-lib-table` exists only in `New_Atmega 2560/`.

## Schematic conventions

- Connection grid: 50 mil (KiCad default).
- Default wire width: 6 mil (schematic), 0.2 mm (PCB).
- Default track width: 0.2 mm, via 0.6/0.3 mm.
- Pin-to-pin conflicts are set to `warning` severity (not error).

## Workflow notes

- Open a project by opening its `.kicad_pro` file in KiCad.
- To generate BOM: use built-in BOM export (CSV format configured per project).
- No automated ERC/DRC in CI — must be run manually from KiCad.
- Projects are not cross-referenced; changes in one do not affect others.
