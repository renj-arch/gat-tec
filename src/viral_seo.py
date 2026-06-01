import random

CHANNEL_NAME = "TechnReview"
CHANNEL_HANDLE = "@technreview"

TITLE_TEMPLATES = {
    "comparisons": [
        "{product_a} vs {product_b} — Which One Wins? ⚡",
        "{product_a} vs {product_b}: The Ultimate Comparison",
        "Don't Buy {product_a} or {product_b} Until You Watch This",
        "This {product_a} vs {product_b} Comparison Changes Everything",
        "{product_a} vs {product_b} — The Winner Will Surprise You",
        "I Compared {product_a} and {product_b} So You Don't Have To",
        "Stop Wondering: {product_a} vs {product_b} — Full Breakdown",
        "The Real Difference Between {product_a} and {product_b}",
        "Which Is Better? {product_a} vs {product_b} 🔥",
        "{product_a} vs {product_b} — 5 Tests, 1 Winner",
    ],
}

DESCRIPTION_TEMPLATES = {
    "comparisons": [
        "{product_a} vs {product_b} — which one should you buy?\n\n"
        "We compared 5 key categories to find the real winner.\n\n"
        "Which one would YOU pick? Let me know in the comments! 👇",
        "Looking to buy {product_a} or {product_b}? Here's everything you need to know before pulling the trigger.\n\n"
        "Comment your choice below! 💬",
    ],
}

ENGAGEMENT_TEMPLATES = [
    "Which one would you pick? Comment below! 👇",
    "Are you Team A or Team B? Drop your answer! ⬇️",
    "I read every comment — tell me your pick! 💬",
    "Share this with someone who's deciding between these two 🔄",
    "Save this for your next purchase decision 📌",
    "Follow for more honest tech comparisons! 🔔",
]


def generate_viral_title(mode: str, data: dict) -> str:
    templates = TITLE_TEMPLATES.get(mode, ["{product_a} vs {product_b} #shorts"])
    template = random.choice(templates)
    template = template.replace("{product_a}", data.get("product_a", "Product A"))
    template = template.replace("{product_b}", data.get("product_b", "Product B"))
    template = template.replace("{hook}", data.get("hook", ""))
    template = template.replace("{reason}", data.get("verdict_reason", ""))
    template = template.replace("{winner}", data.get("verdict", ""))

    if len(template) > 90:
        template = template[:87] + "..."

    return template


def generate_viral_description(mode: str, data: dict, script: str = "") -> str:
    desc_templates = DESCRIPTION_TEMPLATES.get(mode, [
        "{product_a} vs {product_b} — watch till the end for the winner!\n\n"
        "Comment what you think! 👇\n\n{hashtags}"
    ])
    template = random.choice(desc_templates)
    template = template.replace("{product_a}", data.get("product_a", "Product A"))
    template = template.replace("{product_b}", data.get("product_b", "Product B"))
    template = template.replace("{hook}", data.get("hook", ""))

    if script:
        preview = script[:150].strip()
        if len(preview) >= 150:
            preview += "..."
        template += f"\n\n{preview}"

    template += f"\n\n{random.choice(ENGAGEMENT_TEMPLATES)}"
    template += f"\n\n🔗 {CHANNEL_HANDLE}"

    engagement_prompt = random.choice([
        "Which one wins in your opinion? I read every comment! 💬",
        "Drop a 🔥 if you agree with the winner!",
        "Save this for later and share with a friend! 📌",
        "Follow for daily tech comparisons! 🚀",
        "Comment your choice below! 👇",
    ])
    template += f"\n\n{engagement_prompt}"

    return template


def generate_viral_tags(mode: str, data: dict) -> list[str]:
    tags = ["shorts", "techreview", "comparison", "techtips", product_tag := data.get("product_a", "").lower().replace(" ", ""), data.get("product_b", "").lower().replace(" ", "")]
    tags.extend([
        "versus", "vs", "productcomparison",
        "techshorts", "whichisbetter", "buyingguide",
        "tech", "gadgets", "review",
    ])
    if "smartphone" in data.get("product_a", "").lower() or "phone" in data.get("product_a", "").lower():
        tags.extend(["smartphone", "phonereview", "phonecomparison"])
    if "laptop" in data.get("product_a", "").lower():
        tags.extend(["laptop", "laptopcomparison", "laptopreview"])
    if "earbud" in data.get("product_a", "").lower() or "headphone" in data.get("product_a", "").lower():
        tags.extend(["earbuds", "headphones", "audio"])
    if "watch" in data.get("product_a", "").lower():
        tags.extend(["smartwatch", "wearable"])
    if "tablet" in data.get("product_a", "").lower() or "ipad" in data.get("product_a", "").lower():
        tags.extend(["tablet", "ipad"])

    seen = set()
    unique_tags = []
    for tag in tags:
        t = tag.lower().strip()
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)
    return unique_tags[:30]


def generate_viral_hashtags(mode: str, count: int = 6) -> str:
    selected = ["#shorts", "#techreview", "#comparison", "#versus", "#techtips", "#gadgets"]
    random.shuffle(selected)
    return " ".join(selected[:count])
