import json, random, re
from pathlib import Path
from src.script_generator import _generate

BANK_DIR = Path(__file__).parent / "bank"

REFILL_PROMPTS = {
    "comparisons": (
        "Write a tech product comparison for a YouTube Shorts video comparing two popular {category}. "
        "The video will have 5 comparison points. "
        "Never repeat products from this avoid list:"
        "\n---\n{avoid}\n---\n"
        "Format exactly:\n"
        "PRODUCT_A: [product name]\n"
        "PRODUCT_B: [product name]\n"
        "POINT_1: [winner name] wins — [one sentence why]\n"
        "POINT_2: [winner name] wins — [one sentence why]\n"
        "POINT_3: [winner name] wins — [one sentence why]\n"
        "POINT_4: [winner name] wins — [one sentence why]\n"
        "POINT_5: [winner name] wins — [one sentence why]\n"
        "VERDICT: The overall winner is [product] because [reason].\n\n"
        "Make each point factual, specific, and no more than 15 words. "
        "Use real products. Category: {category}"
    ),
}

TECH_CATEGORIES = [
    "smartphones", "laptops", "wireless earbuds", "tablets",
    "smartwatches", "gaming consoles", "graphics cards",
    "streaming devices", "budget headphones", "mechanical keyboards",
    "fitness trackers", "bluetooth speakers", "external SSDs",
    "wireless chargers", "budget smartphones", "gaming mice",
    "monitors", "USB-C hubs", "power banks", "action cameras",
    "noise-cancelling headphones", "ultrabooks", "gaming laptops",
    "folding phones", "smart home speakers",
]

HOOKS = [
    "Which one wins?", "Here's the real comparison:",
    "Let's settle this once and for all:",
    "The ultimate showdown:",
    "Which should you buy?",
    "Here's how they stack up:",
]


def _bank_path(mode: str) -> Path:
    return BANK_DIR / f"{mode}.json"


def _read_bank(mode: str) -> dict:
    path = _bank_path(mode)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"entries": [], "used": [], "min_before_refill": 5, "refill_target": 40}


def _write_bank(mode: str, data: dict):
    path = _bank_path(mode)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _mark_used(mode: str, entry: dict):
    data = _read_bank(mode)
    if "used" not in data:
        data["used"] = []
    used = data["used"]
    if mode == "comparisons":
        for p in [entry.get("product_a", ""), entry.get("product_b", "")]:
            n = _normalize(p)
            if n and n not in used:
                used.append(n)
    data["used"] = used
    _write_bank(mode, data)


def _avoid_sample(mode: str, max_items: int = 30) -> str:
    data = _read_bank(mode)
    used = data.get("used", [])
    if not used:
        return "none yet"
    sample = random.sample(used, min(max_items, len(used)))
    return "\n".join(f"- {item}" for item in sample)


def _is_duplicate_products(mode: str, product_a: str, product_b: str, data: dict) -> bool:
    used = set(data.get("used", []))
    return _normalize(product_a) in used or _normalize(product_b) in used


def pick(mode: str) -> dict | None:
    return None


def count(mode: str) -> int:
    return len(_read_bank(mode)["entries"])


def needs_refill(mode: str) -> bool:
    data = _read_bank(mode)
    return len(data["entries"]) <= data["min_before_refill"]


def ensure_refilled(mode: str):
    if mode != "comparisons":
        return
    if needs_refill(mode):
        refill(mode)


def refill(mode: str, force_count: int | None = None):
    try:
        data = _read_bank(mode)
        target = force_count or data["refill_target"]
        existing = len(data["entries"])
        need = target - existing
        if need <= 0:
            return

        print(f"  Bank refill: generating {need} new {mode} entries...")

        if mode == "comparisons":
            new_entries = _refill_comparisons(need)

        data["entries"].extend(new_entries)
        _write_bank(mode, data)
        print(f"  Bank refilled: {len(data['entries'])} {mode} entries total")
    except Exception as e:
        print(f"  Bank refill failed (non-critical): {e}")


def _refill_comparisons(need: int) -> list:
    entries = []
    attempts = 0
    while len(entries) < need and attempts < need * 5:
        category = random.choice(TECH_CATEGORIES)
        avoid = _avoid_sample("comparisons")
        prompt = REFILL_PROMPTS["comparisons"].format(category=category, avoid=avoid)
        try:
            raw = _generate(prompt, temperature=0.8, max_tokens=600,
                            system="You write factual tech comparison scripts for YouTube Shorts. Be specific with specs and features.")
        except Exception as e:
            print(f"  LLM error (comparisons): {e}")
            attempts += 1
            continue
        if not raw:
            attempts += 1
            continue

        lines = raw.strip().split("\n")
        product_a = product_b = ""
        points = []
        verdict = ""
        reason = ""

        for line in lines:
            line = line.strip()
            up = line.upper()
            if up.startswith("PRODUCT_A:"):
                product_a = line.split(":", 1)[-1].strip()
            elif up.startswith("PRODUCT_B:"):
                product_b = line.split(":", 1)[-1].strip()
            elif up.startswith("POINT_") and ":" in line:
                parts = line.split(":", 1)
                text = parts[-1].strip()
                if text:
                    points.append(text)
            elif up.startswith("VERDICT:"):
                text = line.split(":", 1)[-1].strip()
                if "because" in text.lower():
                    verdict = text.split("because")[0].strip().replace("The overall winner is ", "").replace("The winner is ", "")
                    reason = text.split("because")[-1].strip()
                else:
                    verdict = text
                    reason = text

        if product_a and product_b and len(points) >= 4 and verdict:
            if not _is_duplicate_products("comparisons", product_a, product_b, _read_bank("comparisons")):
                hook = random.choice(HOOKS)
                title = f"{product_a} vs {product_b} — {reason[:30]}"
                image_prompts = [
                    f"product comparison, {product_a} vs {product_b} on a clean white background, side by side, 9:16 vertical, studio lighting, sharp focus, product photography"
                ]
                for p in points:
                    image_prompts.append(
                        f"cinematic close-up shot, {product_a} and {product_b} comparison, {p[:60]}, "
                        f"9:16 vertical, dramatic lighting, tech review style, detailed macro shot"
                    )

                tts_lines = [f"{hook} {product_a} vs {product_b}. Here are 5 reasons why."]
                for i, p in enumerate(points, 1):
                    tts_lines.append(f"Number {i}: {p}")
                tts_lines.append(f"The winner is the {verdict}, because {reason}.")
                tts_lines.append("Which one would you pick? Comment below and subscribe for more tech comparisons!")

                entry = {
                    "title": title[:70],
                    "hook": hook,
                    "product_a": product_a,
                    "product_b": product_b,
                    "points": points,
                    "verdict": verdict,
                    "verdict_reason": reason,
                    "image_prompts": image_prompts,
                    "script": " ".join(tts_lines),
                    "tts_script": " ".join(tts_lines),
                }
                entries.append(entry)
        attempts += 1

    return entries
