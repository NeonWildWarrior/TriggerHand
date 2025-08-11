def show_banner():
    banner = r"""
     _______                 _   _  
    |__   __|               | | | |
       | |                  | |_| |
       | |                  | |_| |
       | |                  | | | |
       |_|(:)(:)(:)(:)(:)(:)|_| |_|(:)(:)(:)
                                    
    ========== [ TriggerHand v1.4 ] ==========

    LoRA Keyword Finder + Renamer
    ------------------------------------------
    Scavenger utility for pulling trigger tags
    and base model info from LoRA metadata.
    Forged for the post-collapse archives.
    ------------------------------------------
    Created by: NeonWildWarrior
    GitHub: https://github.com/neonwildwarrior
    YouTube: https://youtube.com/@neonwildwarrior
    """
    print(banner)

# Call at start of main():
show_banner()

#!/usr/bin/env python3
import argparse, csv, datetime as dt, json, re, sys
from pathlib import Path
from typing import List, Dict, Tuple
from safetensors import safe_open

DRY_RUN_DEFAULT = True
SUPPORTED_EXTS = {".safetensors"}

CANDIDATE_FIELDS = [
    "ss_tag_frequency", "ss_tags", "ss_prompt", "ss_captions",
    "ss_training_comment", "ss_caption", "training_comment",
    "tags", "prompt"
]

MODEL_FIELDS = [
    "ss_base_model", "base_model", "sd_version", "ss_sd_model_name",
    "model", "ss_session_model_name", "ss_network_model", "ss_new_sd_model_hash"
]

# For cleaning the original stem (keep spaces/dots there, we trim later)
SAFE_CHARS = re.compile(r"[^-\w\[\]\(\)\s\.\+&]")
# For sanitizing tags/model tokens inserted into filenames (Windows-safe)
WINDOWS_SAFE_CHARS = re.compile(r"[^A-Za-z0-9_\-\+\(\)\[\]]+")

def read_metadata(path: Path) -> Dict[str, str]:
    try:
        with safe_open(str(path), framework="np") as f:
            return f.metadata() or {}
    except Exception:
        return {}
        

def extract_triggers(meta: Dict[str, str], top_n: int = 5) -> List[str]:
    tags: List[str] = []

    # 1) frequency dict
    freq_raw = meta.get("ss_tag_frequency")
    if freq_raw:
        try:
            freq = json.loads(freq_raw)
            items = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
            tags.extend([k.strip() for k, _ in items if k and k.strip()])
        except Exception:
            pass

    # 2) other candidate fields
    for key in CANDIDATE_FIELDS:
        if key == "ss_tag_frequency":
            continue
        val = meta.get(key)
        if not val or not isinstance(val, str):
            continue
        parts = [p.strip() for p in val.split(",")] if "," in val else re.split(r"[;|\s]+", val.strip())
        for p in parts:
            p = p.strip().strip("#")
            if p and len(p) <= 48:
                tags.append(p)

    # normalize/dedupe
    seen, normed = set(), []
    for t in tags:
        lt = t.lower()
        if lt not in seen:
            seen.add(lt)
            normed.append(lt)

    # filter junk
    junk = {
        "lora","trigger","style","model","keyword","sdxl","sd15","stable","diffusion",
        "none","n/a","na","dataset","img"
    }
    normed = [t for t in normed if t not in junk]

    # prefer shorter tokens first (but keep original freq bias roughly)
    normed = sorted(normed, key=lambda t: (len(t) > 20,))
    return normed[:top_n]

def detect_base_model(meta: Dict[str, str]) -> str:
    """
    Detect common base models from LoRA metadata.
    Returns a compact label (e.g., 'SDXL', 'Pony') or '' if unknown.
    """
    vals = []
    for k in MODEL_FIELDS:
        v = meta.get(k)
        if v and isinstance(v, str):
            vals.append(v.lower())

    blob = " ".join(vals)
    if not blob:
        return ""

    # Named bases first
    if "pony" in blob:
        return "Pony"
    if "illustrious" in blob:
        return "Illustrious"
    if "flux" in blob:
        return "Flux"
    if "rev animated" in blob or "rev_animated" in blob:
        return "ReV-Animated"
    if "dreamshaper" in blob:
        return "DreamShaper"
    if "hunyuan" in blob:
        return "Hunyuan"

    # Families/versions
    if any(s in blob for s in ["sdxl","stable-diffusion-xl","xl-base","xl-refiner","1.0-xl","sd_xl"]):
        return "SDXL"
    if any(s in blob for s in ["sd15","1.5","v1-5","sd v1.5","stable-diffusion-v1-5","sd_1.5"]):
        return "SD15"
    if any(s in blob for s in ["1.4","sd14","v1-4"]):
        return "SD14"
    if "sd3" in blob or "stable-diffusion-3" in blob:
        return "SD3"

    return ""

def _sanitize_tag(tag: str) -> str:
    tag = tag.strip().replace(" ", "_")
    tag = WINDOWS_SAFE_CHARS.sub("", tag)
    return tag[:40]

