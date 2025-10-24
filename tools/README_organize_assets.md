Organize Assets helper

This small utility helps you reorganize the `Assets` directory in the GFEditor workspace.

Usage (dry-run):

PowerShell
```powershell
& .venv\Scripts\python.exe tools\organize_assets.py --assets .\Assets
```

To actually move files, add `--apply` and confirm when prompted:

```powershell
& .venv\Scripts\python.exe tools\organize_assets.py --assets .\Assets --apply
```

Notes and behavior
- Default rules are conservative and aim to:
  - Move image files (.png/.jpg/.dds) into `Assets/itemicon` (if file name suggests an item icon) or `Assets/images` otherwise.
  - Move audio files (.wav, .ogg, .mp3) into `Assets/Sounds`.
  - Move model files (.kfm, .obj, .fbx) into `Assets/Models`.
  - Move top-level loose files into `Assets/Other`.
- The script performs a dry-run by default and prints planned moves. Use `--apply` to perform the moves; it will ask for confirmation.
- The script does not overwrite existing files: if a destination exists it will append `_1`, `_2`, ... to avoid data loss.

Customize rules
- Edit `tools/organize_assets.py` to adjust `IMAGE_EXTS`, `AUDIO_EXTS`, `MODEL_EXTS` or add filename-based rules for more precise placement.

Be careful
- Always run the dry-run first to review planned moves.
- Consider committing or backing up the `Assets` folder before major reorganizations.
