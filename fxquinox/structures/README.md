# Project Structure

``` text
.
└── 📁 $PROJECT/
    ├── 📁 .pipeline/
    │   ├── 📁 custom_modules/
    │   │   └── 📄 README.md
    │   └── 📁 worfile_presets/
    │       └── 📄 README.md
    ├── 📁 production/
    │   ├── 📁 assets/
    │   │   └── 📁 $ASSET/
    │   │       ├── 📁 exports
    │   │       ├── 📁 playblasts
    │   │       ├── 📁 renders/
    │   │       │   ├── 📁 2d_renders
    │   │       │   └── 📁 3d_renders
    │   │       ├── 📁 workfiles/
    │   │       │   └── 📁 $STEP/
    │   │       │       └── 📁 $TASK/
    │   │       │           └── 📄 $WORKFILE.hip
    │   │       └── 📄 .$ASSET_info.json
    │   └── 📁 shots/
    │       └── 📁 $SEQUENCE/
    │           └── 📁 $SHOT/
    │               ├── 📁 exports
    │               ├── 📁 playblasts
    │               ├── 📁 renders/
    │               │   ├── 📁 2d_renders
    │               │   └── 📁 3d_renders
    │               ├── 📁 workfiles/
    │               │   └── 📁 $STEP/
    │               │       └── 📁 $TASK/
    │               │           └── $WORKFILE.hip
    │               └── 📄 .$SHOT_info.json
    └── 📄 .$PROJECT_info.json
```