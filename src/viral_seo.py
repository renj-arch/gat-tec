import random

CHANNEL_NAME = "RawTechReview"
CHANNEL_HANDLE = "@rawtechreview"

TITLE_TEMPLATES = {
    "comparisons": [
        "{product_a} vs {product_b} — Honest Review Compared",
        "{product_a} vs {product_b}: Which One Should You Buy?",
        "Don't Buy {product_a} or {product_b} Until You See This Review",
        "{product_a} vs {product_b} — Real Pros and Cons",
        "Which Is Better For You? {product_a} vs {product_b}",
        "{product_a} vs {product_b} — 5 Category Breakdown",
        "The Real Difference Between {product_a} and {product_b}",
        "Honest Review: {product_a} vs {product_b}",
        "Stop Wondering \u2014 {product_a} vs {product_b} Full Review",
    ],
}

DESCRIPTION_TEMPLATES = {
    "comparisons": [
        "Here is an honest breakdown of {product_a} vs {product_b} across 5 categories \u2014 no bias, just real pros and cons.\n\n"
        "Which one fits your needs? Let me know in the comments! \U0001f447",
        "Looking to buy {product_a} or {product_b}? Here is everything you need to know before spending your money.\n\n"
        "Full review with real pros and cons. Comment your pick below! \U0001f4ac",
    ],
}

ENGAGEMENT_TEMPLATES = [
    "Which one fits your needs better? Comment below! 👇",
    "Which are you going with? Drop your choice! ⬇️",
    "I read every comment — tell me your pick! 💬",
    "Share this with someone who's deciding between these two 🔄",
    "Save this for your next purchase decision 📌",
    "Follow for more honest tech reviews! 🔔",
]


def generate_viral_title(mode: str, data: dict) -> str:
    templates = TITLE_TEMPLATES.get(mode, ["{product_a} vs {product_b} #shorts"])
    template = random.choice(templates)
    template = template.replace("{product_a}", data.get("product_a", "Product A"))
    template = template.replace("{product_b}", data.get("product_b", "Product B"))
    template = template.replace("{hook}", data.get("hook", ""))

    if len(template) > 90:
        template = template[:87] + "..."

    return template


def generate_viral_description(mode: str, data: dict, script: str = "") -> str:
    desc_templates = DESCRIPTION_TEMPLATES.get(mode, [
        "{product_a} vs {product_b} — honest review.\n\n"
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
        "Drop a 🔥 if you found this review helpful!",
        "Save this for later and share with a friend! 📌",
        "Follow for daily honest tech reviews! 🚀",
        "Comment your choice below! 👇",
    ])
    template += f"\n\n{engagement_prompt}"

    return template


def generate_viral_tags(mode: str, data: dict) -> list[str]:
    tags = ["shorts", "techreview", "review", "techtips",
            data.get("product_a", "").lower().replace(" ", ""),
            data.get("product_b", "").lower().replace(" ", "")]
    tags.extend([
        "versus", "vs", "productcomparison",
        "techshorts", "comparison", "buyingguide",
        "tech", "gadgets", "honestreview",
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
    selected = ["#shorts", "#techreview", "#honestreview", "#comparison", "#techtips", "#gadgets"]
    random.shuffle(selected)
    return " ".join(selected[:count])
