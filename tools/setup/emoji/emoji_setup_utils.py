# This file contains various helper functions used by `build_emoji` tool.
# See docs/subsystems/emoji.md for details on how this system works.

from collections import defaultdict

from typing import Any, Dict, List

# Emojisets that we currently support.
EMOJISETS = ['apple', 'emojione', 'google', 'twitter']

# Some image files in the old emoji farm had a different name than in the new emoji
# farm. `remapped_emojis` is a map that contains a mapping of their name in the old
# emoji farm to their name in the new emoji farm.
remapped_emojis = {
    "0023": "0023-20e3",    # Hash
    "0030": "0030-20e3",    # Zero
    "0031": "0031-20e3",    # One
    "0032": "0032-20e3",    # Two
    "0033": "0033-20e3",    # Three
    "0034": "0034-20e3",    # Four
    "0035": "0035-20e3",    # Five
    "0036": "0036-20e3",    # Six
    "0037": "0037-20e3",    # Seven
    "0038": "0038-20e3",    # Eight
    "0039": "0039-20e3",    # Nine
    "1f48f": "1f469-200d-2764-200d-1f48b-200d-1f468",    # Couple kiss
    "1f491": "1f469-200d-2764-200d-1f468",  # Couple with heart
}

def emoji_names_for_picker(emoji_name_maps: Dict[str, Dict[str, Any]]) -> List[str]:
    emoji_names = []  # type: List[str]
    for emoji_code, name_info in emoji_name_maps.items():
        emoji_names.append(name_info["canonical_name"])
        emoji_names.extend(name_info["aliases"])

    return sorted(emoji_names)

def get_emoji_code(emoji_dict: Dict[str, Any]) -> str:
    emoji_code = emoji_dict["unified"]
    return emoji_code.lower()

# Returns a dict from categories to list of codepoints. The list of
# codepoints are sorted according to the `sort_order` as defined in
# `emoji_data`.
def generate_emoji_catalog(emoji_data: List[Dict[str, Any]],
                           emoji_name_maps: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    sort_order = {}  # type: Dict[str, int]
    emoji_catalog = defaultdict(list)  # type: Dict[str, List[str]]

    for emoji_dict in emoji_data:
        emoji_code = get_emoji_code(emoji_dict)
        if not emoji_is_universal(emoji_dict) or emoji_code not in emoji_name_maps:
            continue
        category = emoji_dict["category"]
        sort_order[emoji_code] = emoji_dict["sort_order"]
        emoji_catalog[category].append(emoji_code)

    # Sort the emojis according to iamcal's sort order. This sorting determines the
    # order in which emojis will be displayed in emoji picker.
    for category in emoji_catalog:
        emoji_catalog[category].sort(key=lambda emoji_code: sort_order[emoji_code])

    return dict(emoji_catalog)

# Use only those names for which images are present in all
# the emoji sets so that we can switch emoji sets seemlessly.
def emoji_is_universal(emoji_dict: Dict[str, Any]) -> bool:
    for emoji_set in EMOJISETS:
        if not emoji_dict['has_img_' + emoji_set]:
            return False
    return True

def generate_codepoint_to_name_map(emoji_name_maps: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    codepoint_to_name = {}  # type: Dict[str, str]
    for emoji_code, name_info in emoji_name_maps.items():
        codepoint_to_name[emoji_code] = name_info["canonical_name"]
    return codepoint_to_name

def generate_name_to_codepoint_map(emoji_name_maps: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    name_to_codepoint = {}
    for emoji_code, name_info in emoji_name_maps.items():
        canonical_name = name_info["canonical_name"]
        aliases = name_info["aliases"]
        name_to_codepoint[canonical_name] = emoji_code
        for alias in aliases:
            name_to_codepoint[alias] = emoji_code
    return name_to_codepoint

def get_remapped_emojis_map() -> Dict[str, str]:
    return remapped_emojis
