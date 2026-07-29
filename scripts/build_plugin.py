#!/usr/bin/env python3
"""Build and validate the dual Codex and Claude plugin archive."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

from run_evaluations import RUNTIME_MANIFEST, SKILL_NAME


ROOT = Path(__file__).resolve().parents[1]
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CODEX_MARKETPLACE_PLUGIN = ROOT / "plugins" / SKILL_NAME
CODEX_MANIFEST = CODEX_MARKETPLACE_PLUGIN / ".codex-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
SKILL_ROOT = ROOT / "skills" / SKILL_NAME
DIST = ROOT / "dist"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class PluginBuildError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate without keeping build output",
    )
    parser.add_argument(
        "--expect-version",
        help="Fail unless the manifest version matches this release version",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PluginBuildError(f"{path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise PluginBuildError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def validate_source(expect_version: str | None = None) -> str:
    codex = load_json(CODEX_MANIFEST)
    codex_marketplace = load_json(CODEX_MARKETPLACE)
    claude = load_json(CLAUDE_MANIFEST)
    marketplace = load_json(CLAUDE_MARKETPLACE)
    codex_plugin_entries = codex_marketplace.get("plugins")
    if not isinstance(codex_plugin_entries, list) or len(codex_plugin_entries) != 1:
        raise PluginBuildError("Codex marketplace must contain exactly one plugin")
    codex_marketplace_plugin = codex_plugin_entries[0]
    if not isinstance(codex_marketplace_plugin, dict):
        raise PluginBuildError("Codex marketplace plugin entry must be an object")
    plugin_entries = marketplace.get("plugins")
    if not isinstance(plugin_entries, list) or len(plugin_entries) != 1:
        raise PluginBuildError("Claude marketplace must contain exactly one plugin")
    marketplace_plugin = plugin_entries[0]
    if not isinstance(marketplace_plugin, dict):
        raise PluginBuildError("Claude marketplace plugin entry must be an object")

    names = {
        codex.get("name"),
        codex_marketplace_plugin.get("name"),
        claude.get("name"),
        marketplace_plugin.get("name"),
        SKILL_NAME,
    }
    if names != {SKILL_NAME}:
        raise PluginBuildError("plugin and skill names do not match")
    versions = {
        codex.get("version"),
        claude.get("version"),
        marketplace_plugin.get("version"),
    }
    if len(versions) != 1:
        raise PluginBuildError("Codex, Claude, and marketplace versions do not match")
    version = versions.pop()
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise PluginBuildError("plugin version must be strict semantic versioning")
    if expect_version is not None and version != expect_version:
        raise PluginBuildError(
            f"release version {expect_version!r} does not match manifest {version!r}"
        )

    required_codex = ("description", "author", "skills", "interface")
    missing_codex = [key for key in required_codex if not codex.get(key)]
    if missing_codex:
        raise PluginBuildError(
            "Codex manifest is missing: " + ", ".join(missing_codex)
        )
    interface = codex["interface"]
    interface_required = (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "defaultPrompt",
    )
    if not isinstance(interface, dict):
        raise PluginBuildError("Codex interface must be an object")
    missing_interface = [key for key in interface_required if not interface.get(key)]
    if missing_interface:
        raise PluginBuildError(
            "Codex interface is missing: " + ", ".join(missing_interface)
        )
    prompts = interface["defaultPrompt"]
    if (
        not isinstance(prompts, list)
        or not prompts
        or len(prompts) > 3
        or any(not isinstance(prompt, str) or len(prompt) > 128 for prompt in prompts)
    ):
        raise PluginBuildError(
            "Codex defaultPrompt must contain one to three strings of 128 characters or fewer"
        )
    if codex.get("skills") != "./skills/" or claude.get("skills") != "./skills/":
        raise PluginBuildError("plugin skill paths must use ./skills/")
    codex_source = codex_marketplace_plugin.get("source")
    if codex_marketplace.get("name") != SKILL_NAME:
        raise PluginBuildError("Codex marketplace name must match the plugin")
    if codex_source != {
        "source": "local",
        "path": f"./plugins/{SKILL_NAME}",
    }:
        raise PluginBuildError("Codex marketplace must load its plugin wrapper")
    if codex_marketplace_plugin.get("policy") != {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }:
        raise PluginBuildError("Codex marketplace policy is invalid")
    wrapper_skills = CODEX_MARKETPLACE_PLUGIN / "skills"
    if wrapper_skills.resolve() != (ROOT / "skills").resolve():
        raise PluginBuildError("Codex wrapper must use the canonical skills")
    if marketplace_plugin.get("source") != "./":
        raise PluginBuildError("Claude marketplace must load the repository root")

    for relative in RUNTIME_MANIFEST:
        source = SKILL_ROOT / relative
        if not source.is_file() or source.is_symlink():
            raise PluginBuildError(f"invalid package source: {source.relative_to(ROOT)}")
    for source in (ROOT / "LICENSE", ROOT / "PRIVACY.md", ROOT / "TERMS.md"):
        if not source.is_file():
            raise PluginBuildError(f"missing package source: {source.relative_to(ROOT)}")
    return version


def build_plugin(version: str) -> tuple[Path, Path]:
    plugin_root = DIST / SKILL_NAME
    if plugin_root.exists():
        shutil.rmtree(plugin_root)
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    (plugin_root / ".claude-plugin").mkdir(parents=True)
    packaged_skill = plugin_root / "skills" / SKILL_NAME
    packaged_skill.mkdir(parents=True)

    shutil.copy2(CODEX_MANIFEST, plugin_root / ".codex-plugin" / "plugin.json")
    shutil.copy2(CLAUDE_MANIFEST, plugin_root / ".claude-plugin" / "plugin.json")
    for relative in RUNTIME_MANIFEST:
        source = SKILL_ROOT / relative
        target = packaged_skill / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for name in ("LICENSE", "PRIVACY.md", "TERMS.md"):
        shutil.copy2(ROOT / name, plugin_root / name)

    archive = DIST / f"{SKILL_NAME}-plugin-{version}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for path in sorted(plugin_root.rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(DIST))
    return plugin_root, archive


def validate_build(plugin_root: Path, archive: Path) -> None:
    expected = {
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        "LICENSE",
        "PRIVACY.md",
        "TERMS.md",
        *{f"skills/{SKILL_NAME}/{relative}" for relative in RUNTIME_MANIFEST},
    }
    actual = {
        path.relative_to(plugin_root).as_posix()
        for path in plugin_root.rglob("*")
        if path.is_file()
    }
    if actual != expected:
        raise PluginBuildError(
            f"unexpected package files: expected {sorted(expected)}, found {sorted(actual)}"
        )
    packaged_skill = plugin_root / "skills" / SKILL_NAME
    for relative in RUNTIME_MANIFEST:
        if (packaged_skill / relative).read_bytes() != (SKILL_ROOT / relative).read_bytes():
            raise PluginBuildError(f"packaged skill differs: {relative}")
    if not zipfile.is_zipfile(archive):
        raise PluginBuildError("plugin archive is not a valid ZIP file")
    with zipfile.ZipFile(archive) as source:
        archived = {name for name in source.namelist() if not name.endswith("/")}
    expected_archived = {f"{SKILL_NAME}/{path}" for path in expected}
    if archived != expected_archived:
        raise PluginBuildError("plugin archive contents do not match the package")


def main() -> int:
    args = parse_args()
    try:
        version = validate_source(args.expect_version)
        plugin_root, archive = build_plugin(version)
        validate_build(plugin_root, archive)
    except PluginBuildError as error:
        print(f"error: {error}")
        return 1
    print(f"Built {archive.relative_to(ROOT)}")
    if args.check:
        shutil.rmtree(DIST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
