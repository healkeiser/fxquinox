"""The fxcore module provides a set of tools for managing and automating the creation of VFX entities."""

# Built-in
import sys

# Internal
from fxquinox.fxcore import (
    create_project,
    create_sequence,
    create_sequences,
    create_shot,
    create_shots,
    create_asset,
    create_assets,
    run_launcher,
)


if __name__ == "__main__":
    from fxquinox.cli import _fxcli

    _fxcli.main(target_module=sys.modules[__name__], description=__doc__ if __doc__ else __name__)
