"""Connectivity graph builder for hierarchical schematic projects."""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .kicad.netlist_parser import NetlistParser
from .constants import DEFAULT_NET_TYPE, FORMAT_CADENCE, KICAD_CLI_TIMEOUT
from .project_indexer import ProjectIndex


@dataclass
class NetConnection:
    """Connectivity for a single net."""

    net_name: str
    net_code: int | None
    net_type: str
    connected_refs: list[str] = field(default_factory=list)
    connected_pins: list[tuple[str, str, str]] = field(default_factory=list)


@dataclass
class ConnectivityGraph:
    """Unified project connectivity keyed by net name."""

    all_nets: dict[str, NetConnection]
    netlist_available: bool
    resolver: object
    component_nets: dict[str, dict] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class ConnectivityBuilder:
    """Build root-netlist connectivity for one hierarchical project."""

    def __init__(self, classify_net_type: Optional[object] = None) -> None:
        del classify_net_type

    def build(self, project_index: ProjectIndex, root_schematic: str | Path) -> ConnectivityGraph:
        root_path = Path(root_schematic).resolve()

        # Use Cadence connectivity builder for Cadence projects
        if getattr(project_index.scope, "format", "kicad") == FORMAT_CADENCE:
            from .cadence.connectivity import CadenceConnectivityBuilder
            return CadenceConnectivityBuilder().build(project_index, root_path)

        all_nets: dict[str, NetConnection] = {}
        component_nets: dict[str, dict] = {}
        warnings: list[str] = []

        netlist_path = self._export_netlist(root_path)
        if netlist_path is None:
            return ConnectivityGraph(
                all_nets={},
                netlist_available=False,
                resolver=project_index.resolver,
                component_nets={},
                warnings=["kicad-cli netlist export unavailable"],
            )

        netlist_parser = NetlistParser(str(netlist_path))
        netlist_data = netlist_parser._parse_file()
        # Clean up temp file after parsing
        try:
            netlist_path.unlink(missing_ok=True)
        except OSError:
            pass
        warnings.extend(netlist_data.get("warnings", []))

        for reference, component in netlist_data.get("components", {}).items():
            component_nets[reference] = {
                "pins": dict(component.pins),
                "pin_count": len(component.pins),
                "reference": component.reference,
                "sheet_path": component.sheet_instance_path,
            }

        for net_name, net in netlist_data.get("nets", {}).items():
            connected_refs = list(dict.fromkeys(reference for reference, _pin in net.pins))
            connected_pins = [(reference, pin, "") for reference, pin in net.pins]
            all_nets[net_name] = NetConnection(
                net_name=net_name,
                net_code=net.code,
                net_type=DEFAULT_NET_TYPE,
                connected_refs=connected_refs,
                connected_pins=connected_pins,
            )

        return ConnectivityGraph(
            all_nets=all_nets,
            netlist_available=True,
            resolver=project_index.resolver,
            component_nets=component_nets,
            warnings=warnings,
        )

    def _export_netlist(self, root_schematic: Path) -> Optional[Path]:
        fd, temp_path = tempfile.mkstemp(suffix=".xml")
        os.close(fd)
        try:
            result = subprocess.run(
                [
                    "kicad-cli",
                    "sch",
                    "export",
                    "netlist",
                    "--format",
                    "kicadxml",
                    "-o",
                    temp_path,
                    str(root_schematic),
                ],
                capture_output=True,
                text=True,
                timeout=KICAD_CLI_TIMEOUT,
                check=False,
            )
        except FileNotFoundError:
            Path(temp_path).unlink(missing_ok=True)
            return None
        except Exception:
            Path(temp_path).unlink(missing_ok=True)
            return None

        if result.returncode != 0:
            Path(temp_path).unlink(missing_ok=True)
            return None
        return Path(temp_path)
