#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
from pathlib import Path
import textwrap
import re

# shipped with conan
import yaml
import colorama
from colorama import Fore

colorama.init()

RECIPES = Path(__file__).resolve().parent / "recipes"
EXPORTED_RE = re.compile(r"Exported: (\S+)")

def conan_run(op, args, verbose=False):
    cmd = ["conan", op] + args
    cmd_str = " ".join(cmd)
    if verbose:
        print("  +", cmd_str, flush=True)
    else:
        print(Fore.CYAN + f"  ~ conan {op}" + Fore.RESET, flush=True)

    env = os.environ.copy()
    env["CLICOLOR_FORCE"] = "1"
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        env=env
    )

    if verbose or res.returncode != 0:
        print(textwrap.indent(res.stdout, "  > "), end="", flush=True)
    else:
        ref = "done"
        if op == "export":
            if found := EXPORTED_RE.search(res.stdout):
                ref = found.group(1)
        print(Fore.GREEN + f"  -> {ref}" + Fore.RESET, flush=True)

    return res.returncode


def recipe_versions(name):
    cfg = yaml.safe_load((RECIPES / name / "config.yml").read_text())
    return [(str(v), d["folder"]) for v, d in cfg["versions"].items()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--upload", metavar="REMOTE", help="upload recipes to REMOTE")
    p.add_argument("--verbose", action="store_true", help="enable verbose output from conan")
    args = p.parse_args()

    recipes = []
    for name in sorted({d.name for d in RECIPES.iterdir() if d.is_dir()}):
        for version, folder in recipe_versions(name):
            recipes.append((name, version, folder))

    for i, (name, version, folder) in enumerate(recipes):
        print(Fore.BLUE + f"[{i+1}/{len(recipes)}] Recipe {name}/{version}" + Fore.RESET)
        if res := conan_run("export", [
            str(RECIPES / name / folder),
            f"--version={version}",
            "--user=amnezia",
        ], args.verbose):
            return res
        if args.upload:
            if res := conan_run("upload", [f"{name}/{version}@amnezia", "-r", args.upload, "--only-recipe", "-c"], args.verbose):
                return res

    return 0


if __name__ == "__main__":
    sys.exit(main())
