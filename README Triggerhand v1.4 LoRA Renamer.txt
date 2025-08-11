     _______                 _   _  
    |__   __|               | | | |
       | |                  | |_| |
       | |                  | |_| |
       | |                  | | | |
       |_|(:)(:)(:)(:)(:)(:)|_| |_|(:)(:)(:)
                                    
============================================================
    TriggerHand — LoRA Keyword Finder & Renamer
============================================================

    ------------------------------------------
    Scavenger utility for pulling trigger tags
    and base model info from LoRA metadata.
    Forged for the post-collapse archives.
    ------------------------------------------
    Created by: NeonWildWarrior
    GitHub: https://github.com/neonwildwarrior
    YouTube: https://youtube.com/@neonwildwarrior

------------------------------------------------------------
TriggerHand is A tiny (~16 KB) Python utility that scans your LoRA 
`.safetensors` files, extracts trigger words and base model 
info from the metadata, and renames them with that info 
in the filename.

------------------------------------------------------------
FEATURES
------------------------------------------------------------
- Reads LoRA metadata for trigger words, base model, and 
  common model families (Pony, Illustrious, Flux, ReV 
  Animated, DreamShaper, Hunyuan, etc.)
- Dry-run preview by default — see changes before renaming
- CSV report of all changes for reference
- Works with subfolders
- Drag-and-drop ready `.bat` for zero-terminal setup

------------------------------------------------------------
REQUIREMENTS
------------------------------------------------------------
- Python 3.8+ installed and added to PATH
- `safetensors` module (install with: pip install safetensors)
- LoRAs saved as `.safetensors`

------------------------------------------------------------
HOW TO USE
------------------------------------------------------------

OPTION 1: DRAG & DROP (Windows)
1. Put the `.bat` file and 
   `Lora_Keyword_finder_renamer.py` in the same folder.
2. Drag a folder of `.safetensors` files onto the `.bat` file.
3. Type `Y` to apply changes, or `N` for preview only.

OPTION 2: COMMAND LINE
    python Lora_Keyword_finder_renamer.py "path\to\LoRA\folder"

Dry run by default.  
Apply changes:
    python Lora_Keyword_finder_renamer.py "path\to\LoRA\folder" --apply

Options
    --top N → max number of trigger keywords to include (default 5).
    --preview N → show up to N planned renames before running (default 20).

Example:
python Lora_Keyword_finder_renamer.py "D:\LoRAs\MyFolder" --top 7 --preview 30

------------------------------------------------------------
OUTPUT
------------------------------------------------------------
- Updated filenames with trigger words + base model info
- CSV log saved in the scanned folder

Example:
Before-
redDress_v2.safetensors
animePonyX.safetensors

After-
redDress_v2 [trigger=red_dress+fantasy_art] [model=SD15].safetensors
animePonyX [model=Pony].safetensors

============================================================
Notes:
    Works best with LoRAs from platforms like CivitAI that include proper metadata.
    If a LoRA has no metadata, it will be skipped. 
    Not all creators put their trigger keywords or model in their metadata so results will vary. 
    It's been useful for me to find out info on my forgotten about LoRA's.

CSV Report
 Every run generates a CSV in the target folder:
    old_path, new_path, triggers, kw_count, model
    hit_type (both / triggers / model)
You can use this file to undo changes manually if needed.

------------------------------------------------------------
LORA ORGANIZATION TIPS
------------------------------------------------------------
- Manually choose the correct folder location every time you download a lora
- Separate LoRAs by base model first (1.5, XL, Flux, etc.)
- Add your own tags to filenames for quick searchability when you download so you don't rely on this tool
- Back up before bulk renaming

Here's a sample Lora Organization Tree
📂 LoRAs
│
├── 📂 SD1.5
│   ├── 📂 Styles
│   │   ├── Pony
│   │   ├── Illustrious
│   │   ├── DreamShaper
│   │   └── Realistic Vision
│   ├── 📂 Characters
│   │   ├── Anime Characters
│   │   ├── Realistic
│   │   └── OCs / Custom
│   ├── 📂 Clothing & Fashion
│   │   ├── Armor
│   │   ├── Casual
│   │   └── Fantasy Outfits
│   └── 📂 ControlNet & Utility
│       ├── Pose
│       ├── Depth
│       └── Edge / Line Art
│
├── 📂 SDXL
│   ├── 📂 Styles
│   │   ├── Illustrious XL
│   │   ├── DreamShaper XL
│   │   └── Realistic Vision XL
│   ├── 📂 Characters
│   │   ├── Anime Characters
│   │   ├── Realistic
│   │   └── OCs / Custom
│   ├── 📂 Clothing & Fashion
│   │   ├── Armor
│   │   ├── Casual
│   │   └── Fantasy Outfits
│   └── 📂 ControlNet & Utility
│       ├── Pose XL
│       ├── Depth XL
│       └── Edge / Line Art XL
│
├── 📂 Flux
│   ├── 📂 Styles
│   │   ├── Flux Illustration
│   │   └── Flux Realism
│   ├── 📂 Characters
│   │   ├── Anime Characters
│   │   ├── Realistic
│   │   └── OCs / Custom
│   └── 📂 Clothing & Fashion
│       ├── Armor
│       ├── Casual
│       └── Fantasy Outfits
│
└── 📂 WAN2.1
    ├── 📂 Styles
    │   ├── WAN Illustration
    │   └── WAN Realism
    ├── 📂 Characters
    │   ├── Anime Characters
    │   ├── Realistic
    │   └── OCs / Custom
    └── 📂 Clothing & Fashion
        ├── Armor
        ├── Casual
        └── Fantasy Outfits


-NeonWildWarrior




