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
    "0023": "0023-fe0f-20e3",    # Hash
    "0030": "0030-fe0f-20e3",    # Zero
    "0031": "0031-fe0f-20e3",    # One
    "0032": "0032-fe0f-20e3",    # Two
    "0033": "0033-fe0f-20e3",    # Three
    "0034": "0034-fe0f-20e3",    # Four
    "0035": "0035-fe0f-20e3",    # Five
    "0036": "0036-fe0f-20e3",    # Six
    "0037": "0037-fe0f-20e3",    # Seven
    "0038": "0038-fe0f-20e3",    # Eight
    "0039": "0039-fe0f-20e3",    # Nine
    "1f1e8": "1f1e8-1f1f3",      # cn
    "1f1e9": "1f1e9-1f1ea",      # de
    "1f1ea": "1f1ea-1f1f8",      # es
    "1f1eb": "1f1eb-1f1f7",      # fr
    "1f1ec": "1f1ec-1f1e7",      # gb/us
    "1f1ee": "1f1ee-1f1f9",      # it
    "1f1ef": "1f1ef-1f1f5",      # jp
    "1f1f0": "1f1f0-1f1f7",      # kr
    "1f1f7": "1f1f7-1f1fa",      # ru
    "1f1fa": "1f1fa-1f1f8",      # us
}

def emoji_names_for_picker(emoji_name_maps: Dict[str, Dict[str, Any]]) -> List[str]:
    emoji_names = []  # type: List[str]
    for emoji_code, name_info in emoji_name_maps.items():
        emoji_names.append(name_info["canonical_name"])
        emoji_names.extend(name_info["aliases"])

    return sorted(emoji_names)

def get_emoji_code(emoji_dict: Dict[str, Any]) -> str:
    # Starting from version 4.0.0, `emoji_datasource` package has started to
    # add an emoji presentation variation selector for certain emojis which
    # have defined variation sequences. Since in informal environments(like
    # texting and chat), it is more appropriate for an emoji to have a colorful
    # display so until emoji characters have a text presentation selector, it
    # should have a colorful display. Hence we can continue using emoji characters
    # without appending emoji presentation selector.
    # (http://unicode.org/reports/tr51/index.html#Presentation_Style)
    emoji_code = emoji_dict["non_qualified"] or emoji_dict["unified"]
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

def get_remapped_emojis_map(emoji_data: List[Dict[str, Any]]) -> Dict[str, str]:
    # Extend `remapped_emojis` to include emojis whose filename from version 4
    # have a emoji presentation selector(FE0F) appended to them.
    for emoji_dict in emoji_data:
        if emoji_dict['non_qualified'] is not None:
            unified_codepoint = emoji_dict['unified'].lower()
            non_qualified_codepoint = emoji_dict['non_qualified'].lower()
            remapped_emojis[non_qualified_codepoint] = unified_codepoint
    return remapped_emojis
