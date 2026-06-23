"""Cadence OrCAD Capture XML parser.

Parses XML exported from OrCAD Capture (File → Export → XML...) to extract
components, nets, pages, and pin-to-net connectivity via coordinate matching.
"""

import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# Reuse KiCad data structures so downstream pipeline works unchanged
from ..kicad.schematic_parser import SchematicComponent, SchematicNet


# Pin electrical type mapping from Cadence numeric type
# type=4: passive/signal, type=7: power, type=0: input, type=1: output, type=2: bidirectional
_CADENCE_PIN_TYPES = {
    "0": "input",
    "1": "output",
    "2": "bidirectional",
    "3": "tri_state",
    "4": "passive",
    "5": "open_collector",
    "6": "open_emitter",
    "7": "power_in",
}

# Property-based DNP detection rules.
# Each entry: (property_name, {match_values})  — matched case-insensitively.
# Extend this list to support new DNP/assembly property conventions.
_CADENCE_DNP_PROP_RULES: list[tuple[str, frozenset[str]]] = [
    ("ASSY",              frozenset({"DNP"})),
    ("DNP",               frozenset({"TRUE", "1", "YES"})),
    ("POPULATE",          frozenset({"NO", "FALSE", "0"})),
    ("EXCLUDE_FROM_BOM",  frozenset({"TRUE", "1", "YES"})),
    ("Status",            frozenset({"DNP", "DO NOT POPULATE", "NOT FITTED", "NF"})),
]

# Value-based DNP markers — if component value matches exactly, it's DNP.
_CADENCE_DNP_VALUE_MARKERS: frozenset[str] = frozenset({
    "DNP", "NC", "NF", "NO STUFF", "DNS", "DO NOT POPULATE",
})


