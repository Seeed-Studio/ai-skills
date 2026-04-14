"""Shared constants for the schematic analyzer pipeline."""

# ---- Format identifiers ----
FORMAT_KICAD = "kicad"
FORMAT_CADENCE = "cadence"

# ---- Net type strings (used across all parsers and builders) ----
NET_TYPE_LOCAL = "local"
NET_TYPE_POWER = "power"
NET_TYPE_GLOBAL = "global"
NET_TYPE_HIERARCHICAL = "hierarchical"
NET_TYPE_UNKNOWN = "unknown"
DEFAULT_NET_TYPE = "Unclassified"

# ---- Sheet type strings ----
SHEET_TYPE_ROOT = "root"
SHEET_TYPE_HIERARCHY = "hierarchy"

# ---- Page name prefix ----
PAGE_NAME_PREFIX = "page"

# ---- Default query/config values ----
DEFAULT_QUERY_LIMIT = 10

# ---- Subprocess timeout for kicad-cli (seconds) ----
KICAD_CLI_TIMEOUT = 60
