# -*- coding: utf-8 -*-
"""Registry of selectable plantMASST tree/table versions.

This intentionally lives outside the `microbe_masst` git submodule so that
adding or changing versions never requires touching submodule files. Each
entry just points at a `tree_file` (masst tree json) and `metadata_file`
(sample metadata csv) pair, in the same format the microbe_masst submodule's
`masst_utils.SpecialMasst` dataclass expects.

To add a new version:
  1. Drop its tree_file/metadata_file somewhere under this repo (e.g. in
     `plant_masst_versions/data/<version_id>/`).
  2. Add an entry below pointing at those paths.
"""
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_THIS_DIR)
_SUBMODULE_DATA_DIR = os.path.join(_REPO_ROOT, "microbe_masst", "data")

DEFAULT_VERSION = "default"

VERSIONS = {
    "default": {
        "label": "Latest",
        "tree_file": os.path.join(_SUBMODULE_DATA_DIR, "plant_masst_tree.json"),
        "metadata_file": os.path.join(_SUBMODULE_DATA_DIR, "plant_masst_table.csv"),
    },
    "test": {
        "label": "Test (no Dendrocnide moroides)",
        "tree_file": os.path.join(_THIS_DIR, "plant_masst_tree_test.json"),
        "metadata_file": os.path.join(_THIS_DIR, "plant_masst_table_test.csv"),
    },
    # "2024-06": {
    #     "label": "PlantMASST v2024-06",
    #     "tree_file": os.path.join(_THIS_DIR, "data", "2024-06", "plant_masst_tree.json"),
    #     "metadata_file": os.path.join(_THIS_DIR, "data", "2024-06", "plant_masst_table.csv"),
    # },
}


def version_options():
    """Options list for a dash dropdown/select, e.g. [{"label": ..., "value": ...}, ...]."""
    return [{"label": cfg["label"], "value": vid} for vid, cfg in VERSIONS.items()]
