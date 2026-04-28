#!/usr/bin/env python3
"""agentskills - Cross-agent skill synchronization tool.

Manages skills across Claude Code, OpenCode, OpenClaw, and Hermes
using a unified storage directory with symlinks.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# === Configuration ===

AGENT_SKILLS_DIR = Path.home() / ".agent-skills"
METADATA_DIR = AGENT_SKILLS_DIR / ".agentskills"
CONFIG_FILE = METADATA_DIR / "config.json"
REGISTRY_FILE = METADATA_DIR / "registry.json"

AGENT_DIRS = {
    "claude": Path.home() / ".claude" / "skills",
    "opencode": Path.home() / ".config" / "opencode" / "skills",
    "openclaw": Path.home() / ".openclaw" / "workspace" / "skills",
    "hermes": Path.home() / ".hermes" / "skills",
}


# === Helpers ===


def ensure_metadata():
    """Create metadata directory and default files if missing."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(
            {"enabled_agents": list(AGENT_DIRS.keys()), "version": "0.1.0"},
            indent=2,
        ))
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text(json.dumps({}, indent=2))


def load_registry():
    """Load the skill registry."""
    ensure_metadata()
    return json.loads(REGISTRY_FILE.read_text())


def save_registry(registry):
    """Save the skill registry."""
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2))


def list_agent_skills(agent_name):
    """List skill names installed for a given agent."""
    agent_dir = AGENT_DIRS.get(agent_name)
    if not agent_dir or not agent_dir.exists():
        return []
    results = []
    for entry in sorted(agent_dir.iterdir()):
        if entry.is_dir() or entry.is_symlink():
            results.append(entry.name)
    return results


def is_symlink(path):
    """Check if a path is a symlink."""
    return path.is_symlink()


def scan_all_skills():
    """Scan all agent directories.

    Returns dict: {skill_name: {agent: "symlink"|"local", path: Path}}
    """
    skills = {}
    for agent, agent_dir in AGENT_DIRS.items():
        if not agent_dir.exists():
            continue
        for entry in sorted(agent_dir.iterdir()):
            if entry.is_dir() or entry.is_symlink():
                name = entry.name
                if name not in skills:
                    skills[name] = {}
                skills[name][agent] = {
                    "type": "symlink" if is_symlink(entry) else "local",
                    "path": entry,
                }
    return skills


def symlink_skill(agent_name, skill_name):
    """Create a symlink from an agent's skills dir to ~/.agent-skills/<skill>."""
    agent_dir = AGENT_DIRS.get(agent_name)
    if not agent_dir:
        return False
    target = AGENT_SKILLS_DIR / skill_name
    link = agent_dir / skill_name

    if link.exists() or link.is_symlink():
        # Already exists
        return True

    agent_dir.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target)
    return True


def unlink_skill(agent_name, skill_name):
    """Remove a symlink from an agent's skills dir."""
    agent_dir = AGENT_DIRS.get(agent_name)
    if not agent_dir:
        return
    link = agent_dir / skill_name
    if link.is_symlink():
        link.unlink()


# === Commands ===


def cmd_init(args):
    """Initialize the unified skills directory."""
    if AGENT_SKILLS_DIR.exists():
        print(f"[info] {AGENT_SKILLS_DIR} already exists.")
    else:
        AGENT_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[ok] Created {AGENT_SKILLS_DIR}")

    ensure_metadata()
    print(f"[ok] Created metadata at {METADATA_DIR}")

    # Check agent directories
    print("\nAgent directories:")
    for agent, agent_dir in AGENT_DIRS.items():
        status = "exists" if agent_dir.exists() else "missing"
        print(f"  {agent:12s} {agent_dir} [{status}]")