def print_preview(plan, limit=20):
    if not plan:
        print("No files eligible for rename to preview.")
        return
    shown = plan[:limit]
    print("\nPreview (old → new):")
    # column formatting
    old_w = max(len(p[0].name) for p in shown)
    old_w = min(old_w, 60)  # cap for tidy output
    for old, new, *_ in shown:
        old_name = old.name
        new_name = new.name
        if len(old_name) > 60:
            old_name = old_name[:57] + "..."
        print(f"  {old_name.ljust(63)}  →  {new_name}")
    if len(plan) > limit:
        print(f"...and {len(plan) - limit} more")

def safe_tag_block(triggers: List[str]) -> str:
    if not triggers:
        return ""
    return "[trigger=" + "+".join(_sanitize_tag(t) for t in triggers) + "]"

def model_block(model_label: str) -> str:
    return f"[model={model_label}]" if model_label else ""

def propose_name(path: Path, tag_block: str, model_tag: str) -> str:
    stem = SAFE_CHARS.sub("", path.stem).strip()
    # strip previous blocks (old colon or new equals)
    stem = re.sub(r"\[trigger[:=][^\]]+\]", "", stem).strip()
    stem = re.sub(r"\[model[:=][^\]]+\]", "", stem).strip()
    blocks = [b for b in [tag_block, model_tag] if b]
    new_stem = (stem + " " + " ".join(blocks)).strip() if blocks else stem
    new_stem = new_stem.rstrip(" .")
    return f"{new_stem}{path.suffix}"

def uniquify(dest: Path) -> Path:
    if not dest.exists():
        return dest
    parent, stem, suffix, n = dest.parent, dest.stem, dest.suffix, 1
    while True:
        candidate = parent / f"{stem} ({n}){suffix}"
        if not candidate.exists():
            return candidate
        n += 1

SUPPORTED_EXTS = {".safetensors"}

def collect_targets(root: Path, recursive: bool = True) -> List[Path]:
    it = (root.rglob("*") if recursive else root.glob("*"))
    return [p for p in it if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]

def build_plan(files: List[Path], top_n: int) -> List[Tuple[Path, Path, List[str], str, str]]:
    """
    Returns (old_path, new_path, triggers, model, hit_type)
    hit_type = 'both' | 'triggers' | 'model' | 'none'
    """
    plan = []
    for f in files:
        meta = read_metadata(f)
        if not meta:
            continue
        triggers = extract_triggers(meta, top_n=top_n)
        model = detect_base_model(meta)
        hit_type = ("both" if (triggers and model)
                    else "triggers" if triggers
                    else "model" if model
                    else "none")
        if hit_type == "none":
            continue
        tag_block = safe_tag_block(triggers)
        model_tag = model_block(model)
        new_name = propose_name(f, tag_block, model_tag)
        new_path = f.with_name(new_name)
        plan.append((f, new_path, triggers, model, hit_type))
    return plan

def write_csv(plan, out_dir: Path) -> Path:
    ts = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_path = out_dir / f"triggersmith_report_{ts}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["old_path", "new_path", "triggers", "kw_count", "model", "hit_type"])
        for old, new, tags, model, hit_type in plan:
            w.writerow([str(old), str(new), ", ".join(tags), len(tags), model or "", hit_type])
    return csv_path

def print_summary(plan):
    total = len(plan)
    both = sum(1 for *_ , h in plan if h == "both")
    trig = sum(1 for *_ , h in plan if h == "triggers")
    model = sum(1 for *_ , h in plan if h == "model")
    print(f"Renamable total: {total}  |  both: {both}  |  triggers: {trig}  |  model: {model}")

def main():
    show_banner()  # optional

    ap = argparse.ArgumentParser(description="T.Hand — LoRA Keyword Finder & Renamer")
    ap.add_argument("folder", help="Folder to scan")
    ap.add_argument("--apply", action="store_true", help="Apply renames (default is dry-run)")
    ap.add_argument("--top", type=int, default=5, help="Max triggers to include (default 5)")
    ap.add_argument("--preview", type=int, default=20, help="Show up to N planned renames in the preview (default 20)")
    ap.add_argument("--no-recursive", action="store_true",
                help="Only scan the top-level folder (default is recursive)")
    args = ap.parse_args()

    root = Path(args.folder).expanduser().resolve()
    if not root.exists():
        print(f"[!] Folder not found: {root}")
        sys.exit(1)

    files = collect_targets(root, recursive=not args.no_recursive)
    print(f"Scanning: {root}")
    print(f"Found {len(files)} .safetensors file(s)")

    plan = build_plan(files, top_n=args.top)
    print_summary(plan)
    print_preview(plan, limit=args.preview)

    # write CSV and announce it (csv_path is in scope here)
    csv_path = write_csv(plan, root)
    print(f"CSV log saved to: {csv_path}")

    if not args.apply:
        print("\nDRY RUN: no files were renamed.")
        print("Use --apply to rename. You’ll be asked to confirm.")
        return

    # applying changes flow
    print_preview(plan, limit=args.preview)
    print("\nType YES to continue and apply these renames:")
    if input().strip() != "YES":
        print("Aborted.")
        return

    renamed = skipped = 0
    for old, new, *_ in plan:
        try:
            final = uniquify(new)
            if final == old:
                skipped += 1
                continue
            old.rename(final)
            renamed += 1
        except Exception as e:
            print(f"[skip] {old.name} -> {new.name} ({e})")
            skipped += 1

    print(f"\nDone. Renamed: {renamed} | Skipped: {skipped}")
    print(f"CSV log saved to: {csv_path}")

if __name__ == "__main__":
    main()