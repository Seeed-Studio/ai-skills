"""Project indexing for ERC-clean hierarchical schematics."""

from __future__ import annotations

import re as _re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .parser_factory import get_schematic_parser
from .scope_resolver import ProjectScope, ScopeResolver


class UnknownReferenceError(KeyError):
    """Raised when a reference cannot be resolved."""


@dataclass(frozen=True)
class ComponentInstance:
    """One unique component in the project hierarchy."""

    reference: str
    instance_id: str
    value: str
    lib_id: str
    footprint: Optional[str]
    source_schematic: Path
    sheet_path: str
    sheet_type: str
    pins: list[dict]
    properties: dict[str, str]
    flags: dict[str, bool]

    @property
    def sheet_instance_path(self) -> str:
        return self.sheet_path


@dataclass(frozen=True)
class SheetInfo:
    """Metadata for one page in the hierarchy."""

    sheet_name: str
    sheet_file: str
    sheet_path: str
    sheet_type: str
    component_count: int

    @property
    def sheet_instance_path(self) -> str:
        return self.sheet_path


@dataclass(frozen=True)
class IndexStatistics:
    """Summary counts for the project index."""

    total_components: int
    total_sheets: int
    duplicate_reference_count: int
    dnp_filtered: int = 0


@dataclass
class InstanceResolver:
    """Resolve user-facing references in an ERC-clean project."""

    ref_to_instances: dict[str, list[str]]

    def resolve_ref(
        self,
        ref: str,
        sheet_name: Optional[str] = None,
        sheet_name_to_path: Optional[dict[str, str]] = None,
    ) -> str:
        del sheet_name, sheet_name_to_path
        ref_key = str(ref).upper()
        matches = list(self.ref_to_instances.get(ref_key, ()))
        if not matches:
            raise UnknownReferenceError(ref)
        return matches[0]


@dataclass(frozen=True)
class NetInfo:
    """One unique project net."""

    net_name: str
    net_code: int | None
    net_type: str


@dataclass(frozen=True)
class ProjectIndex:
    """Indexed project structure keyed by reference and net name."""

    scope: ProjectScope
    components: dict[str, ComponentInstance]
    nets: dict[str, NetInfo]
    hierarchy: list[SheetInfo]
    resolver: InstanceResolver
    sheet_name_to_path: dict[str, str]
    statistics: IndexStatistics