def cmd_sync(args):
    """Synchronize skills from all agents into the unified directory."""
    ensure_metadata()
    registry = load_registry()

    all_skills = scan_all_skills()
    migrated = []
    deduplicated = []
    symlinked = []

    # Phase 1: move local skills to unified storage
    for skill_name, agents in all_skills.items():
        if skill_name in registry:
            continue  # Already managed

        # Find the best copy to keep (prefer non-symlink with latest mtime)
        local_copies = [
            (agent, info)
            for agent, info in agents.items()
            if info["type"] == "local"
        ]
        symlink_agents = [
            agent for agent, info in agents.items() if info["type"] == "symlink"
        ]

        if local_copies:
            # Pick the one with newest mtime
            best_agent, best_info = max(
                local_copies,
                key=lambda x: _get_mtime(x[1]["path"]),
            )

            if len(local_copies) > 1:
                # Dedup: remove older copies
                for agent, info in local_copies:
                    if agent != best_agent:
                        shutil.rmtree(info["path"])
                        deduplicated.append(f"{skill_name} (removed duplicate from {agent})")

            # Move to unified storage
            src = best_info["path"]
            dst = AGENT_SKILLS_DIR / skill_name
            if src != dst:
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.move(str(src), str(dst))
                migrated.append(f"{skill_name} (from {best_agent})")

            # Create symlinks for all agents
            for agent in AGENT_DIRS:
                if symlink_skill(agent, skill_name):
                    symlinked.append(f"{skill_name} -> {agent}")

            registry[skill_name] = {
                "source": best_agent,
                "installed_at": datetime.now().isoformat(),
                "git": (AGENT_SKILLS_DIR / skill_name / ".git").exists(),
            }

        elif symlink_agents:
            # All copies are already symlinks, just ensure all agents have them
            for agent in AGENT_DIRS:
                if agent not in agents and symlink_skill(agent, skill_name):
                    symlinked.append(f"{skill_name} -> {agent}")

    # Phase 2: ensure symlinks for all registry entries
    for skill_name in registry:
        for agent in AGENT_DIRS:
            agent_link = AGENT_DIRS[agent] / skill_name
            if not agent_link.exists() and not agent_link.is_symlink():
                if (AGENT_SKILLS_DIR / skill_name).exists():
                    if symlink_skill(agent, skill_name):
                        symlinked.append(f"{skill_name} -> {agent} (restored)")

    save_registry(registry)

    # Report
    if migrated:
        print(f"\n[migrated] {len(migrated)} skill(s) moved to unified storage:")
        for item in migrated:
            print(f"  - {item}")
    if deduplicated:
        print(f"\n[deduplicated] {len(deduplicated)} duplicate(s) removed:")
        for item in deduplicated:
            print(f"  - {item}")
    if symlinked:
        print(f"\n[symlinked] {len(symlinked)} symlink(s) created:")
        for item in symlinked:
            print(f"  - {item}")
    if not migrated and not deduplicated and not symlinked:
        print("[ok] All skills are already synchronized.")


def _get_mtime(path):
    """Get modification time of a path, handling broken symlinks."""
    try:
        if path.is_symlink():
            return path.resolve().stat().st_mtime
        return path.stat().st_mtime
    except (OSError, FileNotFoundError):
        return 0


def cmd_list(args):
    """List all skills and their status across agents."""
    ensure_metadata()
    registry = load_registry()
    all_skills = scan_all_skills()

    # Combine registry and discovered skills
    all_names = sorted(set(list(registry.keys()) + list(all_skills.keys())))

    if not all_names:
        print("No skills found.")
        return

    agent_names = list(AGENT_DIRS.keys())
    # Column widths
    name_width = max(len(n) for n in all_names) + 2

    header = f"{'SKILL':<{name_width}}" + "".join(f" {a:<12}" for a in agent_names)
    print(header)
    print("-" * len(header))

    for skill_name in all_names:
        row = f"{skill_name:<{name_width}}"
        agents = all_skills.get(skill_name, {})
        for agent in agent_names:
            if agent in agents:
                info = agents[agent]
                if info["type"] == "symlink":
                    row += f" {'✓ symlink':<12}"
                else:
                    row += f" {'⚠ local':<12}"
            else:
                row += f" {'✗ missing':<12}"
        print(row)

    print(f"\nTotal: {len(all_names)} skill(s)")


def cmd_install(args):
    """Install a new skill from URL or local path."""
    ensure_metadata()
    registry = load_registry()

    source = args.source
    skill_name = args.name

    dst = AGENT_SKILLS_DIR / skill_name

    if dst.exists():
        print(f"[skip] Skill '{skill_name}' already installed.")
        return

    if os.path.isdir(source):
        # Local path copy
        print(f"[copy] Installing from local: {source}")
        shutil.copytree(source, str(dst))
    elif source.startswith("http"):
        # Git clone
        print(f"[clone] Cloning: {source}")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", source, str(dst)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"[error] Git clone failed:\n{result.stderr}")
            if dst.exists():
                shutil.rmtree(dst)
            return
    else:
        print(f"[error] Unsupported source: {source}")
        print("  Use a git URL (https://...) or a local directory path.")
        return

    # Verify SKILL.md exists
    skill_md = dst / "SKILL.md"
    if not skill_md.exists():
        # Try to find it in subdirectories
        found = list(dst.rglob("SKILL.md"))
        if found:
            print(f"[warn] SKILL.md found in subdirectory: {found[0].relative_to(dst)}")
        else:
            print(f"[warn] No SKILL.md found in '{skill_name}'. May not be detected by all agents.")

    # Register and symlink
    registry[skill_name] = {
        "source": "manual",
        "url": source if source.startswith("http") else None,
        "installed_at": datetime.now().isoformat(),
        "git": (dst / ".git").exists(),
    }
    save_registry(registry)

    for agent in AGENT_DIRS:
        symlink_skill(agent, skill_name)

    print(f"[ok] Installed '{skill_name}' to {dst}")


