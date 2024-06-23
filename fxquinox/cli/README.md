## `fxquinox.cli`

Thid module contains the CLI counterparts of different modules. To call then in a terminal, simply type `python -m fxquinox.cli.<module name>`.

For example `python -m fxquinox.cli.fxcore`:

```shell
usage: fxcore.py [-h]
                 {create_asset,create_assets,create_project,create_sequence,create_sequences,create_shot,create_shots,get_project,run_launcher,set_project}
                 ...

The fxcore module provides a set of tools for managing and automating the creation of VFX entities.

options:
  -h, --help            Show this help message and exit with the information on how to use this program.

commands:
  {create_asset,create_assets,create_project,create_sequence,create_sequences,create_shot,create_shots,get_project,run_launcher,set_project}
    create_asset        Creates a new asset directory structure within a project.
    create_assets       Creates new asset directory structures within a project.
    create_project      Creates a new project directory structure.
    create_sequence     Creates a new sequence directory structure within a project.
    create_sequences    Creates new sequence directory structures within a project.
    create_shot         Creates a new shot directory structure within a sequence.
    create_shots        Creates new shot directory structures within a sequence.
    get_project         Gets the project path and name from the environment file.
    run_launcher        Runs the FX Launcher UI.
    set_project         Sets the project path in the project browser.
```