def _safe_int(val: Any, default: int = 0) -> int:
    """Convert a value to int, returning *default* on any failure."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


@dataclass
class _WireSegment:
    """One wire segment from a NetScalar."""
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    net_id: int  # index of parent NetScalar


@dataclass
class _NetData:
    """Parsed net with wire segments and optional name."""
    net_id: int
    name: str
    wires: list[_WireSegment] = field(default_factory=list)
    alias_positions: list[tuple[int, int]] = field(default_factory=list)
    page_index: int = 0


@dataclass
class _GlobalData:
    """Parsed Global power/ground symbol."""
    name: str
    symbol_name: str
    loc_x: int
    loc_y: int
    page_index: int
    rotation: int = 0
    mirror: int = 0


@dataclass
class _OffPageData:
    """Parsed OffPageConnector for cross-page signals."""
    name: str
    symbol_name: str
    loc_x: int
    loc_y: int
    page_index: int
    rotation: int = 0
    mirror: int = 0
    iref: str = ""


@dataclass
class _PinData:
    """Component pin with absolute position."""
    name: str
    position_index: str
    pin_type: str
    abs_x: int
    abs_y: int
    is_no_connect: bool = False


@dataclass
class _PartData:
    """Parsed component instance."""
    reference: str
    value: str
    pkg_name: str
    lib_name: str
    footprint: str
    loc_x: int
    loc_y: int
    mirror: int
    rotation: int
    device_designator: str
    properties: dict[str, str] = field(default_factory=dict)
    pins: list[_PinData] = field(default_factory=list)
    page_index: int = 0
    db_id: str = ""


def _get_symbol_connection_point_static(
    loc_x: int, loc_y: int, pin_offset: tuple[int, int],
    rotation: int = 0, mirror: int = 0,
) -> tuple[int, int]:
    """Calculate connection point for a symbol given its pin offset and transform.

    This is the pure-logic version used by both the parser and unit tests.
    """
    dx, dy = pin_offset

    # Apply mirror first (horizontal flip: negate X offset)
    if mirror:
        dx = -dx

    # Apply rotation to pin offset (rotation is on the symbol placement)
    if rotation == 1:  # 90°
        dx, dy = -dy, dx
    elif rotation == 2:  # 180°
        dx, dy = -dx, -dy
    elif rotation == 3:  # 270°
        dx, dy = dy, -dx

    return loc_x + dx, loc_y + dy


def _transform_pin_coords(
    part_loc_x: int, part_loc_y: int,
    hotpt_x: int, hotpt_y: int,
    mirror: int, rotation: int,
) -> tuple[int, int]:
    """Transform pin hotpoint coordinates to absolute schematic coordinates.

    In OrCAD Capture XML, hotptX/hotptY are already relative to the part's
    placed position (locX/locY) with mirror and rotation already accounted for.
    Simple addition gives the absolute position.
    """
    return part_loc_x + hotpt_x, part_loc_y + hotpt_y


def is_cadence_xml(file_path: str | Path) -> bool:
    """Check if an XML file is a Cadence OrCAD Capture export.

    Uses multiple heuristic checks for robustness across different
    OrCAD export versions and configurations:
    1. dsn.xsd schema reference (standard OrCAD export)
    2. <Design root element (OrCAD Capture XML structure)
    3. Cadence-specific elements: <Schematic>, <PartInst>, <Cache>
    4. Cadence namespace patterns in root element
    """
    path = Path(file_path)
    if not path.exists() or path.suffix.lower() != ".xml":
        return False
    try:
        # Read first 4KB to check header without parsing full file
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            header = f.read(4096)

        # Strong indicators (any one is sufficient)
        strong_indicators = [
            "dsn.xsd",
            "<Design",
            "<Schematic>",
            "xsi:schemaLocation",
        ]
        strong_count = sum(1 for ind in strong_indicators if ind in header)
        if strong_count >= 2:
            return True

        # Moderate indicators (need 2+ to confirm)
        moderate_indicators = [
            "<PartInst",
            "<Cache>",
            "<PortInstScalar",
            "<NetScalar",
            "<TitleBlock",
            "<PageDateTime",
        ]
        moderate_count = sum(1 for ind in moderate_indicators if ind in header)
        if moderate_count >= 2:
            return True

        # Single strong indicator + one moderate indicator
        if strong_count >= 1 and moderate_count >= 1:
            return True

        return False
    except Exception:
        return False


class CadenceXMLParser:
    """Parser for Cadence OrCAD Capture XML export files.

    Implements the same interface as KiCad SchematicParser so the downstream
    analysis pipeline (core detection, role classification, subsystem detection)
    works unchanged.
    """

    def __init__(self, file_path: str, include_child_sheets: bool = True) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Cadence XML file not found: {file_path}")

        self._tree: Optional[ET.ElementTree] = None
        self._root: Optional[ET.Element] = None

        # Cached parsed data
        self._pages: Optional[list[dict[str, Any]]] = None
        self._parts: Optional[list[_PartData]] = None
        self._nets_data: Optional[list[_NetData]] = None
        self._globals: Optional[list[_GlobalData]] = None
        self._offpage: Optional[list[_OffPageData]] = None
        self._components: Optional[list[SchematicComponent]] = None
        self._nets: Optional[list[SchematicNet]] = None
        self._pin_net_map: Optional[dict[str, dict[str, str]]] = None  # ref -> {pin_name -> net_name}
        self._title_block: Optional[dict[str, str]] = None
        self._unmatched_pin_count: int = 0  # Count of pins not matched to any net

    def _ensure_parsed(self) -> None:
        """Parse the XML file if not already done."""
        if self._tree is not None:
            return
        try:
            self._tree = ET.parse(self.file_path)
        except ET.ParseError as exc:
            raise ValueError(
                f"Failed to parse Cadence XML file '{self.file_path}': {exc}"
            ) from exc
        self._root = self._tree.getroot()
        try:
            self._parse_all()
        except Exception:
            # Reset so a retry will re-parse from scratch
            self._tree = None
            self._root = None
            raise

    def _parse_all(self) -> None:
        """Parse all data from the XML tree."""
        self._parse_symbol_pin_cache()
        self._parse_pages()
        self._parse_parts()
        self._parse_nets_raw()
        self._parse_globals()
        self._parse_offpage()
        self._parse_title_block()
        self._build_connectivity()
        self._build_components()
        self._build_nets()

    def _parse_symbol_pin_cache(self) -> None:
        """Parse GlobalSymbol and OffPageSymbol pin offsets from <Cache>."""
        self._symbol_pin_offsets: dict[str, tuple[int, int]] = {}
        cache = self._root.find("Cache")
        if cache is None:
            return

        # Parse GlobalSymbol pin offsets (GND, VCC_BAR, etc.)
        for gs in cache.findall("GlobalSymbol"):
            gs_defn = gs.find("Defn")
            if gs_defn is None:
                continue
            sym_name = gs_defn.get("name", "")
            pin = gs.find("SymbolPinScalar")
            if pin is not None:
                pin_defn = pin.find("Defn")
                if pin_defn is not None:
                    hx = _safe_int(pin_defn.get("hotptX", "0"))
                    hy = _safe_int(pin_defn.get("hotptY", "0"))
                    if sym_name not in self._symbol_pin_offsets:
                        self._symbol_pin_offsets[sym_name] = (hx, hy)

        # Parse OffPageSymbol pin offsets
        for ops in cache.findall("OffPageSymbol"):
            ops_defn = ops.find("Defn")
            if ops_defn is None:
                continue
            sym_name = ops_defn.get("name", "")
            pin = ops.find("SymbolPinScalar")
            if pin is not None:
                pin_defn = pin.find("Defn")
                if pin_defn is not None:
                    hx = _safe_int(pin_defn.get("hotptX", "0"))
                    hy = _safe_int(pin_defn.get("hotptY", "0"))
                    if sym_name not in self._symbol_pin_offsets:
                        self._symbol_pin_offsets[sym_name] = (hx, hy)

    def _get_symbol_connection_point(
        self, loc_x: int, loc_y: int, symbol_name: str,
        rotation: int = 0, mirror: int = 0,
    ) -> tuple[int, int]:
        """Calculate the wire connection point for a Global or OffPage symbol."""
        pin_offset = self._symbol_pin_offsets.get(symbol_name)
        if pin_offset is None:
            # Unknown symbol — use symbol's own position as connection point
            return (loc_x, loc_y)
        return _get_symbol_connection_point_static(loc_x, loc_y, pin_offset, rotation, mirror)

    def _parse_pages(self) -> None:
        """Extract page structure from <Schematic><Page> elements."""
        self._pages = []
        schematic = self._root.find("Schematic")
        if schematic is None:
            return

        for idx, page in enumerate(schematic.findall("Page")):
            defn = page.find("Defn")
            page_name = defn.get("name", f"Page_{idx + 1}") if defn is not None else f"Page_{idx + 1}"
            dt = page.find("PageDateTime")
            create_date = ""
            modify_date = ""
            if dt is not None:
                dt_defn = dt.find("Defn")
                if dt_defn is not None:
                    create_date = dt_defn.get("createDate", "")
                    modify_date = dt_defn.get("modifyDate", "")

            self._pages.append({
                "index": idx,
                "name": page_name,
                "create_date": create_date,
                "modify_date": modify_date,
                "element": page,
            })

    def _parse_parts(self) -> None:
        """Extract all PartInst elements from all pages."""
        self._parts = []

        for page_info in self._pages:
            page_elem = page_info["element"]
            page_idx = page_info["index"]

            for part_inst in page_elem.findall("PartInst"):
                part = self._parse_one_part(part_inst, page_idx)
                if part is not None:
                    self._parts.append(part)

    def _parse_one_part(self, part_inst: ET.Element, page_index: int) -> Optional[_PartData]:
        """Parse a single PartInst element."""
        defn = part_inst.find("Defn")
        if defn is None:
            return None

        ref_elem = part_inst.find("Reference")
        if ref_elem is None:
            return None
        ref_defn = ref_elem.find("Defn")
        if ref_defn is None:
            return None
        reference = ref_defn.get("name", "")
        if not reference:
            return None

        # Value
        val_elem = part_inst.find("PartValue")
        value = ""
        if val_elem is not None:
            val_defn = val_elem.find("Defn")
            if val_defn is not None:
                value = val_defn.get("name", "")

        # Part info
        pkg_name = defn.get("pkgName", "")
        lib_name = defn.get("libName", "")
        loc_x = _safe_int(defn.get("locX", "0"))
        loc_y = _safe_int(defn.get("locY", "0"))
        mirror = _safe_int(defn.get("mirror", "0"))
        rotation = _safe_int(defn.get("rotation", "0"))
        device_designator = defn.get("deviceDesignator", "")
        db_id = defn.get("dbId", "")

        # Properties from PartInstUserProp
        properties: dict[str, str] = {}
        for prop in part_inst.findall("PartInstUserProp"):
            prop_defn = prop.find("Defn")
            if prop_defn is not None:
                pname = prop_defn.get("name", "")
                pval = prop_defn.get("val", "")
                if pname:
                    properties[pname] = pval

        footprint = properties.get("PCB Footprint", "")

        # Pins from PortInstScalar
        pins: list[_PinData] = []
        for port in part_inst.findall("PortInstScalar"):
            port_defn = port.find("Defn")
            if port_defn is None:
                continue

            pin_name = port_defn.get("name", "")
            position_idx = port_defn.get("position", "0")
            pin_type_code = port_defn.get("type", "4")
            hotpt_x = _safe_int(port_defn.get("hotptX", "0"))
            hotpt_y = _safe_int(port_defn.get("hotptY", "0"))

            # Check no-connect
            is_nc = False
            nc_elem = port.find("IsNoConnect")
            if nc_elem is not None:
                nc_defn = nc_elem.find("Defn")
                if nc_defn is not None:
                    is_nc = nc_defn.get("val", "0") == "1"

            abs_x, abs_y = _transform_pin_coords(
                loc_x, loc_y, hotpt_x, hotpt_y, mirror, rotation,
            )

            pins.append(_PinData(
                name=pin_name,
                position_index=position_idx,
                pin_type=_CADENCE_PIN_TYPES.get(pin_type_code, "passive"),
                abs_x=abs_x,
                abs_y=abs_y,
                is_no_connect=is_nc,
            ))

        return _PartData(
            reference=reference,
            value=value,
            pkg_name=pkg_name,
            lib_name=lib_name,
            footprint=footprint,
            loc_x=loc_x,
            loc_y=loc_y,
            mirror=mirror,
            rotation=rotation,
            device_designator=device_designator,
            properties=properties,
            pins=pins,
            page_index=page_index,
            db_id=db_id,
        )

    def _parse_nets_raw(self) -> None:
        """Extract NetScalar elements with their wire segments and aliases."""
        self._nets_data = []
        net_counter = 0

        for page_info in self._pages:
            page_elem = page_info["element"]
            page_idx = page_info["index"]

            for net_scalar in page_elem.findall("NetScalar"):
                net_defn = net_scalar.find("Defn")
                raw_name = net_defn.get("name", "") if net_defn is not None else ""

                net_data = _NetData(
                    net_id=net_counter,
                    name="",  # Will be set from alias or left auto-generated
                    page_index=page_idx,
                )

                # Parse wire segments and aliases
                for wire in net_scalar.findall("WireScalar"):
                    wire_defn = wire.find("Defn")
                    if wire_defn is None:
                        continue

                    start_x = _safe_int(wire_defn.get("startX", "0"))
                    start_y = _safe_int(wire_defn.get("startY", "0"))
                    end_x = _safe_int(wire_defn.get("endX", "0"))
                    end_y = _safe_int(wire_defn.get("endY", "0"))

                    net_data.wires.append(_WireSegment(
                        start_x=start_x,
                        start_y=start_y,
                        end_x=end_x,
                        end_y=end_y,
                        net_id=net_counter,
                    ))

                    # Check for Alias (net name label)
                    for alias in wire.findall("Alias"):
                        alias_defn = alias.find("Defn")
                        if alias_defn is not None:
                            alias_name = alias_defn.get("name", "")
                            if alias_name:
                                net_data.name = alias_name
                            alias_x = _safe_int(alias_defn.get("locX", "0"))
                            alias_y = _safe_int(alias_defn.get("locY", "0"))
                            net_data.alias_positions.append((alias_x, alias_y))

                # Use raw name from NetScalar Defn if no alias found  
                if not net_data.name and raw_name:
                    net_data.name = raw_name

                self._nets_data.append(net_data)
                net_counter += 1

    def _parse_globals(self) -> None:
        """Extract Global elements (power/ground symbols)."""
        self._globals = []

        for page_info in self._pages:
            page_elem = page_info["element"]
            page_idx = page_info["index"]

            for glob in page_elem.findall("Global"):
                defn = glob.find("Defn")
                if defn is None:
                    continue

                name = defn.get("name", "")
                if not name:
                    # Fallback: use symbolName (e.g. "GND", "VCC_BAR") as net name
                    name = defn.get("symbolName", "")
                if not name:
                    continue

                self._globals.append(_GlobalData(
                    name=name,
                    symbol_name=defn.get("symbolName", ""),
                    loc_x=_safe_int(defn.get("locX", "0")),
                    loc_y=_safe_int(defn.get("locY", "0")),
                    page_index=page_idx,
                    rotation=_safe_int(defn.get("rotation", "0")),
                    mirror=_safe_int(defn.get("mirror", "0")),
                ))

    def _parse_offpage(self) -> None:
        """Extract OffPageConnector elements (cross-page signal connections)."""
        self._offpage = []

        for page_info in self._pages:
            page_elem = page_info["element"]
            page_idx = page_info["index"]

            for opc in page_elem.findall("OffPageConnector"):
                defn = opc.find("Defn")
                if defn is None:
                    continue

                name = defn.get("name", "")
                if not name:
                    continue

                iref = ""
                for prop in opc.findall("OffPageConnectorUserProp"):
                    prop_defn = prop.find("Defn")
                    if prop_defn is not None and prop_defn.get("name") == "IREF":
                        iref = prop_defn.get("val", "")

                self._offpage.append(_OffPageData(
                    name=name,
                    symbol_name=defn.get("symbolName", ""),
                    loc_x=_safe_int(defn.get("locX", "0")),
                    loc_y=_safe_int(defn.get("locY", "0")),
                    page_index=page_idx,
                    rotation=_safe_int(defn.get("rotation", "0")),
                    mirror=_safe_int(defn.get("mirror", "0")),
                    iref=iref,
                ))

    # Flexible field name mappings for title block properties
    _TITLE_BLOCK_FIELD_MAP = {
        "rev": [
            "rev", "revision", "rev.", "version", "ver",
            "sheet revision", "drawing revision", "revsion",
        ],
        "date": [
            "date", "doc date", "document date", "create date",
            "created", "design date", "modified",
        ],
        "company": [
            "organization", "company", "org", "firm",
            "engineer", "author", "designed by",
        ],
        "title": [
            "title", "project", "design name", "project name",
            "schematic name", "drawing title",
        ],
        "comment": [
            "comment", "comments", "note", "notes", "description",
        ],
    }

    def _parse_title_block(self) -> None:
        """Extract title block info from the first page that has one."""
        self._title_block = {"title": "", "date": "", "rev": "", "company": "", "comment": ""}

        # Get project name from Design/Defn
        design_defn = self._root.find("Defn")
        if design_defn is not None:
            self._title_block["title"] = design_defn.get("rootName", "")

        # Build reverse lookup: lowercase alias -> field key
        alias_to_key: dict[str, str] = {}
        for key, aliases in self._TITLE_BLOCK_FIELD_MAP.items():
            for alias in aliases:
                alias_to_key[alias] = key

        # Try to get more info from first page's TitleBlock
        for page_info in self._pages:
            page_elem = page_info["element"]
            tb = page_elem.find("TitleBlock")
            if tb is None:
                continue

            for prop in tb.findall("TitleBlockUserProp"):
                prop_defn = prop.find("Defn")
                if prop_defn is None:
                    continue
                pname = prop_defn.get("name", "").lower().strip()
                pval = prop_defn.get("val", "")
                if not pval:
                    continue

                # Exact match first
                key = alias_to_key.get(pname)
                if key is None:
                    # Substring match: check if any alias is contained in pname,
                    # but require word boundary to avoid false positives (e.g. "date" matching "validate")
                    for alias, mapped_key in alias_to_key.items():
                        if alias in pname and (pname == alias or '_' in pname or pname.endswith(alias)):
                            key = mapped_key
                            break

                if key == "title" and self._title_block.get("title"):
                    # Don't override rootName with empty/generic title
                    continue
                if key:
                    self._title_block[key] = pval
            break  # Only need first title block

    def _build_connectivity(self) -> None:
        """Build pin-to-net mapping via coordinate matching.

        This is the core algorithm: match pin absolute coordinates to wire endpoints,
        Global symbol positions, and OffPageConnector positions.
        """
        # Build coordinate → net mapping
        # Key: (page_index, x, y), Value: net name or net_id
        coord_to_net: dict[tuple[int, int, int], str] = {}
        net_id_to_name: dict[int, str] = {}
        unnamed_counter = 0
        coord_conflicts: list[tuple[tuple[int, int, int], str, str]] = []

        # Step 1: Register all wire endpoints with their net
        for net_data in self._nets_data:
            for wire in net_data.wires:
                for wx, wy in ((wire.start_x, wire.start_y), (wire.end_x, wire.end_y)):
                    key = (net_data.page_index, wx, wy)
                    new_val = f"__net_{net_data.net_id}"
                    existing = coord_to_net.get(key)
                    if existing is not None and existing != new_val:
                        coord_conflicts.append((key, existing, new_val))
                    coord_to_net[key] = new_val

        # Step 2: Register Global symbols — they create named nets at their connection points
        # Globals with the same name across pages are the same net
        for glob in self._globals:
            glob_net_name = glob.name
            conn_x, conn_y = self._get_symbol_connection_point(
                glob.loc_x, glob.loc_y, glob.symbol_name,
                rotation=glob.rotation, mirror=glob.mirror,
            )
            coord_to_net[(glob.page_index, conn_x, conn_y)] = glob_net_name
            # Also propagate: find which internal net this global connects to
            _matched = False
            for net_data in self._nets_data:
                if _matched:
                    break
                if net_data.page_index != glob.page_index:
                    continue
                for wire in net_data.wires:
                    if ((wire.start_x == conn_x and wire.start_y == conn_y) or
                            (wire.end_x == conn_x and wire.end_y == conn_y)):
                        # This net connects to this global — assign the global's name
                        net_id_to_name[net_data.net_id] = glob_net_name
                        _matched = True
                        break

        # Step 3: Register OffPageConnectors — same name across pages = same net
        for opc in self._offpage:
            opc_net_name = opc.name
            conn_x, conn_y = self._get_symbol_connection_point(
                opc.loc_x, opc.loc_y, opc.symbol_name,
                rotation=opc.rotation, mirror=opc.mirror,
            )
            coord_to_net[(opc.page_index, conn_x, conn_y)] = opc_net_name
            _matched = False
            for net_data in self._nets_data:
                if _matched:
                    break
                if net_data.page_index != opc.page_index:
                    continue
                for wire in net_data.wires:
                    if ((wire.start_x == conn_x and wire.start_y == conn_y) or
                            (wire.end_x == conn_x and wire.end_y == conn_y)):
                        net_id_to_name[net_data.net_id] = opc_net_name
                        _matched = True
                        break

        # Step 4: Assign names from Alias labels
        for net_data in self._nets_data:
            if net_data.name and net_data.net_id not in net_id_to_name:
                net_id_to_name[net_data.net_id] = net_data.name

        # Step 5: Auto-generate names for unnamed nets
        for net_data in self._nets_data:
            if net_data.net_id not in net_id_to_name:
                unnamed_counter += 1
                net_id_to_name[net_data.net_id] = f"Net_{unnamed_counter:04d}"

        # Step 6: Update coord_to_net with resolved names
        for net_data in self._nets_data:
            resolved_name = net_id_to_name.get(net_data.net_id, f"Net_{net_data.net_id}")
            for wire in net_data.wires:
                coord_to_net[(net_data.page_index, wire.start_x, wire.start_y)] = resolved_name
                coord_to_net[(net_data.page_index, wire.end_x, wire.end_y)] = resolved_name

        # Step 7: Match pins to nets
        self._pin_net_map = {}
        unmatched_pins: list[tuple[str, str]] = []  # Track unmatched pins: (ref, pin_name)
        for part in self._parts:
            ref = part.reference.upper()
            if ref not in self._pin_net_map:
                self._pin_net_map[ref] = {}

            for pin in part.pins:
                if pin.is_no_connect:
                    continue

                # Look up pin's absolute coordinate in the net map
                net_name = coord_to_net.get((part.page_index, pin.abs_x, pin.abs_y))
                if net_name:
                    self._pin_net_map[ref][pin.name] = net_name
                else:
                    unmatched_pins.append((ref, pin.name))

        # Store unmatched pins count for warning
        self._unmatched_pin_count = len(unmatched_pins)

        # Store resolved net names for later
        self._net_id_to_name = net_id_to_name

        # Store coordinate conflicts for diagnostics
        self._coord_conflicts = coord_conflicts

    def _is_dnp_component(self, properties: dict[str, str], value: str = "") -> bool:
        """Check if component is marked DNP via properties or value.

        Detection strategy (two dimensions):
        1. Property-based: match PartInstUserProp against _CADENCE_DNP_PROP_RULES
        2. Value-based: check if component value is a known DNP marker

        Rules are data-driven — extend _CADENCE_DNP_PROP_RULES and
        _CADENCE_DNP_VALUE_MARKERS at module level to support new conventions
        without modifying this method.
        """
        # Dimension 1: property-based detection
        for prop_key, prop_val in properties.items():
            key_upper = prop_key.strip().upper()
            val_upper = prop_val.strip().upper()
            for rule_name, rule_values in _CADENCE_DNP_PROP_RULES:
                if key_upper == rule_name.upper() and val_upper in rule_values:
                    return True

        # Dimension 2: value-based detection
        if value and value.strip().upper() in _CADENCE_DNP_VALUE_MARKERS:
            return True

        return False

    def _parse_assembly_flags(self, properties: dict[str, str], value: str = "") -> dict[str, bool]:
        """Parse assembly/BOM flags from PartInstUserProp and component value.

        Replaces the hardcoded all-True defaults with values derived from
        the component's actual OrCAD properties and value field.
        """
        dnp = self._is_dnp_component(properties, value)
        return {
            "dnp": dnp,
            "in_bom": not dnp,
            "on_board": not dnp,
            "exclude_from_sim": dnp,
        }

    def _filter_dnp(self, components: list[SchematicComponent]) -> list[SchematicComponent]:
        """Return only populated components (DNP excluded)."""
        return [c for c in components if not c.flags.get("dnp", False)]

    def _build_components(self) -> None:
        """Build SchematicComponent list from parsed parts.

        All components are retained with correct assembly flags.
        DNP filtering is deferred to public methods (get_components, etc.).
        """
        self._components = []
        # Merge multi-part components (same reference, different deviceDesignator)
        ref_parts: dict[str, list[_PartData]] = {}
        for part in self._parts:
            ref = part.reference.upper()
            if ref not in ref_parts:
                ref_parts[ref] = []
            ref_parts[ref].append(part)

        for ref, parts in ref_parts.items():
            # Use first part as primary
            primary = parts[0]

            # Merge pins from all sections
            all_pins: list[dict[str, Any]] = []
            for part in parts:
                for pin in part.pins:
                    all_pins.append({
                        "number": pin.position_index,
                        "name": pin.name,
                        "electrical_type": pin.pin_type,
                    })

            # Merge properties
            merged_props = dict(primary.properties)
            for part in parts[1:]:
                for k, v in part.properties.items():
                    if k not in merged_props:
                        merged_props[k] = v

            # Extract MPN (prefer explicit MPN field, fallback to Manufacturer Part Number)
            mpn = (merged_props.get("MPN", "") or
                   merged_props.get("Manufacturer Part Number", ""))

            # Build properties dict matching KiCad convention
            props = dict(merged_props)
            if mpn:
                # Remove Manufacturer Part Number if it duplicates MPN
                if props.get("Manufacturer Part Number") == mpn:
                    del props["Manufacturer Part Number"]
                # Remove MPN from properties if it duplicates component value (common for ICs)
                if primary.value == mpn and "MPN" in props:
                    del props["MPN"]
                else:
                    props["MPN"] = mpn

            lib_id = primary.lib_name.split("\\")[-1] if primary.lib_name else ""
            if primary.pkg_name:
                lib_id = f"{lib_id}:{primary.pkg_name}" if lib_id else primary.pkg_name

            # Parse flags from properties + value (no longer hardcoded)
            flags = self._parse_assembly_flags(merged_props, value=primary.value)

            self._components.append(SchematicComponent(
                reference=ref,
                value=primary.value,
                library_id=lib_id,
                footprint=primary.footprint,
                properties=props,
                position=(float(primary.loc_x), float(primary.loc_y)),
                unit=None,
                pins=all_pins,
                flags=flags,
            ))

    def _build_nets(self) -> None:
        """Build SchematicNet list from parsed net data."""
        self._nets = []
        seen_names: set[str] = set()
        code = 0

        # Pre-build reverse index: net_name -> list of (ref, pin_name)
        net_to_pins: dict[str, list[str]] = {}
        for ref, pin_nets in self._pin_net_map.items():
            for pin_name, net_name in pin_nets.items():
                net_to_pins.setdefault(net_name, []).append(f"{ref}.{pin_name}")

        # Named nets from resolved mapping
        for net_data in self._nets_data:
            name = self._net_id_to_name.get(net_data.net_id, "")
            if not name or name in seen_names:
                continue
            seen_names.add(name)

            # Determine net type
            net_type = "local"
            # Check if it's a global (power) net
            for glob in self._globals:
                if glob.name == name:
                    net_type = "power"
                    break
            # Check if it's a cross-page signal
            if net_type == "local":
                for opc in self._offpage:
                    if opc.name == name:
                        net_type = "global"
                        break

            # Position from first wire of first net with this name
            pos = (0.0, 0.0)
            if net_data.wires:
                pos = (float(net_data.wires[0].start_x), float(net_data.wires[0].start_y))

            pins = net_to_pins.get(name, [])
            self._nets.append(SchematicNet(
                name=name,
                code=code,
                type=net_type,
                position=pos,
                node_count=len(pins),
                pins=pins,
            ))
            code += 1

        # Add global nets that may not have appeared in NetScalar
        for glob in self._globals:
            if glob.name not in seen_names:
                seen_names.add(glob.name)
                pins = net_to_pins.get(glob.name, [])
                self._nets.append(SchematicNet(
                    name=glob.name,
                    code=code,
                    type="power",
                    position=(float(glob.loc_x), float(glob.loc_y)),
                    node_count=len(pins),
                    pins=pins,
                ))
                code += 1

        # Add off-page nets not yet seen
        for opc in self._offpage:
            if opc.name not in seen_names:
                seen_names.add(opc.name)
                self._nets.append(SchematicNet(
                    name=opc.name,
                    code=code,
                    type="global",
                    position=(float(opc.loc_x), float(opc.loc_y)),
                ))
                code += 1

    # ---- Public interface (matches KiCad SchematicParser) ----

    def get_components(self) -> list[SchematicComponent]:
        """Return populated components only.

        DNP components are filtered out so downstream analysis reflects the
        populated board. Use get_dnp_count() to report how many were excluded.
        """
        self._ensure_parsed()
        return self._filter_dnp(self._components)

    def get_dnp_count(self) -> int:
        """Return the number of DNP components excluded by get_components()."""
        self._ensure_parsed()
        return sum(1 for c in self._components if c.flags.get("dnp", False))

    def get_nets(self) -> list[SchematicNet]:
        """Get all nets from the schematic."""
        self._ensure_parsed()
        return list(self._nets)

    def get_sheets(self) -> list[dict[str, str]]:
        """Get sheet/page list. Cadence XML has all pages in one file."""
        self._ensure_parsed()
        return [
            {"name": p["name"], "file": str(self.file_path)}
            for p in self._pages
        ]

    def get_sheet_instance_records(self) -> list[dict[str, str]]:
        """Get sheet instance records. For Cadence flat designs, return page records."""
        self._ensure_parsed()
        records = []
        for p in self._pages:
            records.append({
                "sheet_name": p["name"],
                "sheet_file": self.file_path.name,
                "sheet_uuid": str(p["index"]),
                "sheet_uuid_path": f"/{p['index']}",
                "sheet_name_path": f"/{p['name']}",
                "source_schematic": str(self.file_path),
            })
        return records

    def get_title_block(self) -> dict[str, str]:
        """Get title block information."""
        self._ensure_parsed()
        return dict(self._title_block)

    def get_sheet_instances(self) -> list[str]:
        """Get sheet instance paths."""
        self._ensure_parsed()
        return ["/"] + [f"/{p['name']}" for p in self._pages]

    def get_component_by_reference(self, reference: str) -> Optional[SchematicComponent]:
        """Find component by reference designator."""
        self._ensure_parsed()
        ref_upper = reference.upper()
        for comp in self._filter_dnp(self._components):
            if comp.reference.upper() == ref_upper:
                return comp
        return None

    def search_components(self, pattern: str) -> list[SchematicComponent]:
        """Search populated components by text pattern (matches reference, value, properties)."""
        self._ensure_parsed()
        pattern_lower = pattern.lower()
        results = []
        for comp in self._components:
            if (pattern_lower in comp.reference.lower() or
                    pattern_lower in comp.value.lower() or
                    any(pattern_lower in v.lower() for v in comp.properties.values())):
                results.append(comp)
        return self._filter_dnp(results)

    def get_component_connections(self, reference: str) -> dict[str, Any]:
        """Get pin-to-net connections for a component."""
        self._ensure_parsed()
        ref_upper = reference.upper()
        pin_nets = self._pin_net_map.get(ref_upper, {})
        comp = self.get_component_by_reference(reference)
        if comp is None:
            return {"error": f"Component {reference} not found"}

        return {
            "reference": ref_upper,
            "value": comp.value,
            "pins": pin_nets,
            "net_count": len(set(pin_nets.values())),
        }

    def get_page_connectivity_entities(self) -> list[dict[str, Any]]:
        """Return connectivity entities (globals, off-page connectors) for synthesis."""
        self._ensure_parsed()
        entities = []

        for glob in self._globals:
            entities.append({
                "kind": "global",
                "name": glob.name,
                "position": (float(glob.loc_x), float(glob.loc_y)),
                "page_index": glob.page_index,
                "symbol_name": glob.symbol_name,
            })

        for opc in self._offpage:
            entities.append({
                "kind": "global",  # Treat as global for synthesis compatibility
                "name": opc.name,
                "position": (float(opc.loc_x), float(opc.loc_y)),
                "page_index": opc.page_index,
                "symbol_name": opc.symbol_name,
            })

        return entities

    def find_connected_entities(self, anchor_names: set[str]) -> list[dict[str, Any]]:
        """Find connectivity entities matching the given net names."""
        self._ensure_parsed()
        all_entities = self.get_page_connectivity_entities()
        return [e for e in all_entities if e["name"] in anchor_names]

    # ---- Cadence-specific accessors ----

    def get_pin_net_map(self) -> dict[str, dict[str, str]]:
        """Get the complete pin-to-net mapping. {ref: {pin_name: net_name}}"""
        self._ensure_parsed()
        return dict(self._pin_net_map)

    def get_unmatched_pin_count(self) -> int:
        """Get the number of pins that could not be matched to any net via coordinate matching.

        This is a quality metric for XML coordinate matching. A high count may indicate
        coordinate misalignment or missing wire connections.
        """
        self._ensure_parsed()
        return self._unmatched_pin_count

    def get_page_count(self) -> int:
        """Get number of schematic pages."""
        self._ensure_parsed()
        return len(self._pages)

    def get_page_names(self) -> list[str]:
        """Get ordered list of page names."""
        self._ensure_parsed()
        return [p["name"] for p in self._pages]

    def get_components_on_page(self, page_index: int) -> list[SchematicComponent]:
        """Get populated components on a specific page."""
        self._ensure_parsed()
        page_refs = set()
        for part in self._parts:
            if part.page_index == page_index:
                page_refs.add(part.reference.upper())
        page_components = [c for c in self._components if c.reference.upper() in page_refs]
        return self._filter_dnp(page_components)