def cmd_remove(args):
    """Remove a skill from all agents."""
    ensure_metadata()
    registry = load_registry()
    skill_name = args.skill

    unified = AGENT_SKILLS_DIR / skill_name

    if not unified.exists() and skill_name not in registry:
        print(f"[error] Skill '{skill_name}' not found.")
        return

    # Remove symlinks from all agents
    for agent in AGENT_DIRS:
        unlink_skill(agent, skill_name)

    # Remove from unified storage
    if unified.exists() and not unified.is_symlink():
        shutil.rmtree(unified)
        print(f"[ok] Removed '{skill_name}' from unified storage.")
    elif unified.is_symlink():
        unified.unlink()
        print(f"[ok] Removed symlink '{skill_name}'.")

    # Update registry
    registry.pop(skill_name, None)
    save_registry(registry)


def cmd_status(args):
    """Show status of all skills."""
    ensure_metadata()
    registry = load_registry()
    all_skills = scan_all_skills()

    issues = []

    # Check for broken symlinks
    for agent, agent_dir in AGENT_DIRS.items():
        if not agent_dir.exists():
            continue
        for entry in sorted(agent_dir.iterdir()):
            if entry.is_symlink() and not entry.exists():
                issues.append(f"broken symlink: {entry} -> {entry.resolve()}")

    # Check for skills not in unified storage (un-converged)
    for skill_name, agents in all_skills.items():
        local_agents = [a for a, info in agents.items() if info["type"] == "local"]
        if len(local_agents) > 1:
            issues.append(
                f"un-converged '{skill_name}': found in {', '.join(local_agents)}"
            )

    # Summary
    total = len(set(list(registry.keys()) + list(all_skills.keys())))
    print(f"Unified skills dir: {AGENT_SKILLS_DIR}")
    print(f"  Skills in registry: {len(registry)}")
    print(f"  Skills on disk:     {total}")
    print()

    if issues:
        print(f"[issues] {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("[ok] No issues found.")


def cmd_update(args):
    """Update skills from their git repositories."""
    ensure_metadata()
    registry = load_registry()

    target = args.skill if args.skill else "all"

    updated = []
    errors = []

    for skill_name in registry:
        if target != "all" and skill_name != target:
            continue

        skill_dir = AGENT_SKILLS_DIR / skill_name
        if not (skill_dir / ".git").exists():
            if target == skill_name:
                print(f"[skip] '{skill_name}' is not a git repository.")
            continue

        print(f"[updating] {skill_name}...")
        result = subprocess.run(
            ["git", "-C", str(skill_dir), "pull", "--ff-only"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            updated.append(skill_name)
        else:
            errors.append((skill_name, result.stderr.strip()))

    if updated:
        print(f"\n[updated] {len(updated)} skill(s): {', '.join(updated)}")
    if errors:
        print(f"\n[errors] {len(errors)} update(s) failed:")
        for name, err in errors:
            print(f"  {name}: {err}")
    if not updated and not errors and target == "all":
        print("[ok] No git-based skills to update.")


def cmd_migrate(args):
    """Full migration: sync all existing skills to unified architecture."""
    print("=" * 60)
    print("agentskills: Migrating to unified skill storage")
    print("=" * 60)

    # Step 1: init
    print("\n[1/3] Initializing...")
    cmd_init(None)

    # Step 2: sync
    print("\n[2/3] Syncing skills...")
    cmd_sync(None)

    # Step 3: status
    print("\n[3/3] Final status:")
    cmd_status(None)

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)


# === CLI Entry ===


def main():
    parser = argparse.ArgumentParser(
        prog="agentskills",
        description="Cross-agent skill synchronization tool",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    p_init = subparsers.add_parser("init", help="Initialize unified skills directory")
    p_init.set_defaults(func=cmd_init)

    # sync
    p_sync = subparsers.add_parser("sync", help="Sync skills from all agents")
    p_sync.set_defaults(func=cmd_sync)

    # list
    p_list = subparsers.add_parser("list", help="List all skills and status")
    p_list.set_defaults(func=cmd_list)

    # install
    p_install = subparsers.add_parser("install", help="Install a skill from URL or path")
    p_install.add_argument("source", help="Git URL or local directory path")
    p_install.add_argument("--name", required=True, help="Skill name (directory name)")
    p_install.set_defaults(func=cmd_install)

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a skill from all agents")
    p_remove.add_argument("skill", help="Skill name to remove")
    p_remove.set_defaults(func=cmd_remove)

    # status
    p_status = subparsers.add_parser("status", help="Check skill status and issues")
    p_status.set_defaults(func=cmd_status)

    # update
    p_update = subparsers.add_parser("update", help="Update skills from git")
    p_update.add_argument("skill", nargs="?", default="all", help="Skill name or 'all'")
    p_update.set_defaults(func=cmd_update)

    # migrate
    p_migrate = subparsers.add_parser("migrate", help="Full migration wizard")
    p_migrate.set_defaults(func=cmd_migrate)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
