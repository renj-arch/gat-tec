import random
import bank_manager

HOOKS = [
    "Here is an honest breakdown of both:",
    "Let me break this down for you:",
    "Thinking of buying one? Here is what you need to know:",
    "Full review of both \u2014 no bias, just facts:",
    "Based on the specs and performance data, here is the breakdown:",
    "Both products compared honestly:",
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
     ["Display — Samsung has a brighter screen. iPhone has more accurate colors for photo editing.",
      "Battery — iPhone lasts about 2 hours longer. Samsung charges faster with its 45W charging.",
      "Camera — Samsung gives you 100x space zoom. iPhone captures more natural skin tones.",
      "Performance — both are blazing fast. iPhone edges ahead in gaming with better sustained performance.",
      "Software — iOS is simpler and cleaner. One UI gives you more customization options."],
     "Buy the iPhone if you want a reliable camera and long battery. Get the Samsung for zoom and display."),
    ("MacBook Air M4", "Dell XPS 16",
     ["Battery — MacBook Air lasts 18 hours. The Dell barely hits 10 on a good day.",
      "Performance — MacBook crushes video editing thanks to the M4 chip. Dell is better for Windows-only software.",
      "Build — both are premium aluminum. MacBook is thinner and lighter by half a pound.",
      "Ports — Dell gives you USB-A, HDMI, and headphone jack. MacBook makes you carry dongles.",
      "Price — MacBook starts at $1099. Dell costs more at $1499 for comparable specs."],
     "MacBook for battery and portability. Dell if you need Windows and ports."),
    ("AirPods Pro 2", "Samsung Galaxy Buds 3 Pro",
     ["Noise cancellation — AirPods block slightly more ambient noise. Galaxy Buds are close behind.",
      "Sound — Galaxy Buds have punchier bass. AirPods have a more balanced, neutral sound signature.",
      "Battery — Galaxy Buds last 6 hours with ANC. AirPods get 5.5 hours. Case adds extra charges for both.",
      "Comfort — AirPods are lighter and fit more ear types. Galaxy Buds stay more secure during workouts.",
      "Ecosystem — AirPods are seamless with iPhone. Galaxy Buds unlock extra features on Samsung phones."],
     "AirPods for iPhone users. Galaxy Buds for Android — especially Samsung owners."),
    ("PlayStation 5", "Xbox Series X",
     ["Exclusive games — PS5 has Spider-Man, God of War, TLOU. Xbox has Halo, Forza, and Starfield.",
      "Performance — Xbox Series X has slightly better raw GPU power. PS5 has faster SSD loading.",
      "Value — Xbox Game Pass gives hundreds of games for $15/month. PS Plus is more expensive for less.",
      "Controller — PS5's haptic feedback and adaptive triggers feel next-gen. Xbox controller is more traditional.",
      "Backwards compatibility — Xbox plays games from four generations. PS5 is limited to PS4 games."],
     "PS5 for exclusives and immersive controller. Xbox for Game Pass and backwards compatibility."),
    ("iPad Pro M4", "Samsung Galaxy Tab S10 Ultra",
     ["Display — iPad Pro OLED has perfect blacks and stunning HDR. Samsung has a bigger 14.6-inch screen.",
      "Stylus — Apple Pencil Pro has better latency. Samsung S Pen comes included in the box — no extra cost.",
      "Multitasking — Samsung DeX gives you a real desktop experience. iPadOS Stage Manager is catching up slowly.",
      "Performance — M4 chip outperforms Snapdragon in every benchmark. But both handle any app smoothly.",
      "Apps — iPad has better creative apps like Procreate and Final Cut. Samsung has better file management and customization."],
     "iPad Pro for creative professionals. Galaxy Tab if you want a laptop replacement with DeX."),
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

    product_a, product_b, points, recommendation = result

    hook = random.choice(HOOKS)
    title = f"{product_a} vs {product_b} — Honest Review"
    image_prompts = [
        f"product comparison, {product_a} vs {product_b} on a clean white background, side by side, 9:16 vertical, studio lighting, sharp focus, product photography"
    ]
    for p in points:
        image_prompts.append(
            f"cinematic close-up shot, {product_a} and {product_b} comparison, {p[:60]}, "
            f"9:16 vertical, dramatic lighting, tech review style, detailed macro shot"
        )

    tts_lines = [f"{hook} Let's compare {product_a} and {product_b} across 5 categories."]
    for i, p in enumerate(points, 1):
        tts_lines.append(f"{i}. {p}")
    tts_lines.append(f"Final take: {recommendation}")
    tts_lines.append("Which one fits your needs better? Let me know in the comments and follow for more honest reviews!")

    return {
        "title": title[:70],
        "hook": hook,
        "product_a": product_a,
        "product_b": product_b,
        "points": points,
        "recommendation": recommendation,
        "image_prompts": image_prompts,
        "script": " ".join(tts_lines),
        "tts_script": " ".join(tts_lines),
    }


def _try_llm() -> tuple | None:
    try:
        from src.script_generator import _generate
        category = random.choice(CATEGORIES)
        prompt = (
            f"Write an honest tech review comparison for a YouTube Shorts comparing two popular {category}. "
            f"Format exactly:\n"
            f"PRODUCT_A: [product name]\n"
            f"PRODUCT_B: [product name]\n"
            f"POINT_1: [aspect] — [what A does well] [what B does well]\n"
            f"POINT_2: [aspect] — [what A does well] [what B does well]\n"
            f"POINT_3: [aspect] — [what A does well] [what B does well]\n"
            f"POINT_4: [aspect] — [what A does well] [what B does well]\n"
            f"POINT_5: [aspect] — [what A does well] [what B does well]\n"
            f"RECOMMENDATION: Buy [product] if you want [reason]. Get [product] if you need [reason].\n\n"
            f"Rules:\n"
            f"- No winners, no losers. Just honest pros and cons for each.\n"
            f"- Each point covers a different aspect (display, battery, camera, performance, price, etc.)\n"
            f"- CRITICAL: Use ONLY facts you are 100% sure are true. Never make up specs, numbers, or features.\n"
            f"- If you don't know the exact spec, describe it generally (e.g. 'fast charging' instead of a fake watt number).\n"
            f"- Use real products with real, widely-known specifications.\n"
            f"Category: {category}"
        )
        system = "You write honest, balanced tech review scripts for YouTube Shorts. CRITICAL: Only use facts you are certain are true. Never fabricate specs, prices, or features. General descriptions are better than made-up numbers."
        raw = _generate(prompt, temperature=0.8, max_tokens=700, system=system)
        if not raw:
            return None

        lines = raw.strip().split("\n")
        product_a = product_b = ""
        points = []
        recommendation = ""

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
            elif up.startswith("RECOMMENDATION:"):
                recommendation = line.split(":", 1)[-1].strip()

        if product_a and product_b and len(points) >= 4 and recommendation:
            return (product_a, product_b, points[:5], recommendation)
        return None
    except Exception as e:
        print(f"  LLM error: {e}")
        return None
