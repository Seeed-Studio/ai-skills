"""Project scope resolution for KiCad and Cadence schematics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectScope:
    """Resolved project scope for one input path."""

    root_schematic: Path
    project_name: str
    referenced_sheets: list[Path]
    is_hierarchical: bool
    scope_type: str
    format: str = "kicad"  # "kicad" or "cadence"


class ScopeResolver:
    """Resolve root schematic and analysis scope deterministically."""

    @classmethod
    def resolve(cls, path: str | Path) -> ProjectScope:
        input_path = Path(path).resolve()
        root_schematic, scope_type, fmt = cls._resolve_root_schematic(input_path)
        project_name = cls._resolve_project_name(input_path, root_schematic, fmt)
        referenced_sheets = cls._collect_referenced_sheets(root_schematic, fmt)

        return ProjectScope(
            root_schematic=root_schematic,
            project_name=project_name,
            referenced_sheets=referenced_sheets,
            is_hierarchical=bool(referenced_sheets),
            scope_type=scope_type,
            format=fmt,
        )

    @classmethod
    def find_schematic(cls, path: str | Path) -> Path:
        """Compatibility wrapper returning the resolved root schematic."""
        root_schematic, _scope_type, _fmt = cls._resolve_root_schematic(Path(path).resolve())
        return root_schematic

    @classmethod
    def _resolve_root_schematic(cls, input_path: Path) -> tuple[Path, str, str]:
        if input_path.is_file():
            if input_path.suffix == ".kicad_sch":
                return input_path.resolve(), cls._scope_type_for_schematic(input_path.resolve()), "kicad"
            if input_path.suffix == ".kicad_pro":
                project_schematic = input_path.with_suffix(".kicad_sch")
                if project_schematic.exists():
                    return project_schematic.resolve(), "directory", "kicad"
                return cls._resolve_root_schematic(input_path.parent.resolve())
            # Check for Cadence XML
            if input_path.suffix.lower() == ".xml":
                from .cadence.xml_parser import is_cadence_xml
                if is_cadence_xml(input_path):
                    return input_path.resolve(), "flat", "cadence"

            # Check for Cadence netlist .dat file — resolve via parent directory
            if input_path.suffix.lower() == ".dat":
                # Walk up to find the project directory (skip netlist subdirectory)
                return cls._resolve_root_schematic(input_path.parent.parent.resolve())

            raise ValueError(f"Not a supported schematic file: {input_path}")

        if input_path.is_dir():
            # Try KiCad first
            schematics = sorted(candidate.resolve() for candidate in input_path.glob("*.kicad_sch"))
            if schematics:
                # Existing KiCad directory logic
                project_files = sorted(input_path.glob("*.kicad_pro"))
                if len(project_files) == 1:
                    project_schematic = input_path / f"{project_files[0].stem}.kicad_sch"
                    if project_schematic.exists():
                        return project_schematic.resolve(), "directory", "kicad"

                hierarchical_roots: list[tuple[int, int, Path]] = []
                for schematic in schematics:
                    content = schematic.read_text(encoding="utf-8", errors="ignore")
                    sheet_instances = content.count("(sheet_instances")
                    sheet_count = content.count("(sheet\n") + content.count("(sheet\r\n")
                    if sheet_instances:
                        hierarchical_roots.append((sheet_instances, sheet_count, schematic))

                if hierarchical_roots:
                    hierarchical_roots.sort(key=lambda item: (item[0], item[1], item[2].name))
                    return hierarchical_roots[-1][2], "directory", "kicad"

                schematics_by_sheet_count: list[tuple[int, Path]] = []
                for schematic in schematics:
                    content = schematic.read_text(encoding="utf-8", errors="ignore")
                    schematics_by_sheet_count.append(
                        (content.count("(sheet\n") + content.count("(sheet\r\n"), schematic)
                    )
                schematics_by_sheet_count.sort(key=lambda item: (item[0], item[1].name))
                if schematics_by_sheet_count[-1][0] > 0:
                    return schematics_by_sheet_count[-1][1], "directory", "kicad"

                return schematics[0], "directory", "kicad"

            # Try Cadence XML
            from .cadence.xml_parser import is_cadence_xml
            for xml_file in sorted(input_path.glob("*.xml")):
                if is_cadence_xml(xml_file):
                    return xml_file.resolve(), "flat", "cadence"

            # Try Cadence netlist directory (contains pstxnet.dat etc.)
            from .cadence.netlist_dat_parser import find_netlist_dir
            netlist_dir = find_netlist_dir(input_path)
            if netlist_dir is not None:
                # Look for a companion .xml in the netlist dir or its parent
                search_dirs = [netlist_dir, netlist_dir.parent]
                for search_dir in search_dirs:
                    from .cadence.xml_parser import is_cadence_xml
                    for xml_file in sorted(search_dir.glob("*.xml")):
                        if is_cadence_xml(xml_file):
                            return xml_file.resolve(), "flat", "cadence"
                # No XML found — return the netlist dir itself
                return netlist_dir.resolve(), "flat", "cadence"

            raise FileNotFoundError(f"No supported schematic files in: {input_path}")

        raise FileNotFoundError(f"Path not found: {input_path}")

    @classmethod
    def _resolve_project_name(cls, input_path: Path, root_schematic: Path, fmt: str) -> str:
        if fmt == "cadence":
            # For Cadence, use the XML filename stem
            return root_schematic.stem

        if input_path.is_file() and input_path.suffix == ".kicad_pro":
            return input_path.stem

        project_files = sorted(root_schematic.parent.glob("*.kicad_pro"))
        if len(project_files) == 1:
            return project_files[0].stem

        return root_schematic.stem

    @classmethod
    def _collect_referenced_sheets(cls, root_schematic: Path, fmt: str) -> list[Path]:
        if fmt == "cadence":
            # Cadence XML contains all pages in one file — no child sheets
            return []

        referenced: list[Path] = []
        seen: set[Path] = set()

        def visit(schematic_file: Path, active_files: set[Path]) -> None:
            from .kicad.schematic_parser import SchematicParser
            parser = SchematicParser(str(schematic_file), include_child_sheets=False)
            for sheet in parser.get_sheets():
                sheet_file = sheet.get("file", "")
                if not sheet_file:
                    continue
                child_path = (schematic_file.parent / sheet_file).resolve()
                if not child_path.exists():
                    continue
                if child_path not in seen:
                    referenced.append(child_path)
                    seen.add(child_path)
                if child_path in active_files:
                    continue
                visit(child_path, active_files | {child_path})

        visit(root_schematic.resolve(), {root_schematic.resolve()})
        return referenced

    @classmethod
    def _scope_type_for_schematic(cls, schematic_path: Path) -> str:
        from .kicad.schematic_parser import SchematicParser
        parser = SchematicParser(str(schematic_path), include_child_sheets=False)
        return "hierarchy" if parser.get_sheets() else "flat"
