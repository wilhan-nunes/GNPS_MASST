# -*- coding: utf-8 -*-
"""Runs `masst_client.py` or `masst_batch_client.py` from the microbe_masst
submodule after pointing PLANT_MASST at a chosen tree/table version.

This does NOT modify anything inside the microbe_masst submodule - it only
reassigns attributes on the shared `masst_utils.PLANT_MASST` config object at
runtime, then executes the requested submodule script exactly as if it had
been called directly.

Usage:
    python run_plant_masst.py <masst_client|masst_batch_client> [--plant_table_version ID] [...other args passed through...]
"""
import os
import runpy
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_THIS_DIR)
_SUBMODULE_CODE_DIR = os.path.join(_REPO_ROOT, "microbe_masst", "code")

sys.path.insert(0, _THIS_DIR)
sys.path.insert(0, _SUBMODULE_CODE_DIR)

from registry import DEFAULT_VERSION, VERSIONS


def _pop_flag(argv, flag):
    if flag in argv:
        i = argv.index(flag)
        value = argv[i + 1]
        del argv[i:i + 2]
        return value
    return None


def main():
    argv = sys.argv[1:]
    if not argv:
        raise SystemExit("usage: run_plant_masst.py <masst_client|masst_batch_client> [args...]")

    target = argv[0]
    remaining_args = argv[1:]

    version = _pop_flag(remaining_args, "--plant_table_version") or DEFAULT_VERSION
    version_cfg = VERSIONS.get(version, VERSIONS[DEFAULT_VERSION])

    import masst_utils
    masst_utils.PLANT_MASST.tree_file = version_cfg["tree_file"]
    masst_utils.PLANT_MASST.metadata_file = version_cfg["metadata_file"]

    target_script = os.path.join(_SUBMODULE_CODE_DIR, "{}.py".format(target))
    sys.argv = [target_script] + remaining_args
    runpy.run_path(target_script, run_name="__main__")


if __name__ == "__main__":
    main()
