"""Cadence connectivity builder.

Builds ConnectivityGraph from Cadence data sources. Prefers authoritative
Allegro netlist files (pstxnet.dat) when available, falls back to XML
coordinate-based matching otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..connectivity_builder import ConnectivityGraph, NetConnection
from ..constants import DEFAULT_NET_TYPE
from ..project_indexer import ProjectIndex
from .netlist_dat_parser import find_netlist_dir, build_pin_net_map_from_dat, parse_pstxprt
from .xml_parser import CadenceXMLParser


class CadenceConnectivityBuilder:
    """Build connectivity graph from Cadence data.

    Data source priority:
      1. pstxnet.dat (Allegro netlist) — precise, engine-computed
      2. XML coordinate matching — fallback when .dat files unavailable
    """

    @staticmethod
    def _aggregate_net_pins(pin_net_map: dict[str, dict[str, str]]) -> dict[str, list[tuple[str, str]]]:
        """Aggregate pins per net from pin-net map."""
        net_pins: dict[str, list[tuple[str, str]]] = {}
        for ref, pin_nets in pin_net_map.items():
            for pin_name, net_name in pin_nets.items():
                if net_name not in net_pins:
                    net_pins[net_name] = []
                net_pins[net_name].append((ref, pin_name))
        return net_pins

    @staticmethod
    def _get_pin_net_map(root_path: Path) -> tuple[dict[str, dict[str, str]], str, Optional[CadenceXMLParser], Optional[Path]]:
        """Get pin-net map, preferring .dat files over XML coordinate matching.

        Returns:
            (pin_net_map, source_label, parser_or_none, netlist_dir_or_none)
        """
        # Try authoritative .dat source first — no XML needed for this path
        search_path = root_path.parent if root_path.is_file() else root_path
        netlist_dir = find_netlist_dir(search_path)
        if netlist_dir is not None:
            dat_map = build_pin_net_map_from_dat(netlist_dir)
            if dat_map:
                # Create parser only if needed later (lazy)
                parser = None
                try:
                    parser = CadenceXMLParser(str(root_path))
                except (FileNotFoundError, ValueError):
                    pass
                return dat_map, "pstxnet.dat", parser, netlist_dir

        # Fall back to XML coordinate matching — XML is required here
        parser = CadenceXMLParser(str(root_path))
        return parser.get_pin_net_map(), "xml_coordinate", parser, None

    def build(self, project_index: ProjectIndex, root_schematic: str | Path) -> ConnectivityGraph:
        """Build connectivity from Cadence data.

        Prefers pstxnet.dat when available for precise connectivity,
        falls back to XML coordinate matching otherwise.
        """
        root_path = Path(root_schematic).resolve()
        pin_net_map, source, parser, netlist_dir = self._get_pin_net_map(root_path)

        # Try to load page information from pstxprt.dat
        page_info: dict[str, dict] = {}
        if source == "pstxnet.dat" and netlist_dir is not None:
            pstxprt_file = netlist_dir / "pstxprt.dat"
            if pstxprt_file.exists():
                page_info = parse_pstxprt(pstxprt_file)

        all_nets_data: dict[str, NetConnection] = {}
        component_nets: dict[str, dict] = {}
        warnings: list[str] = []
        if source == "xml_coordinate":
            warnings.append("Using XML coordinate matching (no pstxnet.dat found). "
                          "For higher accuracy, export Allegro netlist.")
            # Add warning for unmatched pins (parser guaranteed non-None for xml_coordinate)
            if parser is not None:
                unmatched_count = parser.get_unmatched_pin_count()
                if unmatched_count > 0:
                    warnings.append(f"XML coordinate matching: {unmatched_count} pins could not be matched to nets. "
                                  "This may indicate coordinate misalignment or incomplete wiring.")

        # Build component_nets from pin-net map
        for ref, pin_nets in pin_net_map.items():
            comp = project_index.components.get(ref)
            # Use page from pstxprt.dat if available, otherwise use XML's sheet_path
            sheet_path = comp.sheet_path if comp else "/"
            if ref in page_info:
                sheet_path = page_info[ref]["page"]

            component_nets[ref] = {
                "pins": dict(pin_nets),
                "pin_count": len(pin_nets),
                "reference": ref,
                "sheet_path": sheet_path,
                "dat_source": source == "pstxnet.dat",
            }

        # Build all_nets: aggregate pins per net
        net_pins = self._aggregate_net_pins(pin_net_map)

        code = 0
        for net_name, pins in net_pins.items():
            connected_refs = list(dict.fromkeys(ref for ref, _ in pins))
            connected_pins_list = [(ref, pin, "") for ref, pin in pins]

            all_nets_data[net_name] = NetConnection(
                net_name=net_name,
                net_code=code,
                net_type=DEFAULT_NET_TYPE,
                connected_refs=connected_refs,
                connected_pins=connected_pins_list,
            )
            code += 1

        return ConnectivityGraph(
            all_nets=all_nets_data,
            netlist_available=True,
            resolver=project_index.resolver,
            component_nets=component_nets,
            warnings=warnings,
        )
