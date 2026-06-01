import re
import random

STOP_WORDS = set("""
a an the is it of in on to for and or but at by with from as was are be
been being have has had do does did will would could should may might shall
can need just very too so up out off over all any each every no not only
own same than that this these those what which who how when where why
about into through during before after above below between under again
further then once here there some such more most other else like get got
make made take took see saw know knew think thought come came give gave
find found tell told become became leave left feel felt put set bring
brought begin began keep kept hold held write wrote stand stood hear heard
let mean meant meet met run ran pay paid sit sat speak spoke lie lay lead
led read grow grew lose lost fall fell send sent build built understand
draw drew break broke spend spent cut rise rose drive drove buy bought wear
wore choose chose seek sought throw threw catch caught reveal shows showed
shown called known following using looking trying giving making taking getting
""".split())

MODE_KEYWORDS = {
    "comparisons": [
        "vs", "versus", "comparison", "tech review", "which is better",
        "product comparison", "buying guide", "tech showdown",
        "best choice", "should you buy", "review",
    ],
}

CATEGORY_MAP = {
    "comparisons": "howto",
}


def extract_keywords(text: str, max_words: int = 20) -> list[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    filtered = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    bigrams = []
    words_list = filtered
    for i in range(len(words_list) - 1):
        bigram = f"{words_list[i]} {words_list[i+1]}"
        if len(bigram) > 5:
            bigrams.append(bigram)
    bigram_freq = {}
    for b in bigrams:
        bigram_freq[b] = bigram_freq.get(b, 0) + 1
    sorted_bigrams = sorted(bigram_freq.items(), key=lambda x: -x[1])
    result = [w for w, _ in sorted_bigrams[:max_words//2]]
    result += [w for w, _ in sorted_words[:max_words//2]]
    seen = set()
    unique = []
    for item in result:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique[:max_words]


def generate_keyword_tags(mode: str, data: dict) -> list[str]:
    tags = []
    mode_base = MODE_KEYWORDS.get(mode, [mode])
    tags.extend(mode_base)
    text_pool = []
    for key in ["script", "tts_script", "title"]:
        val = data.get(key, "")
        if val:
            text_pool.append(val)
    for key in ["points", "product_a", "product_b", "verdict_reason"]:
        items = data.get(key, [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str):
                    text_pool.append(item)
        elif isinstance(items, str):
            text_pool.append(items)
    combined = " ".join(text_pool)
    extracted = extract_keywords(combined, max_words=10)
    tags.extend(extracted)
    seen = set()
    unique = []
    for tag in tags:
        t = tag.lower().strip()
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:30]


def generate_audience_tags(mode: str) -> list[str]:
    audience_map = {
        "comparisons": ["tech enthusiasts", "shoppers", "gadget lovers", "deal hunters", "review watchers"],
    }
    return audience_map.get(mode, ["general audience"])


def get_youtube_category(mode: str) -> str:
    return CATEGORY_MAP.get(mode, "entertainment")