class ProjectIndexer:
    """Build a structural project index from the resolved hierarchy only."""

    def build(
        self,
        path: str | Path,
    ) -> ProjectIndex:
        input_path = Path(path).resolve()
        scope = ScopeResolver.resolve(input_path)

        components: dict[str, ComponentInstance] = {}
        hierarchy: list[SheetInfo] = []
        sheet_name_to_path: dict[str, str] = {}
        dnp_filtered = 0

        for record in self._build_sheet_records(scope):
            parser = get_schematic_parser(str(record.file_path), include_child_sheets=False)
            local_components = parser.get_components()
            dnp_filtered += parser.get_dnp_count()
            hierarchy.append(
                SheetInfo(
                    sheet_name=record.sheet_name,
                    sheet_file=record.file_path.name,
                    sheet_path=record.sheet_path,
                    sheet_type=record.sheet_type,
                    component_count=len(local_components),
                )
            )
            sheet_name_to_path[record.sheet_name] = record.sheet_path

            for component in local_components:
                reference = component.reference.upper()
                pins = []
                for pin in component.pins:
                    if isinstance(pin, dict):
                        pins.append({"number": pin.get("number", ""), "name": pin.get("name", "")})
                    else:
                        pins.append(
                            {
                                "number": getattr(pin, "number", ""),
                                "name": getattr(pin, "name", ""),
                            }
                        )

                components[reference] = ComponentInstance(
                    reference=reference,
                    instance_id=reference,
                    value=component.value,
                    lib_id=component.library_id,
                    footprint=component.footprint,
                    source_schematic=record.file_path,
                    sheet_path=record.sheet_path,
                    sheet_type=record.sheet_type,
                    pins=pins,
                    properties=dict(component.properties),
                    flags=dict(component.flags),
                )

        # Cadence: enrich with page info from pstxprt.dat when available
        if scope.format == "cadence":
            enriched = self._enrich_cadence_pages(
                scope, components, hierarchy, sheet_name_to_path
            )
            if enriched is not None:
                components, hierarchy, sheet_name_to_path = enriched

        return ProjectIndex(
            scope=scope,
            components=components,
            nets={},  # TODO: populate from ConnectivityBuilder when integrated
            hierarchy=hierarchy,
            resolver=InstanceResolver({ref: [ref] for ref in sorted(components)}),
            sheet_name_to_path=sheet_name_to_path,
            statistics=IndexStatistics(
                total_components=len(components),
                total_sheets=len(hierarchy),
                duplicate_reference_count=0,  # TODO: compute from actual instance resolution
                dnp_filtered=dnp_filtered,
            ),
        )

    @staticmethod
    def _enrich_cadence_pages(
        scope: ProjectScope,
        components: dict[str, ComponentInstance],
        hierarchy: list[SheetInfo],
        sheet_name_to_path: dict[str, str],
    ) -> (
        tuple[dict[str, ComponentInstance], list[SheetInfo], dict[str, str]] | None
    ):
        """Enrich Cadence project with page info from pstxprt.dat.

        Returns (components, hierarchy, sheet_name_to_path) or None if
        pstxprt.dat is unavailable.
        """
        from .cadence.netlist_dat_parser import find_netlist_dir, parse_pstxprt
        from .parser_factory import get_schematic_parser

        netlist_dir = find_netlist_dir(scope.root_schematic)
        if netlist_dir is None:
            return None
        pstxprt_path = netlist_dir / "pstxprt.dat"
        if not pstxprt_path.exists():
            return None

        part_info = parse_pstxprt(pstxprt_path)
        if not part_info:
            return None

        # Build ref -> page mapping
        ref_to_page: dict[str, str] = {}
        page_refs: dict[str, list[str]] = {}
        for ref, info in part_info.items():
            ref_key = ref.upper()
            if ref_key not in components:
                continue
            page = info.get("page")
            if page:
                ref_to_page[ref_key] = page
                page_refs.setdefault(page, []).append(ref_key)

        if not page_refs:
            return None

        # Sort pages numerically (page5, page6, ...)
        def _page_sort_key(name: str) -> int:
            m = _re.search(r"\d+", name)
            return int(m.group()) if m else 0

        sorted_pages = sorted(page_refs.keys(), key=_page_sort_key)

        # Build pageN → human-readable page name mapping from XML parser
        page_display_names: dict[str, str] = {}
        try:
            xml_parser = get_schematic_parser(str(scope.root_schematic), include_child_sheets=False)
            xml_page_names = xml_parser.get_page_names()
            for raw_page in page_refs:
                m = _re.search(r"\d+", raw_page)
                if m:
                    page_idx = int(m.group()) - 1  # page3 → index 2
                    if 0 <= page_idx < len(xml_page_names):
                        page_display_names[raw_page] = xml_page_names[page_idx]
        except Exception:
            pass

        # Build new hierarchy
        new_hierarchy: list[SheetInfo] = []
        new_sheet_name_to_path: dict[str, str] = {}
        for page_name in sorted_pages:
            display_name = page_display_names.get(page_name, page_name)
            sheet_path = f"/{page_name}"
            new_hierarchy.append(
                SheetInfo(
                    sheet_name=display_name,
                    sheet_file=scope.root_schematic.name,
                    sheet_path=sheet_path,
                    sheet_type="hierarchy",
                    component_count=len(page_refs[page_name]),
                )
            )
            new_sheet_name_to_path[display_name] = sheet_path

        # Reassign component sheet_paths (frozen dataclass — recreate)
        new_components: dict[str, ComponentInstance] = {}
        for ref, comp in components.items():
            page = ref_to_page.get(ref)
            if page:
                new_path = f"/{page}"
            else:
                # Components not in pstxprt.dat: keep on first page
                new_path = new_hierarchy[0].sheet_path if new_hierarchy else "/"
            new_components[ref] = ComponentInstance(
                reference=comp.reference,
                instance_id=comp.instance_id,
                value=comp.value,
                lib_id=comp.lib_id,
                footprint=comp.footprint,
                source_schematic=comp.source_schematic,
                sheet_path=new_path,
                sheet_type="hierarchy",
                pins=comp.pins,
                properties=comp.properties,
                flags=comp.flags,
            )

        return new_components, new_hierarchy, new_sheet_name_to_path

    def _build_sheet_records(self, scope: ProjectScope) -> list["_SheetRecord"]:
        records: list[_SheetRecord] = [
            _SheetRecord(
                sheet_name=scope.project_name,
                file_path=scope.root_schematic,
                sheet_path="/",
                sheet_type="root",
            )
        ]
        if scope.format == "cadence":
            # Cadence XML: all pages in one file, pages reported by get_sheets()
            # but they all reference the same file — no child traversal needed
            return records

        root_parser = get_schematic_parser(str(scope.root_schematic), include_child_sheets=False)
        for sheet in root_parser.get_sheet_instance_records():
            source_schematic = Path(sheet["source_schematic"]).resolve()
            child_file = (source_schematic.parent / sheet["sheet_file"]).resolve()
            if not child_file.exists():
                continue
            records.append(
                _SheetRecord(
                    sheet_name=sheet["sheet_name"],
                    file_path=child_file,
                    sheet_path=sheet["sheet_name_path"],
                    sheet_type="hierarchy",
                )
            )
        return records


@dataclass(frozen=True)
class _SheetRecord:
    """Internal sheet traversal record."""

    sheet_name: str
    file_path: Path
    sheet_path: str
    sheet_type: str
