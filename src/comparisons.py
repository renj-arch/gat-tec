import random
import bank_manager

HOOKS = [
    "Which one wins?", "Here's the real comparison:",
    "Let's settle this once and for all:",
    "The ultimate showdown:",
    "Which should you buy?",
    "Here's how they stack up:",
]

CATEGORIES = [
    "smartphones", "laptops", "wireless earbuds", "tablets",
    "smartwatches", "gaming consoles", "graphics cards",
    "streaming devices", "budget headphones", "mechanical keyboards",
    "fitness trackers", "bluetooth speakers", "external SSDs",
    "wireless chargers", "budget smartphones", "gaming mice",
    "monitors", "USB-C hubs", "power banks", "action cameras",
]

FALLBACKS = [
    ("iPhone 16 Pro", "Samsung Galaxy S25 Ultra",
     ["Display quality — Samsung wins with its brighter, more vibrant screen.",
      "Battery life — iPhone 16 Pro lasts about 2 hours longer on a single charge.",
      "Camera zoom — Samsung's 100x space zoom blows the iPhone out of the water.",
      "Performance — both are lightning fast, but the A18 chip edges ahead in gaming.",
      "Software updates — Apple promises 7 years, Samsung promises 7 years too."],
     "Samsung Galaxy S25 Ultra", "Display and camera zoom"),
    ("MacBook Air M4", "Dell XPS 16",
     ["Battery life — MacBook Air lasts 18 hours, the Dell barely hits 10.",
      "Performance — both handle daily tasks, but the M4 crushes video editing.",
      "Portability — MacBook is lighter by half a pound and thinner.",
      "Ports — Dell has USB-A, HDMI, and a headphone jack. MacBook needs dongles.",
      "Price — MacBook starts at $1099, Dell at $1499 for similar specs."],
     "MacBook Air M4", "Battery life and performance"),
    ("AirPods Pro 2", "Samsung Galaxy Buds 3 Pro",
     ["Noise cancellation — AirPods Pro 2 block out slightly more ambient noise.",
      "Sound quality — Galaxy Buds 3 Pro have punchier bass and richer mids.",
      "Battery life — Galaxy Buds last 6 hours vs AirPods' 5.5 hours with ANC on.",
      "Comfort — AirPods are lighter and fit more ear shapes comfortably.",
      "Ecosystem — AirPods are seamless with iPhone, Buds are better with Samsung."],
     "AirPods Pro 2", "Ecosystem integration"),
    ("PlayStation 5", "Xbox Series X",
     ["Exclusive games — PS5 has Spider-Man, God of War, and The Last of Us.",
      "Performance — Xbox Series X has slightly better raw graphics power.",
      "Game Pass — Xbox Game Pass gives you hundreds of games for $15 a month.",
      "Controller — PS5's haptic feedback and adaptive triggers are game-changing.",
      "Price — both cost $499, but Xbox often goes on sale."],
     "PlayStation 5", "Exclusive games and controller innovation"),
    ("iPad Pro M4", "Samsung Galaxy Tab S10 Ultra",
     ["Display — iPad Pro's OLED is superior with perfect blacks and HDR.",
      "Stylus — Apple Pencil Pro has better latency and tilt sensitivity.",
      "Multitasking — Samsung DeX gives you a true desktop-like experience.",
      "Performance — M4 chip outperforms the Snapdragon in every benchmark.",
      "Software — iPadOS has better creative apps, Android offers more customization."],
     "iPad Pro M4", "Display and creative software support"),
]


def generate_comparison_script() -> dict:
    entry = bank_manager.pick("comparisons")
    if entry:
        print(f"  Using banked comparison ({bank_manager.count('comparisons')} left)")
        return entry

    print("  Bank empty, generating fresh comparison...")
    result = _try_llm()
    if not result:
        print("  LLM unavailable, using fallback")
        result = random.choice(FALLBACKS)

    product_a, product_b, points, verdict, reason = result

    hook = random.choice(HOOKS)
    title = f"{product_a} vs {product_b} — {reason[:30]}"
    image_prompts = [
        f"product comparison, {product_a} vs {product_b} on a clean white background, side by side, 9:16 vertical, studio lighting, sharp focus, product photography"
    ]
    for p in points:
        product = product_a if product_a in p else product_b
        image_prompts.append(
            f"cinematic close-up shot, {product_a} and {product_b} comparison, {p[:60]}, "
            f"9:16 vertical, dramatic lighting, tech review style, detailed macro shot"
        )

    tts_lines = [f"{hook} {product_a} vs {product_b}. Here are 5 reasons why."]
    for i, p in enumerate(points, 1):
        tts_lines.append(f"Number {i}: {p}")
    tts_lines.append(f"The winner is the {verdict}, because {reason}.")
    tts_lines.append("Which one would you pick? Comment below and subscribe for more tech comparisons!")

    return {
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


def _try_llm() -> tuple | None:
    try:
        from src.script_generator import _generate
        category = random.choice(CATEGORIES)
        prompt = (
            f"Write a tech product comparison for a YouTube Shorts video comparing two popular {category}. "
            f"The video will have 5 comparison points. "
            f"Format exactly:\n"
            f"PRODUCT_A: [product name]\n"
            f"PRODUCT_B: [product name]\n"
            f"POINT_1: [winner name] wins — [one sentence why]\n"
            f"POINT_2: [winner name] wins — [one sentence why]\n"
            f"POINT_3: [winner name] wins — [one sentence why]\n"
            f"POINT_4: [winner name] wins — [one sentence why]\n"
            f"POINT_5: [winner name] wins — [one sentence why]\n"
            f"VERDICT: [The overall winner is... because of...]\n\n"
            f"Make each point factual, specific, and no more than 15 words. "
            f"Category: {category}. Use real products."
        )
        system = "You write fast-paced, factual tech comparison scripts for YouTube Shorts. Be specific with specs and features."
        raw = _generate(prompt, temperature=0.8, max_tokens=600, system=system)
        if not raw:
            return None

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
            return (product_a, product_b, points[:5], verdict, reason)
        return None
    except Exception as e:
        print(f"  LLM error: {e}")
        return None
