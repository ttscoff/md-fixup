#!/usr/bin/env python3
"""
Markdown linter that:
1. Normalizes line endings to Unix
2. Trims trailing whitespace (preserves exactly 2 spaces for line breaks)
3. Collapses multiple blank lines (max 1 consecutive, except in code blocks)
4. Normalizes headline spacing (exactly 1 space after #)
5. Ensures blank line after headline
6. Ensures blank line before code block
7. Ensures blank line after code block
8. Ensures blank line before list
9. Ensures blank line after list
10. Ensures blank line before horizontal rule
11. Ensures blank line after horizontal rule
12. Converts list indentation spaces to tabs consistently
13. Normalizes list marker spacing
14. Wraps text at specified width (preserving links, code spans, fenced blocks)
15. Ensures exactly one blank line at end of file
16. Normalizes IAL (Inline Attribute List) spacing for both Kramdown and Pandoc styles
17. Normalizes fenced code block language identifier spacing
18. Normalizes reference-style link definition spacing
19. Normalizes task list checkbox (lowercase x)
20. Normalizes blockquote spacing
21. Normalizes display math block spacing (handles multi-line, preserves currency)
22. Normalizes table formatting (aligns columns, handles relaxed and headerless tables)
23. Normalizes emoji names (spellcheck and correct typos using fuzzy matching)
24. Normalizes typography (curly quotes to straight, en/em dashes, ellipses, guillemets)
25. Normalizes bold/italic markers (bold: always __, italic: always *)
26. Normalizes list markers (renumbers ordered lists, standardizes bullet markers by level)
27. Resets ordered lists to start at 1 (if disabled, preserves starting number)
28. Converts links to numeric reference links
29. Places link definitions at the end of the document (if skipped and reference-links enabled, places at beginning)
30. Converts links to inline format (overrides reference-links if enabled)

Table cleanup script: Dr. Drang <https://leancrew.com/>
"""

import re
import sys
import argparse
import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

VERSION = "0.1.26"
DEFAULT_WRAP_WIDTH = 60

# Valid GitHub emoji names (normalized: lowercase, hyphens to underscores, sorted, deduplicated)
VALID_EMOJI_NAMES = [
    "+1",
    "100",
    "1234",
    "8ball",
    "_1",
    "a",
    "ab",
    "abc",
    "abcd",
    "accept",
    "aerial_tramway",
    "airplane",
    "alarm_clock",
    "alien",
    "ambulance",
    "anchor",
    "angel",
    "anger",
    "angry",
    "anguished",
    "ant",
    "apple",
    "aquarius",
    "aries",
    "arrow_backward",
    "arrow_double_down",
    "arrow_double_up",
    "arrow_down",
    "arrow_down_small",
    "arrow_forward",
    "arrow_heading_down",
    "arrow_heading_up",
    "arrow_left",
    "arrow_lower_left",
    "arrow_lower_right",
    "arrow_right",
    "arrow_right_hook",
    "arrow_up",
    "arrow_up_down",
    "arrow_up_small",
    "arrow_upper_left",
    "arrow_upper_right",
    "arrows_clockwise",
    "arrows_counterclockwise",
    "art",
    "articulated_lorry",
    "astonished",
    "atm",
    "b",
    "baby",
    "baby_bottle",
    "baby_chick",
    "baby_symbol",
    "back",
    "baggage_claim",
    "balloon",
    "ballot_box_with_check",
    "bamboo",
    "banana",
    "bangbang",
    "bank",
    "bar_chart",
    "barber",
    "baseball",
    "basketball",
    "bath",
    "bathtub",
    "battery",
    "bear",
    "bee",
    "beer",
    "beers",
    "beetle",
    "beginner",
    "bell",
    "bento",
    "bicyclist",
    "bike",
    "bikini",
    "bird",
    "birthday",
    "black_circle",
    "black_joker",
    "black_large_square",
    "black_medium_small_square",
    "black_medium_square",
    "black_nib",
    "black_small_square",
    "black_square_button",
    "blossom",
    "blowfish",
    "blue_book",
    "blue_car",
    "blue_heart",
    "blush",
    "boar",
    "boat",
    "bomb",
    "book",
    "bookmark",
    "bookmark_tabs",
    "books",
    "boom",
    "boot",
    "bouquet",
    "bow",
    "bowling",
    "boy",
    "bread",
    "bride_with_veil",
    "bridge_at_night",
    "briefcase",
    "broken_heart",
    "bug",
    "bulb",
    "bullettrain_front",
    "bullettrain_side",
    "bus",
    "busstop",
    "bust_in_silhouette",
    "busts_in_silhouette",
    "cactus",
    "cake",
    "calendar",
    "calling",
    "camel",
    "camera",
    "cancer",
    "candy",
    "capital_abcd",
    "capricorn",
    "car",
    "card_index",
    "carousel_horse",
    "cat",
    "cat2",
    "cd",
    "chart",
    "chart_with_downwards_trend",
    "chart_with_upwards_trend",
    "checkered_flag",
    "cherries",
    "cherry_blossom",
    "chestnut",
    "chicken",
    "children_crossing",
    "chocolate_bar",
    "christmas_tree",
    "church",
    "cinema",
    "circus_tent",
    "city_sunrise",
    "city_sunset",
    "cl",
    "clap",
    "clapper",
    "clipboard",
    "clock1",
    "clock10",
    "clock11",
    "clock12",
    "clock130",
    "clock2",
    "clock230",
    "clock3",
    "clock330",
    "clock4",
    "clock430",
    "clock5",
    "clock530",
    "clock6",
    "clock630",
    "clock7",
    "clock730",
    "clock8",
    "clock830",
    "clock9",
    "clock930",
    "closed_book",
    "closed_lock_with_key",
    "closed_umbrella",
    "cloud",
    "clubs",
    "cn",
    "cocktail",
    "coffee",
    "cold_sweat",
    "collision",
    "computer",
    "confetti_ball",
    "confounded",
    "confused",
    "congratulations",
    "construction",
    "construction_worker",
    "convenience_store",
    "cookie",
    "cool",
    "cop",
    "copyright",
    "corn",
    "couple",
    "couple_with_heart",
    "couplekiss",
    "cow",
    "cow2",
    "credit_card",
    "crescent_moon",
    "crossed_flags",
    "crown",
    "cry",
    "crying_cat_face",
    "crystal_ball",
    "cupid",
    "curly_loop",
    "currency_exchange",
    "curry",
    "custard",
    "customs",
    "dancer",
    "dancers",
    "dango",
    "dart",
    "dash",
    "date",
    "de",
    "deciduous_tree",
    "department_store",
    "diamond_shape_with_a_dot_inside",
    "diamonds",
    "disappointed",
    "disappointed_relieved",
    "dizzy",
    "dizzy_face",
    "do_not_litter",
    "dog",
    "dog2",
    "dollar",
    "dolls",
    "dolphin",
    "donut",
    "door",
    "doughnut",
    "dragon",
    "dragon_face",
    "dress",
    "dromedary_camel",
    "droplet",
    "dvd",
    "ear",
    "ear_of_rice",
    "earth_africa",
    "earth_americas",
    "earth_asia",
    "egg",
    "eggplant",
    "eight",
    "eight_pointed_black_star",
    "eight_spoked_asterisk",
    "electric_plug",
    "elephant",
    "email",
    "end",
    "envelope",
    "envelope_with_arrow",
    "es",
    "euro",
    "european_castle",
    "european_post_office",
    "evergreen_tree",
    "exclamation",
    "expressionless",
    "eyeglasses",
    "eyes",
    "facepunch",
    "factory",
    "fallen_leaf",
    "family",
    "fast_forward",
    "fax",
    "fearful",
    "feelsgood",
    "feet",
    "ferris_wheel",
    "file_folder",
    "finnadie",
    "fire",
    "fireworks",
    "first_quarter_moon",
    "first_quarter_moon_with_face",
    "fish",
    "fish_cake",
    "fishing_pole_and_fish",
    "fist",
    "five",
    "flags",
    "flashlight",
    "flipper",
    "floppy_disk",
    "flower_playing_cards",
    "flushed",
    "foggy",
    "football",
    "footprints",
    "fork_and_knife",
    "fountain",
    "four",
    "four_leaf_clover",
    "fr",
    "free",
    "fried_shrimp",
    "fries",
    "frog",
    "frowning",
    "fu",
    "fuelpump",
    "full_moon",
    "full_moon_with_face",
    "game_die",
    "gb",
    "gem",
    "gemini",
    "ghost",
    "gift",
    "gift_heart",
    "girl",
    "globe_with_meridians",
    "goat",
    "goberserk",
    "godmode",
    "golf",
    "grapes",
    "green_apple",
    "green_book",
    "green_heart",
    "grey_exclamation",
    "grey_question",
    "grimacing",
    "grin",
    "grinning",
    "guardsman",
    "guitar",
    "gun",
    "haircut",
    "hamburger",
    "hammer",
    "hamster",
    "hand",
    "handbag",
    "hankey",
    "hatched_chick",
    "hatching_chick",
    "headphones",
    "hear_no_evil",
    "heart",
    "heart_decoration",
    "heart_eyes",
    "heart_eyes_cat",
    "heartbeat",
    "heartpulse",
    "hearts",
    "heavy_check_mark",
    "heavy_division_sign",
    "heavy_dollar_sign",
    "heavy_exclamation_mark",
    "heavy_minus_sign",
    "heavy_multiplication_x",
    "heavy_plus_sign",
    "helicopter",
    "herb",
    "hibiscus",
    "high_brightness",
    "high_heel",
    "hocho",
    "honey_pot",
    "honeybee",
    "horse",
    "horse_racing",
    "hospital",
    "hotel",
    "hotsprings",
    "hourglass",
    "hourglass_flowing_sand",
    "house",
    "house_with_garden",
    "hushed",
    "ice_cream",
    "icecream",
    "id",
    "ideograph_advantage",
    "imp",
    "inbox_tray",
    "incoming_envelope",
    "information_desk_person",
    "information_source",
    "innocent",
    "interrobang",
    "iphone",
    "it",
    "izakaya_lantern",
    "jack_o_lantern",
    "japan",
    "japanese_castle",
    "japanese_goblin",
    "japanese_ogre",
    "jeans",
    "joy",
    "joy_cat",
    "jp",
    "key",
    "keycap_ten",
    "kimono",
    "kiss",
    "kissing",
    "kissing_cat",
    "kissing_closed_eyes",
    "kissing_heart",
    "kissing_smiling_eyes",
    "koala",
    "koko",
    "kr",
    "large_blue_circle",
    "large_blue_diamond",
    "large_orange_diamond",
    "last_quarter_moon",
    "last_quarter_moon_with_face",
    "laughing",
    "leaves",
    "ledger",
    "left_luggage",
    "left_right_arrow",
    "leftwards_arrow_with_hook",
    "lemon",
    "leo",
    "leopard",
    "libra",
    "light_rail",
    "link",
    "lips",
    "lipstick",
    "lock",
    "lock_with_ink_pen",
    "lollipop",
    "loop",
    "loudspeaker",
    "love_hotel",
    "love_letter",
    "low_brightness",
    "m",
    "mag",
    "mag_right",
    "mahjong",
    "mailbox",
    "mailbox_closed",
    "mailbox_with_mail",
    "mailbox_with_no_mail",
    "man",
    "man_with_gua_pi_mao",
    "man_with_turban",
    "mans_shoe",
    "maple_leaf",
    "mask",
    "massage",
    "meat_on_bone",
    "mega",
    "melon",
    "memo",
    "mens",
    "metal",
    "metro",
    "microphone",
    "microscope",
    "milky_way",
    "minibus",
    "minidisc",
    "mobile_phone_off",
    "money_with_wings",
    "moneybag",
    "monkey",
    "monkey_face",
    "monorail",
    "moon",
    "mortar_board",
    "mount_fuji",
    "mountain_bicyclist",
    "mountain_cableway",
    "mountain_railway",
    "mouse",
    "mouse2",
    "movie_camera",
    "moyai",
    "muscle",
    "mushroom",
    "musical_keyboard",
    "musical_note",
    "musical_score",
    "mute",
    "nail_care",
    "name_badge",
    "neckbeard",
    "necktie",
    "negative_squared_cross_mark",
    "neutral_face",
    "new",
    "new_moon",
    "new_moon_with_face",
    "newspaper",
    "ng",
    "nine",
    "no_bell",
    "no_bicycles",
    "no_entry",
    "no_entry_sign",
    "no_good",
    "no_mobile_phones",
    "no_mouth",
    "no_pedestrians",
    "no_smoking",
    "non_potable_water",
    "nose",
    "notebook",
    "notebook_with_decorative_cover",
    "notes",
    "nut_and_bolt",
    "o",
    "o2",
    "ocean",
    "octocat",
    "octopus",
    "oden",
    "office",
    "ok",
    "ok_hand",
    "ok_woman",
    "older_man",
    "older_woman",
    "on",
    "oncoming_automobile",
    "oncoming_bus",
    "oncoming_police_car",
    "oncoming_taxi",
    "one",
    "open_book",
    "open_file_folder",
    "open_hands",
    "open_mouth",
    "ophiuchus",
    "orange_book",
    "outbox_tray",
    "ox",
    "package",
    "page_facing_up",
    "page_with_curl",
    "pager",
    "palm_tree",
    "panda_face",
    "paperclip",
    "parking",
    "part_alternation_mark",
    "partly_sunny",
    "passport_control",
    "paw_prints",
    "peach",
    "pear",
    "pencil",
    "pencil2",
    "penguin",
    "pensive",
    "performing_arts",
    "persevere",
    "person_frowning",
    "person_with_blond_hair",
    "person_with_pouting_face",
    "phone",
    "pig",
    "pig2",
    "pig_nose",
    "pill",
    "pineapple",
    "pisces",
    "pizza",
    "point_down",
    "point_left",
    "point_right",
    "point_up",
    "point_up_2",
    "police_car",
    "poodle",
    "poop",
    "post_office",
    "postal_horn",
    "postbox",
    "potable_water",
    "pouch",
    "poultry_leg",
    "pound",
    "pray",
    "princess",
    "punch",
    "purple_heart",
    "purse",
    "pushpin",
    "put_litter_in_its_place",
    "question",
    "rabbit",
    "rabbit2",
    "racehorse",
    "radio",
    "radio_button",
    "rage",
    "rage1",
    "rage2",
    "rage3",
    "rage4",
    "railway_car",
    "rainbow",
    "raised_hand",
    "raised_hands",
    "raising_hand",
    "ram",
    "ramen",
    "rat",
    "recycle",
    "red_car",
    "red_circle",
    "registered",
    "relaxed",
    "relieved",
    "repeat",
    "repeat_one",
    "restroom",
    "revolving_hearts",
    "rewind",
    "ribbon",
    "rice",
    "rice_ball",
    "rice_cracker",
    "rice_scene",
    "ring",
    "rocket",
    "roller_coaster",
    "rooster",
    "rose",
    "rotating_light",
    "round_pushpin",
    "rowboat",
    "ru",
    "rugby_football",
    "runner",
    "running",
    "running_shirt_with_sash",
    "sa",
    "sagittarius",
    "sailboat",
    "sake",
    "sandal",
    "santa",
    "satellite",
    "satisfied",
    "saxophone",
    "school",
    "school_satchel",
    "scissors",
    "scorpius",
    "scream",
    "scream_cat",
    "scroll",
    "seat",
    "secret",
    "see_no_evil",
    "seedling",
    "seven",
    "shaved_ice",
    "sheep",
    "shell",
    "ship",
    "shipit",
    "shirt",
    "shit",
    "shoe",
    "shower",
    "signal_strength",
    "six",
    "six_pointed_star",
    "ski",
    "skull",
    "sleeping",
    "sleepy",
    "slot_machine",
    "small_blue_diamond",
    "small_orange_diamond",
    "small_red_triangle",
    "small_red_triangle_down",
    "smile",
    "smile_cat",
    "smiley",
    "smiley_cat",
    "smirk",
    "smirk_cat",
    "smoking",
    "snail",
    "snake",
    "snowboarder",
    "snowflake",
    "snowman",
    "sob",
    "soccer",
    "soon",
    "sos",
    "sound",
    "space_invader",
    "spades",
    "spaghetti",
    "sparkle",
    "sparkler",
    "sparkles",
    "sparkling_heart",
    "speak_no_evil",
    "speaker",
    "speech_balloon",
    "speedboat",
    "squirrel",
    "star",
    "star2",
    "stars",
    "station",
    "statue_of_liberty",
    "steam_locomotive",
    "stew",
    "straight_ruler",
    "strawberry",
    "stuck_out_tongue",
    "stuck_out_tongue_closed_eyes",
    "stuck_out_tongue_winking_eye",
    "sun_with_face",
    "sunflower",
    "sunglasses",
    "sunny",
    "sunrise",
    "sunrise_over_mountains",
    "surfer",
    "sushi",
    "suspect",
    "suspension_railway",
    "sweat",
    "sweat_drops",
    "sweat_smile",
    "sweet_potato",
    "swimmer",
    "symbols",
    "syringe",
    "tada",
    "tanabata_tree",
    "tangerine",
    "taurus",
    "taxi",
    "tea",
    "telephone",
    "telephone_receiver",
    "telescope",
    "tennis",
    "tent",
    "thought_balloon",
    "three",
    "thumbsdown",
    "thumbsup",
    "ticket",
    "tiger",
    "tiger2",
    "tired_face",
    "tm",
    "toilet",
    "tokyo_tower",
    "tomato",
    "tongue",
    "top",
    "tophat",
    "tractor",
    "traffic_light",
    "train",
    "train2",
    "tram",
    "triangular_flag_on_post",
    "triangular_ruler",
    "trident",
    "triumph",
    "trolleybus",
    "trophy",
    "tropical_drink",
    "tropical_fish",
    "truck",
    "trumpet",
    "tshirt",
    "tulip",
    "turtle",
    "tv",
    "twisted_rightwards_arrows",
    "two",
    "two_hearts",
    "two_men_holding_hands",
    "two_women_holding_hands",
    "u5272",
    "u5408",
    "u55b6",
    "u6307",
    "u6708",
    "u6709",
    "u6e80",
    "u7121",
    "u7533",
    "u7981",
    "u7a7a",
    "uk",
    "umbrella",
    "unamused",
    "underage",
    "unlock",
    "up",
    "us",
    "v",
    "vertical_traffic_light",
    "vhs",
    "vibration_mode",
    "video_camera",
    "video_game",
    "violin",
    "virgo",
    "volcano",
    "vs",
    "walking",
    "waning_crescent_moon",
    "waning_gibbous_moon",
    "warning",
    "watch",
    "water_buffalo",
    "watermelon",
    "wave",
    "wavy_dash",
    "waxing_crescent_moon",
    "waxing_gibbous_moon",
    "wc",
    "weary",
    "wedding",
    "whale",
    "whale2",
    "wheelchair",
    "white_check_mark",
    "white_circle",
    "white_flower",
    "white_large_square",
    "white_medium_small_square",
    "white_medium_square",
    "white_small_square",
    "white_square_button",
    "wind_chime",
    "wine_glass",
    "wink",
    "wolf",
    "woman",
    "womans_clothes",
    "womans_hat",
    "womens",
    "worried",
    "wrench",
    "x",
    "yellow_heart",
    "yen",
    "yum",
    "zap",
    "zero",
    "zzz",
]

# Create set for fast lookup
VALID_EMOJI_NAMES_SET = set(VALID_EMOJI_NAMES)

def is_code_block(line):
    """Check if line is a fenced code block delimiter"""
    stripped = line.strip()
    return stripped.startswith('```') or stripped.startswith('~~~')

def is_list_item(line):
    """Check if line is a list item (with or without space after marker)"""
    stripped = line.lstrip()
    # Match list markers with space, or without space followed by non-whitespace
    return bool(re.match(r"^[-*+]\s+|^[-*+][^\s]|^\d+\.\s+", stripped))

def is_headline(line):
    """Check if line is a headline (header)"""
    stripped = line.strip()
    # Match # followed by either whitespace or content (to catch malformed headlines like #BadHeader)
    return bool(re.match(r'^#+\s', stripped) or re.match(r'^#+[^\s#]', stripped))

def is_horizontal_rule(line):
    """Check if line is a horizontal rule"""
    stripped = line.strip()
    return bool(re.match(r'^[-*_]{3,}$', stripped))

def normalize_trailing_whitespace(line):
    """Remove trailing whitespace, but preserve exactly 2 spaces (line break)"""
    # Check if line ends with newline
    has_newline = line.endswith('\n')
    line_no_nl = line.rstrip('\n')

    # Count trailing spaces (before newline)
    trailing_spaces = len(line_no_nl) - len(line_no_nl.rstrip(' '))
    if trailing_spaces == 2:
        # Preserve exactly 2 spaces (markdown line break)
        result = line_no_nl.rstrip('\t') + '  '
    else:
        # Remove all trailing whitespace
        result = line_no_nl.rstrip()

    return result + ('\n' if has_newline else '')

def normalize_headline_spacing(line):
    """Ensure exactly 1 space after # markers"""
    # Preserve newline
    has_newline = line.endswith('\n')
    line_no_nl = line.rstrip('\n')

    match = re.match(r'^(#+)(\s*)(.*)$', line_no_nl)
    if match:
        hashes = match.group(1)
        spaces = match.group(2)
        content = match.group(3)
        # Ensure exactly 1 space
        if spaces != ' ':
            result = hashes + ' ' + content
            return result + ('\n' if has_newline else '')
    return line

def normalize_ial_spacing(line):
    """Normalize IAL (Inline Attribute List) spacing

    Normalizes both Kramdown-style ({: ...}) and Pandoc-style ({...}) IALs:
    - Kramdown: {: #id .class} -> {: #id .class} (space after colon, no trailing space)
    - Pandoc: { #id .class } -> {#id .class} (no space after opening brace, no trailing space)
    - Normalizes spacing between attributes (single space)
    """
    # Preserve newline
    has_newline = line.endswith('\n')
    line_no_nl = line.rstrip('\n')

    # Pattern to match IALs: {: ...} or {...}
    # This matches both Kramdown-style (with colon) and Pandoc-style (without colon)
    # Match opening brace, optional colon, optional whitespace, content, optional whitespace, closing brace
    ial_pattern = r'(\{:?\s*)([^}]*?)(\s*\})'

    def normalize_ial(match):
        opening = match.group(1)  # {: or { with optional space
        content = match.group(2)  # Attributes
        closing = match.group(3)  # } with optional space

        # Normalize content: trim and collapse multiple spaces to single space
        normalized_content = ' '.join(content.split())

        # Determine if it's Kramdown-style (has colon) or Pandoc-style (no colon)
        if ':' in opening:
            # Kramdown-style: {: attributes}
            # Ensure space after colon, no trailing space
            return '{: ' + normalized_content + '}'
        else:
            # Pandoc-style: {attributes}
            # No space after opening brace, no trailing space
            return '{' + normalized_content + '}'

    # Replace all IALs in the line
    normalized = re.sub(ial_pattern, normalize_ial, line_no_nl)
    return normalized + ('\n' if has_newline else '')

def normalize_fenced_code_lang(line):
    """Normalize fenced code block language identifier spacing

    Removes space after opening backticks: ``` python -> ```python
    """
    # Pattern to match fenced code blocks with language identifier
    # Matches ``` or ~~~ followed by optional space and language identifier
    pattern = r'^(```|~~~)\s+([^\s`~]+)'

    def normalize(match):
        fence = match.group(1)
        lang = match.group(2)
        return fence + lang

    normalized = re.sub(pattern, normalize, line)
    return normalized

def normalize_reference_link(line):
    """Normalize reference-style link definition spacing

    Normalizes spacing around colon: [ref] : url -> [ref]: url
    """
    # Pattern to match reference link definitions: [id]: url "title"
    # Matches [id] followed by optional space, colon, optional space, url, optional title
    pattern = r'^(\[[^\]]+\])\s*:\s*'

    def normalize(match):
        return match.group(1) + ': '

    normalized = re.sub(pattern, normalize, line)
    return normalized

def normalize_task_checkbox(line):
    """Normalize task list checkbox to lowercase x

    Converts - [X] to - [x] for consistency
    """
    # Pattern to match task list items with uppercase X
    pattern = r'^(\s*[-*+])\s+(\[[Xx]\])\s+'

    def normalize(match):
        marker = match.group(1)
        checkbox = match.group(2)
        # Convert to lowercase x
        return marker + ' [x] '

    normalized = re.sub(pattern, normalize, line)
    return normalized

def normalize_blockquote_spacing(line):
    """Normalize blockquote spacing

    Ensures space after >: >text -> > text
    """
    # Pattern to match blockquote without space after >
    pattern = r'^(\s*)>([^\s>])'

    def normalize(match):
        indent = match.group(1)
        content = match.group(2)
        return indent + '> ' + content

    normalized = re.sub(pattern, normalize, line)
    return normalized

def normalize_math_spacing(line, is_in_code_block=False):
    """Normalize display math block spacing

    For display math ($$...$$):
    - Single line: $$ text $$ -> $$text$$ (remove spaces inside)
    - Multi-line: No space between opening $$ and first line, or between last line and closing $$

    For inline math ($...$), be conservative - only normalize if clearly math (not currency).
    """
    if is_in_code_block:
        return line

    # Preserve newline
    has_newline = line.endswith('\n')
    line_no_nl = line.rstrip('\n')

    # Pattern for display math: $$...$$
    # This handles both single-line and multi-line (using DOTALL to match across newlines)
    display_math_pattern = r'\$\$([\s\S]*?)\$\$'

    def normalize_display_math(match):
        content = match.group(1)
        # For multi-line, remove leading/trailing whitespace but preserve internal newlines
        # Split by newlines, strip first and last lines, rejoin
        lines = content.split('\n')
        if len(lines) > 1:
            # Multi-line: strip first and last lines, preserve middle
            if lines[0].strip() == '':
                lines = lines[1:]
            if lines and lines[-1].strip() == '':
                lines = lines[:-1]
            if lines:
                lines[0] = lines[0].lstrip()
                lines[-1] = lines[-1].rstrip()
            normalized = '\n'.join(lines)
        else:
            # Single line: just strip
            normalized = content.strip()
        return '$$' + normalized + '$$'

    # Replace display math blocks (using DOTALL flag to match across newlines)
    normalized = re.sub(display_math_pattern, normalize_display_math, line_no_nl, flags=re.DOTALL)

    # For inline math, be very conservative - only normalize if it looks like math
    # (contains operators, letters, or is clearly mathematical)
    # Skip currency patterns like $1.50, $2, etc.
    # Also skip if closing $ has space before it and non-space after it (not math)
    inline_math_pattern = r'\$([^\$]+?)\$'

    def normalize_inline_math(match):
        content = match.group(1)
        match_end = match.end()

        # Check if closing $ has space before it and non-space after it
        has_space_before_closing = content.endswith(' ') or content.endswith('\t')
        has_non_space_after = (match_end < len(normalized) and
                              not normalized[match_end].isspace())

        # If closing $ has space before it AND non-space after it, skip normalization (not math)
        if has_space_before_closing and has_non_space_after:
            return match.group(0)  # Return original unchanged

        # Otherwise, check if it looks like currency
        trimmed_content = content.strip()
        if re.match(r'^[\d.,\s]+$', trimmed_content):
            # Looks like currency, don't normalize
            return '$' + content + '$'
        # Looks like math, normalize spacing
        return '$' + trimmed_content + '$'

    # Replace inline math (conservatively)
    normalized = re.sub(inline_math_pattern, normalize_inline_math, normalized)

    return normalized + ('\n' if has_newline else '')

def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def normalize_emoji_name(name):
    """Normalize emoji name: lowercase, hyphens to underscores, remove colons"""
    name = name.strip(':')
    name = name.lower()
    name = name.replace('-', '_')
    return name

def find_best_emoji_match(name, max_distance=4):
    """Find best emoji match using fuzzy matching

    Returns the shortest matching emoji name within max_distance, or None if no match.
    """
    normalized = normalize_emoji_name(name)

    # Check exact match first
    if normalized in VALID_EMOJI_NAMES_SET:
        return normalized

    # Find fuzzy matches
    candidates = []
    for emoji_name in VALID_EMOJI_NAMES:
        distance = levenshtein_distance(normalized, emoji_name)
        if distance <= max_distance:
            candidates.append((distance, len(emoji_name), emoji_name))

    if not candidates:
        return None

    # Sort by distance (lowest first), then by length (shortest first)
    candidates.sort(key=lambda x: (x[0], x[1]))
    return candidates[0][2]

def normalize_emoji_names(line):
    """Normalize emoji names in a line, correcting typos using fuzzy matching"""
    # Pattern to match :emoji_name: (alphanumeric, underscores, hyphens, plus signs)
    pattern = r':([a-zA-Z0-9_+-]+):'

    def replace_emoji(match):
        emoji_name = match.group(1)
        normalized = normalize_emoji_name(emoji_name)

        # Check if it's already correct
        if normalized in VALID_EMOJI_NAMES_SET:
            return f':{normalized}:'

        # Try fuzzy matching
        best_match = find_best_emoji_match(emoji_name, max_distance=4)
        if best_match:
            return f':{best_match}:'

        # No match found, return original
        return match.group(0)

    return re.sub(pattern, replace_emoji, line)

def normalize_typography(line, skip_em_dash=False, skip_guillemet=False):
    """Normalize typography: curly quotes, dashes, ellipses, guillemets

    Args:
        line: Line to normalize
        skip_em_dash: If True, leave em dashes as-is
        skip_guillemet: If True, leave guillemets as-is
    """
    result = line

    # Curly quotes to straight quotes
    result = result.replace('"', '"')  # Left double quote
    result = result.replace('"', '"')  # Right double quote
    result = result.replace(''', "'")   # Left single quote
    result = result.replace(''', "'")   # Right single quote

    # En dash to --
    result = result.replace('–', '--')  # U+2013

    # Em dash to --- (unless skipped)
    if not skip_em_dash:
        result = result.replace('—', '---')  # U+2014

    # Ellipsis to ...
    result = result.replace('…', '...')  # U+2026

    # Guillemets to quotes (unless skipped)
    if not skip_guillemet:
        result = result.replace('«', '"')  # U+00AB
        result = result.replace('»', '"')  # U+00BB

    return result

def normalize_bold_italic(line, reverse_emphasis=False):
    """Normalize bold and italic markers

    - Bold: always use __ (not **), or reversed: ** (not __)
    - Italics: always use * (not _), or reversed: _ (not *)
    - Handle nested: **_text_** → __*text*__ (or reversed: *__text__* → _**text**_)
    - Handle triple: ***text*** → __*text*__ (or reversed: ___text___ → **text**)
    - Skip inside code spans, code blocks, and emoji markers
    """
    # First, identify protected regions (code spans, emoji markers)
    # Code spans: `code` or ``code``
    code_span_pattern = r'`+[^`]*`+'
    # Emoji markers: :emoji_name:
    emoji_pattern = r':[a-z0-9_+-]+:'

    # Collect all protected regions
    protected_ranges = []

    for match in re.finditer(code_span_pattern, line):
        protected_ranges.append((match.start(), match.end()))

    for match in re.finditer(emoji_pattern, line):
        protected_ranges.append((match.start(), match.end()))

    # Sort and merge overlapping ranges
    protected_ranges.sort()
    merged = []
    for start, end in protected_ranges:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    # Helper to check if a position is in a protected region
    def is_protected(pos):
        return any(start <= pos < end for start, end in merged)

    # Helper to replace only if not in protected region
    def replace_if_not_protected(pattern, replacement):
        def replacer(match):
            if is_protected(match.start()):
                return match.group(0)
            return re.sub(pattern, replacement, match.group(0))
        return replacer

    result = line

    if reverse_emphasis:
        # Reversed: ** for bold, _ for italic
        # Handle ALL bold-italic combinations first (before standalone patterns)
        # All should normalize to: _**text**_

        # General approach: match any 3-marker combo and normalize to _**text**_
        def normalize_bold_italic_reverse_general(match):
            if is_protected(match.start()):
                return match.group(0)
            opening = match.group(1)
            content = match.group(2)
            closing = match.group(3)

            # Verify closing is reverse of opening
            expected_closing = opening[::-1]
            if closing != expected_closing:
                return match.group(0)

            # Normalize to _**content**_
            return f'_**{content}**_'

        # Match any 3 markers + content + any 3 markers, verify balanced
        result = re.sub(r'([_*]{3})(.+?)([_*]{3})', normalize_bold_italic_reverse_general, result)

        # Now handle standalone bold and italic
        # Bold with __ → **
        def replace_bold_rev(match):
            if is_protected(match.start()):
                return match.group(0)
            return f'**{match.group(1)}**'
        result = re.sub(r'(?<!_)__([^_]+?)__(?!_)', replace_bold_rev, result)

        # Italics with * → _
        def replace_italic_rev(match):
            if is_protected(match.start()):
                return match.group(0)
            return f'_{match.group(1)}_'
        result = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', replace_italic_rev, result)
    else:
        # Normal: __ for bold, * for italic
        # Handle ALL bold-italic combinations first (before standalone patterns)
        # All should normalize to: __*text*__
        # A bold-italic combo has exactly 3 markers total (any combination of _ and *)

        # General approach: match any 3-character combination of _ and * at start,
        # then content (non-greedy), then verify closing markers are reverse of opening
        def normalize_bold_italic_general(match):
            if is_protected(match.start()):
                return match.group(0)
            # Group 1: opening markers (3 chars of _ and *)
            # Group 2: content
            # Group 3: closing markers
            opening = match.group(1)
            content = match.group(2)
            closing = match.group(3)

            # Verify closing is reverse of opening (ensures balanced bold-italic combo)
            expected_closing = opening[::-1]
            if closing != expected_closing:
                # Not a valid bold-italic combo (e.g., ***text___), return original
                return match.group(0)

            # Normalize to __*content*__
            return f'__*{content}*__'

        # Match any 3 markers + content + any 3 markers, then verify they're balanced
        # Use \S to ensure content starts with non-whitespace (avoids matching across word boundaries incorrectly)
        # But allow whitespace in the middle of content
        # Pattern: ([_*]{3})(\S.*?\S)([_*]{3}) - ensures content has at least 2 non-whitespace chars
        # However, this might be too restrictive. Let's use a simpler approach:
        # Match any 3 markers, then non-greedy content (at least 1 char), then any 3 markers
        result = re.sub(r'([_*]{3})(.+?)([_*]{3})', normalize_bold_italic_general, result)

        # Now handle standalone bold and italic
        # Bold with ** → __
        # Don't match if followed by _ (that's a nested pattern like **_text_**)
        def replace_bold(match):
            if is_protected(match.start()):
                return match.group(0)
            return f'__{match.group(1)}__'
        # Negative lookbehind: not preceded by *
        # Negative lookahead: not followed by * or _ (to avoid matching nested patterns)
        # Use .+? instead of [^*]+? to allow * in content (for nested italic)
        result = re.sub(r'(?<!\*)\*\*(.+?)\*\*(?![*_])', replace_bold, result)

        # Italics with _ → *
        def replace_italic(match):
            if is_protected(match.start()):
                return match.group(0)
            return f'*{match.group(1)}*'
        result = re.sub(r'(?<!_)_([^_]+?)_(?!_)', replace_italic, result)

    return result

def is_table_row(line):
    """Check if line is a table row (contains pipe characters)"""
    stripped = line.strip()
    # Must contain at least one pipe
    if '|' not in stripped:
        return False
    # Not a separator row (separator rows contain only |, :, -, spaces)
    if set(stripped.replace('|', '')).issubset(':- '):
        return False
    return True

def is_separator_row(line):
    """Check if line is a table separator row"""
    stripped = line.strip()
    # Must contain at least one pipe
    if '|' not in stripped:
        return False
    # Separator rows contain only |, :, -, spaces
    return set(stripped.replace('|', '')).issubset(':- ')

def count_columns(line):
    """Count the number of columns in a table row"""
    stripped = line.strip()
    if not stripped:
        return 0

    # Count pipes
    pipe_count = stripped.count('|')

    # If line starts with |, subtract 1 (leading pipe creates empty first cell)
    if stripped.startswith('|'):
        return pipe_count - 1
    else:
        return pipe_count + 1

def normalize_table_formatting(table_lines):
    """Normalize table formatting using Dr. Drang's algorithm

    Adapted to handle:
    - Standard tables (header + separator + data)
    - Relaxed tables (data rows only, no separator)
    - Headerless tables (separator first, then data)

    Returns normalized table lines or None if not a valid table.
    """
    if not table_lines:
        return None

    # Remove empty lines
    lines = [line.rstrip('\n') for line in table_lines if line.strip()]
    if len(lines) < 2:
        return None

    # Check if all lines are table-related
    if not all('|' in line for line in lines):
        return None

    # Determine table type and find separator
    separator_idx = None
    is_headerless = False
    is_relaxed = True

    # Check if first line is a separator (headerless table)
    if is_separator_row(lines[0]):
        is_headerless = True
        is_relaxed = False
        separator_idx = 0
    else:
        # Look for separator in the lines
        for i, line in enumerate(lines):
            if is_separator_row(line):
                separator_idx = i
                is_relaxed = False
                break

    # If no separator found, it's a relaxed table - insert default separator
    if separator_idx is None:
        # Count columns from first row
        num_cols = count_columns(lines[0])
        if num_cols <= 0:
            return None
        # Insert default separator (all left-aligned, no colons)
        default_separator = '|' + '|'.join([' --- ' for _ in range(num_cols)]) + '|'
        lines.insert(1, default_separator)
        separator_idx = 1

    # Extract separator line and determine alignment
    formatline = lines[separator_idx].strip()
    if not formatline:
        return None
    if formatline[0] == '|':
        formatline = formatline[1:]
    if formatline and formatline[-1] == '|':
        formatline = formatline[:-1]

    fstrings = formatline.split('|')
    justify = []
    for cell in fstrings:
        cell = cell.strip()
        ends = (cell[0] if cell else '') + (cell[-1] if cell else '')
        if ends == '::':
            justify.append('::')
        elif ends == '-:':
            justify.append('-:')
        else:
            justify.append(':-')

    columns = len(justify)

    # Extract content rows (skip separator)
    content_lines = [line for i, line in enumerate(lines) if i != separator_idx]

    # Extract content into matrix
    content = []
    for line in content_lines:
        stripped = line.strip()
        if not stripped:
            # Empty line, skip it
            continue
        if stripped[0] == '|':
            stripped = stripped[1:]
        if stripped and stripped[-1] == '|':
            stripped = stripped[:-1]
        cells = stripped.split('|')
        # Put exactly one space at each end as "bumpers"
        linecontent = [' ' + x.strip() + ' ' for x in cells]
        content.append(linecontent)

    # Append cells to rows that don't have enough
    for i in range(len(content)):
        while len(content[i]) < columns:
            content[i].append(' ')

    # Get width of content in each column
    widths = [2] * columns
    for row in content:
        for i in range(columns):
            # Use len() which handles Unicode correctly in Python 3
            widths[i] = max(len(row[i]), widths[i])

    # Justify function
    def just(string, type, n):
        """Justify a string to length n according to type."""
        if type == '::':
            return string.center(n)
        elif type == '-:':
            return string.rjust(n)
        elif type == ':-':
            return string.ljust(n)
        else:
            return string

    # Format rows
    formatted = []
    for row in content:
        formatted.append('|' + '|'.join([just(s, t, n) for (s, t, n) in zip(row, justify, widths)]) + '|')

    # Recreate format line with appropriate column widths
    formatline = '|' + '|'.join([s[0] + '-' * (n - 2) + s[-1] for (s, n) in zip(justify, widths)]) + '|'

    # Insert separator back in correct position
    if is_headerless:
        # Separator goes first
        formatted.insert(0, formatline)
    else:
        # Separator goes after first row (header)
        formatted.insert(1, formatline)

    # Add newlines back
    return [line + '\n' for line in formatted]

def detect_list_indent_unit(lines, start_idx):
    """Detect the base indentation unit for a list (2 or 4 spaces)
    Looks backwards to find the start of the list, then forward to find first indented item
    Returns the number of spaces used for the first indentation level, or 2 if none found
    """
    # Find the start of this list (first unindented list item)
    list_start = start_idx
    for i in range(start_idx, -1, -1):
        if i < 0:
            break
        line = lines[i]
        if not is_list_item(line):
            # Hit a non-list item, the list starts at the next line
            list_start = i + 1
            break
        # Check if this is an unindented list item (start of list)
        match = re.match(r'^(\s*)([-*+]|\d+\.)', line)
        if match:
            indent = match.group(1)
            space_count = len(indent.replace('\t', ''))
            if space_count == 0:
                # Found the start of the list
                list_start = i
                break

    # Now scan forward from list start to find first indented item
    for i in range(list_start + 1, len(lines)):
        line = lines[i]
        if not is_list_item(line):
            # If we hit a non-list item, stop looking
            if line.strip():
                break
            continue

        # Get indentation (spaces only, ignore tabs)
        match = re.match(r'^(\s*)([-*+]|\d+\.)', line)
        if match:
            indent = match.group(1)
            space_count = len(indent.replace('\t', ''))
            if space_count >= 2:
                # Found first indentation - return it as base unit
                # Round to nearest 2 or 4
                if space_count >= 4:
                    return 4
                else:
                    return 2

    # Default to 2 spaces if no indented item found
    return 2

def spaces_to_tabs_for_list(line, indent_unit):
    """Convert list indentation spaces to tabs based on detected indent unit
    If indent_unit is 2: 2 spaces = 1 tab, 4 spaces = 2 tabs, etc.
    If indent_unit is 4: 4 spaces = 1 tab, 8 spaces = 2 tabs, etc.
    """
    if not is_list_item(line):
        return line

    # Preserve newline
    has_newline = line.endswith('\n')
    line_no_nl = line.rstrip('\n')

    # Match list items with or without space after marker
    match = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', line_no_nl)
    if match:
        indent = match.group(1)
        marker = match.group(2)
        marker_space = match.group(3)
        content = match.group(4)

        # Normalize: ensure exactly one space after marker
        if marker_space != ' ':
            marker_space = ' '

        # Check if already using tabs
        if '\t' in indent:
            # Already has tabs, keep as is
            return line

        # Count leading spaces (ignore tabs if any)
        space_count = len(indent.replace('\t', ''))

        # Convert based on indent_unit
        # If indent_unit is 2: 2 spaces = 1 tab, 4 spaces = 2 tabs, etc.
        # If indent_unit is 4: 4 spaces = 1 tab, 8 spaces = 2 tabs, etc.
        if space_count > 0:
            tabs = '\t' * (space_count // indent_unit)
        else:
            tabs = ''

        result = tabs + marker + marker_space + content
        return result + ('\n' if has_newline else '')

    return line

def get_list_indent(line):
    """Get the indentation level of a list item"""
    match = re.match(r'^(\s*)', line)
    return len(match.group(1)) if match else 0

def get_list_level(indent_str, indent_unit=2):
    """Get the list nesting level (0-based) based on indentation"""
    # Count tabs and spaces
    tab_count = indent_str.count('\t')
    space_count = len(indent_str.replace('\t', ''))
    # Convert spaces to equivalent tabs based on indent_unit
    total_indent = tab_count + (space_count // indent_unit)
    return total_indent

def normalize_list_markers(line, list_context_stack, indent_unit=2, skip_list_reset=False):
    """Normalize list markers based on indentation level

    Args:
        line: The list item line to normalize
        list_context_stack: List of (level, list_type, current_number) tuples tracking list state
        indent_unit: Base indentation unit (2 or 4 spaces per tab)
        skip_list_reset: If True, preserve starting number; if False (default), always start at 1

    Returns:
        (normalized_line, updated_stack, changed)
    """
    if not is_list_item(line):
        return line, list_context_stack, False

    match = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', line)
    if not match:
        return line, list_context_stack, False

    indent = match.group(1)
    marker = match.group(2)
    marker_space = match.group(3)
    content = match.group(4)

    # Calculate current level
    current_level = get_list_level(indent, indent_unit)

    # Determine if this is a numbered list or bulleted list
    is_numbered = bool(re.match(r'^\d+\.', marker))

    # Update the stack - remove contexts for deeper levels (but keep same or shallower)
    # This allows us to return to previous levels and continue those lists
    list_context_stack = [ctx for ctx in list_context_stack if ctx[0] <= current_level]

    # Check if we have a context for this exact level
    matching_context = None
    for ctx in reversed(list_context_stack):
        if ctx[0] == current_level:
            matching_context = ctx
            break

    if matching_context:
        # Continue existing list at this level
        level, list_type, current_number = matching_context
        idx = list_context_stack.index(matching_context)

        if list_type == 'numbered':
            # Continue numbering
            current_number += 1
            list_context_stack[idx] = (level, list_type, current_number)
            new_marker = f'{current_number}.'
        else:
            # Bulleted list - use marker based on level
            if current_level == 0:
                new_marker = '*'
            elif current_level == 1:
                new_marker = '-'
            else:
                new_marker = '+'
    else:
        # New list at this level
        if is_numbered:
            # Extract starting number from marker (e.g., "7." -> 7)
            if skip_list_reset:
                # If list-reset is disabled, preserve the starting number
                start_number = int(marker.rstrip('.'))
            else:
                # If list-reset is enabled (default), always start at 1
                start_number = 1
            list_context_stack.append((current_level, 'numbered', start_number))
            new_marker = f'{start_number}.'
        else:
            list_context_stack.append((current_level, 'bulleted', None))
            # Determine bullet marker based on level
            if current_level == 0:
                new_marker = '*'
            elif current_level == 1:
                new_marker = '-'
            else:
                new_marker = '+'

    # Check if marker changed
    changed = (marker != new_marker)

    # Build new line
    # Ensure exactly one space after marker for consistency
    if marker_space != ' ':
        marker_space = ' '
    has_newline = line.endswith('\n')
    normalized = indent + new_marker + marker_space + content
    if has_newline:
        normalized += '\n'

    return normalized, list_context_stack, changed

def is_blockquote(line):
    """Check if line is a blockquote"""
    stripped = line.lstrip()
    return stripped.startswith('>')

def get_blockquote_prefix(line):
    """Get the blockquote prefix (including spaces)"""
    match = re.match(r'^(\s*)', line)
    spaces = match.group(1) if match else ''
    if line.lstrip().startswith('>'):
        return spaces + '>'
    return ''

def should_preserve_line(line):
    """Check if line should not be wrapped (code blocks, headers, etc.)"""
    stripped = line.strip()
    # Fenced code blocks
    if is_code_block(line):
        return True
    # Headers
    if stripped.startswith('#'):
        return True
    # Horizontal rules
    if is_horizontal_rule(line):
        return True
    # Note: blank lines are NOT preserved here - they go through blank line compression
    return False

def wrap_text(text, width, prefix=''):
    """Wrap text at width, preserving links and code spans"""
    # Always include prefix in the first line
    full_first_line = prefix + text
    if len(full_first_line) <= width:
        return [full_first_line]

    # Don't wrap if it contains a long link or code span
    if re.search(r'\[.*?\]\([^)]{20,}\)', text):
        return [full_first_line]
    if re.search(r'`[^`]{20,}`', text):
        return [full_first_line]

    words = text.split()
    lines = []
    current_line = prefix

    for word in words:
        # Check if adding this word would exceed width
        test_line = current_line + (' ' if current_line != prefix else '') + word
        if len(test_line) <= width:
            current_line = test_line
        else:
            if current_line != prefix:
                lines.append(current_line)
            current_line = prefix + word

    if current_line != prefix:
        lines.append(current_line)

    return lines if lines else [full_first_line]

# Define linting rules (numbered for --skip flag)
LINTING_RULES = {
    1: ("Normalize line endings to Unix", "line-endings"),
    2: ("Trim trailing whitespace (preserve exactly 2 spaces)", "trailing"),
    3: ("Collapse multiple blank lines (max 1 consecutive)", "blank-lines"),
    4: ("Normalize headline spacing (exactly 1 space after #)", "header-spacing"),
    5: ("Ensure blank line after headline", "header-newline"),
    6: ("Ensure blank line before code block", "code-before"),
    7: ("Ensure blank line after code block", "code-after"),
    8: ("Ensure blank line before list", "list-before"),
    9: ("Ensure blank line after list", "list-after"),
    10: ("Ensure blank line before horizontal rule", "rule-before"),
    11: ("Ensure blank line after horizontal rule", "rule-after"),
    12: ("Convert list indentation spaces to tabs", "list-tabs"),
    13: ("Normalize list marker spacing", "list-marker"),
    14: ("Wrap text at specified width", "wrap"),
    15: ("Ensure exactly one blank line at end of file", "end-newline"),
    16: ("Normalize IAL spacing", "ial-spacing"),
    17: ("Normalize fenced code block language identifier spacing", "code-lang-spacing"),
    18: ("Normalize reference-style link definition spacing", "ref-link-spacing"),
    19: ("Normalize task list checkbox (lowercase x)", "task-checkbox"),
    20: ("Normalize blockquote spacing", "blockquote-spacing"),
    21: ("Normalize display math block spacing", "math-spacing"),
    22: ("Normalize table formatting", "table-format"),
    23: ("Normalize emoji names (spellcheck and correct)", "emoji-spellcheck"),
    24: ("Normalize typography (curly quotes, dashes, ellipses, guillemets). Sub-keywords: em-dash, guillemet", "typography"),
    25: ("Normalize bold/italic markers (bold: __, italic: *)", "bold-italic"),
    26: ("Normalize list markers (renumber ordered lists, standardize bullet markers by level)", "list-markers"),
    27: ("Reset ordered lists to start at 1 (if disabled, preserve starting number)", "list-reset"),
    28: ("Convert links to numeric reference links", "reference-links"),
    29: ("Place link definitions at the end of the document (if skipped and reference-links enabled, places at beginning)", "links-at-end"),
    30: ("Convert links to inline format (overrides reference-links if enabled)", "inline-links"),
}

# Create keyword to rule number mapping
KEYWORD_TO_RULE = {desc[1]: num for num, desc in LINTING_RULES.items()}
# Add alias for emphasis
KEYWORD_TO_RULE['emphasis'] = 25

def get_top_level_element_end(lines, start_idx):
    """Find the end of a top-level element (paragraph, list, etc.)

    Returns the index of the last line of the element (inclusive)
    For nested lists, finds the end of the top-level list, not the nested item.
    """
    if start_idx >= len(lines):
        return start_idx

    line = lines[start_idx]
    stripped = line.strip()

    # Empty line ends a paragraph
    if not stripped:
        return start_idx

    # Headline
    if is_headline(line):
        return start_idx

    # List item - find end of top-level list
    if is_list_item(line):
        current_indent = len(line) - len(line.lstrip())

        # If nested, find top-level list start
        if current_indent > 0:
            top_level_start = start_idx
            for i in range(start_idx, -1, -1):
                if i < 0:
                    break
                prev_line = lines[i]
                if not is_list_item(prev_line):
                    top_level_start = i + 1
                    break
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                if prev_indent == 0:
                    top_level_start = i
                    break
        else:
            top_level_start = start_idx

        # Find end of top-level list
        i = top_level_start
        last_top_level_item = top_level_start

        while i < len(lines):
            current = lines[i]
            if not current.strip():
                # Blank line - check if list continues
                if i + 1 < len(lines) and is_list_item(lines[i + 1]):
                    next_line = lines[i + 1]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent == 0:
                        i += 1
                        continue
                    i += 1
                    continue
                return last_top_level_item

            if is_list_item(current):
                current_indent = len(current) - len(current.lstrip())
                if current_indent == 0:
                    last_top_level_item = i
                i += 1
                continue

            # Non-list line - check if indented continuation
            if current.strip().startswith('\t') or (current.strip().startswith(' ') and len(current) - len(current.lstrip()) > 0):
                i += 1
                continue

            # Non-list, non-indented line ends the list
            return last_top_level_item

        return last_top_level_item

    # Blockquote - find end of blockquote
    if is_blockquote(line):
        i = start_idx + 1
        while i < len(lines):
            current = lines[i]
            if not current.strip():
                if i + 1 < len(lines) and is_blockquote(lines[i + 1]):
                    i += 1
                    continue
                return i - 1
            if is_blockquote(current):
                i += 1
                continue
            return i - 1
        return len(lines) - 1

    # Paragraph - ends at blank line or other block element
    i = start_idx + 1
    while i < len(lines):
        current = lines[i]
        if not current.strip():
            return i - 1
        if (is_headline(current) or is_list_item(current) or
            is_code_block(current) or is_horizontal_rule(current) or
            is_blockquote(current)):
            return i - 1
        i += 1
    return len(lines) - 1

def convert_links_in_document(lines, use_inline, use_reference, place_at_beginning):
    """Convert all links in the document using approach similar to formd gist

    Based on: https://gist.github.com/ttscoff/3907181
    """
    if not use_inline and not use_reference:
        return lines

    # Make a copy to avoid modifying the original during iteration
    lines = list(lines)

    # First, collect all existing reference definitions
    # Pattern: [id]: url or [id]: url "title"
    ref_def_pattern = re.compile(r'^(\[[^\]]+\])\s*:\s*(.+)$')
    ref_definitions = {}  # Maps ref_id -> (url, title)
    ref_def_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        match = ref_def_pattern.match(stripped)
        if match:
            ref_id = match.group(1)
            url_part = match.group(2).strip()

            # Extract URL and optional title
            url_match = re.match(r'^([^\s"]+)(?:\s+"([^"]+)")?$', url_part)
            if url_match:
                url = url_match.group(1)
                title = url_match.group(2) if url_match.group(2) else None
            else:
                url = url_part
                title = None

            ref_definitions[ref_id] = (url, title)
            # Also store normalized version for implicit links
            if ref_id.startswith('[') and ref_id.endswith(']'):
                ref_text = ref_id[1:-1].lower().strip()
                normalized_id = f'[{ref_text}]'
                if normalized_id != ref_id:
                    ref_definitions[normalized_id] = (url, title)
            ref_def_lines.append(i)

    # Remove reference definition lines
    for line_idx in reversed(ref_def_lines):
        lines.pop(line_idx)

    # Now find all links in the document
    # Pattern similar to gist: [text][ref] or [text](url)
    match_links = re.compile(r'(\[.*?\])\s?(\[.*?\]|\(.*?\))', re.DOTALL)

    # Track code block state
    in_code_block = False

    # Helper to check if position is in code span
    def is_in_code_span(text, pos):
        before = text[:pos]
        backticks = 0
        i = 0
        while i < len(before):
            if before[i] == '`':
                backticks += 1
                while i + 1 < len(before) and before[i + 1] == '`':
                    i += 1
                    backticks += 1
                i += 1
            elif before[i] == '\\':
                i += 2
            else:
                i += 1
        return backticks % 2 == 1

    # Collect all links with their positions and URLs
    # link_data format: (line_idx, match_start, match_end, link_text, url, title, link_type, ref_id)
    # link_type: 'inline', 'reference', 'implicit'
    # ref_id: original reference ID (for 'reference' and 'implicit' types), None for 'inline'
    link_data = []

    for i, line in enumerate(lines):
        # Track code blocks
        if is_code_block(line):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Track positions we've already matched to avoid duplicates
        matched_positions = set()

        # Find inline links: [text](url) or [text](url "title")
        inline_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        for match in inline_pattern.finditer(line):
            if is_in_code_span(line, match.start()):
                continue
            # Check if this position overlaps with a previously matched link
            pos_key = (i, match.start(), match.end())
            if pos_key in matched_positions:
                continue
            matched_positions.add(pos_key)

            link_text = match.group(1)
            url_part = match.group(2)

            # Extract URL and title
            url_match = re.match(r'^([^\s"]+)(?:\s+"([^"]+)")?$', url_part)
            if url_match:
                url = url_match.group(1)
                title = url_match.group(2)
            else:
                url = url_part
                title = None

            link_data.append((i, match.start(), match.end(), link_text, url, title, 'inline', None))

        # Find reference links: [text][ref]
        ref_pattern = re.compile(r'\[([^\]]+)\]\[([^\]]+)\]')
        for match in ref_pattern.finditer(line):
            if is_in_code_span(line, match.start()):
                continue
            # Check if this position overlaps with a previously matched link
            pos_key = (i, match.start(), match.end())
            if pos_key in matched_positions:
                continue
            matched_positions.add(pos_key)

            link_text = match.group(1)
            ref_id = match.group(2)

            # Look up URL from definitions
            ref_key = f'[{ref_id}]'
            if ref_key in ref_definitions:
                url, title = ref_definitions[ref_key]
                # Preserve existing reference links with their original ID
                link_data.append((i, match.start(), match.end(), link_text, url, title, 'reference', ref_id))
            else:
                # Reference link without definition - treat as inline and convert
                # This shouldn't normally happen, but handle it gracefully
                link_data.append((i, match.start(), match.end(), link_text, None, None, 'inline', None))

        # Find implicit reference links: [text] (without explicit ref)
        # But only if it's not already part of a reference or inline link we found above
        implicit_pattern = re.compile(r'\[([^\]]+)\](?![\[\(])')
        for match in implicit_pattern.finditer(line):
            if is_in_code_span(line, match.start()):
                continue
            # Check if this position overlaps with a previously matched link
            already_covered = False
            for existing_line_idx, existing_start, existing_end in [(p[0], p[1], p[2]) for p in matched_positions if p[0] == i]:
                if existing_start <= match.start() < existing_end:
                    already_covered = True
                    break
            if already_covered:
                continue

            link_text = match.group(1)
            ref_id_normalized = f'[{link_text.lower().strip()}]'

            if ref_id_normalized in ref_definitions:
                url, title = ref_definitions[ref_id_normalized]
                pos_key = (i, match.start(), match.end())
                matched_positions.add(pos_key)
                # Preserve implicit reference links - use the normalized ID as the ref_id
                # Find the actual ref_id that was used in definitions (might be different case)
                actual_ref_id = None
                for def_ref_id in ref_definitions.keys():
                    if def_ref_id.lower() == ref_id_normalized.lower():
                        actual_ref_id = def_ref_id[1:-1]  # Remove brackets
                        break
                if actual_ref_id is None:
                    actual_ref_id = link_text.lower().strip()
                link_data.append((i, match.start(), match.end(), link_text, url, title, 'implicit', actual_ref_id))

    # Convert links based on mode
    if use_inline:
        # Convert all to inline format (process in reverse to maintain positions)
        link_data_reversed = sorted(link_data, key=lambda x: (x[0], x[1]), reverse=True)
        for link_item in link_data_reversed:
            line_idx, start, end, link_text, url, title, link_type, ref_id = link_item
            if not url:  # Skip if no URL
                continue
            line = lines[line_idx]
            if title:
                replacement = f'[{link_text}]({url} "{title}")'
            else:
                replacement = f'[{link_text}]({url})'
            lines[line_idx] = line[:start] + replacement + line[end:]

    elif use_reference:
        # Track text-based reference IDs and their URLs (for preserving existing refs)
        text_ref_to_url = {}  # Maps ref_id -> (url, title)
        # Track which text-based refs we've seen in the document (for ordering)
        text_ref_order = []  # List of ref_ids in document order
        
        # Track numeric references for inline links only
        url_to_ref = {}  # Maps (url, title) -> ref_num
        next_ref = 1

        # First pass: collect text-based reference IDs (including numeric ones)
        for link_item in link_data:
            line_idx, start, end, link_text, url, title, link_type, ref_id = link_item
            
            if link_type == 'reference':
                # Preserve existing reference links - track their ID and URL
                if ref_id and url:  # Only if we have both
                    text_ref_to_url[ref_id] = (url, title)
                    if ref_id not in text_ref_order:
                        text_ref_order.append(ref_id)
            elif link_type == 'implicit':
                # Preserve implicit reference links - track their ID and URL
                if ref_id and url:  # Only if we have both
                    text_ref_to_url[ref_id] = (url, title)
                    if ref_id not in text_ref_order:
                        text_ref_order.append(ref_id)

        # Determine the highest numeric ID used in text-based references
        # This ensures we don't duplicate numeric IDs when assigning to inline links
        used_numeric_ids = set()
        for ref_id in text_ref_to_url.keys():
            # Check if ref_id is a numeric string (like "1", "2", etc.)
            try:
                num_id = int(ref_id)
                used_numeric_ids.add(num_id)
            except ValueError:
                # Not a numeric ID, ignore
                pass

        # Find the next available numeric ID (must be higher than any existing numeric ID)
        if used_numeric_ids:
            next_ref = max(used_numeric_ids) + 1

        # Second pass: assign numeric references to inline links (skipping used numbers)
        for link_item in link_data:
            line_idx, start, end, link_text, url, title, link_type, ref_id = link_item
            
            if link_type == 'inline':
                # Only inline links get numeric references
                if url:  # Only if we have a URL
                    url_key = (url, title)
                    if url_key not in url_to_ref:
                        # Make sure we don't use a number that's already taken
                        while next_ref in used_numeric_ids:
                            next_ref += 1
                        url_to_ref[url_key] = next_ref
                        used_numeric_ids.add(next_ref)
                        next_ref += 1

        # Replace links (process in reverse to maintain positions)
        # Group links by line and sort by position (right to left for replacement)
        links_by_line = {}
        seen_links = set()  # Track (line_idx, start, end) to avoid duplicates
        for link_item in link_data:
            line_idx, start, end, link_text, url, title, link_type, ref_id = link_item
            link_key = (line_idx, start, end)
            if link_key in seen_links:
                continue  # Skip duplicate links
            seen_links.add(link_key)

            if line_idx not in links_by_line:
                links_by_line[line_idx] = []
            links_by_line[line_idx].append((start, end, link_text, url, title, link_type, ref_id))

        for line_idx in sorted(links_by_line.keys(), reverse=True):
            line = lines[line_idx]
            # Sort by start position, descending (right to left)
            line_links = sorted(links_by_line[line_idx], key=lambda x: x[0], reverse=True)

            # Build new line by replacing from right to left
            # This ensures positions don't shift as we replace
            replaced_ranges = set()  # Track (start, end) ranges we've replaced
            new_line = line
            for link_item in line_links:
                start, end, link_text, url, title, link_type, ref_id = link_item
                # Skip if we've already replaced this exact range (avoid duplicates)
                range_key = (start, end)
                if range_key in replaced_ranges:
                    continue
                replaced_ranges.add(range_key)

                if link_type == 'reference' and ref_id:
                    # Preserve existing reference link
                    replacement = f'[{link_text}][{ref_id}]'
                elif link_type == 'implicit' and ref_id:
                    # Preserve implicit reference link
                    replacement = f'[{link_text}]'
                elif link_type == 'inline' and url:
                    # Convert inline link to numeric reference
                    url_key = (url, title)
                    ref_num = url_to_ref[url_key]
                    replacement = f'[{link_text}][{ref_num}]'
                else:
                    # Skip links without valid data
                    continue
                    
                # Replace from right to left to maintain positions
                new_line = new_line[:start] + replacement + new_line[end:]

            # Verify that if the original line was a list item, the new line is still a list item
            # This ensures we don't break list structure during link conversion
            if is_list_item(line):
                # Extract the list item structure from the original line
                orig_match = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', line)
                if orig_match:
                    orig_indent = orig_match.group(1)
                    orig_marker = orig_match.group(2)
                    orig_marker_space = orig_match.group(3)
                    orig_content = orig_match.group(4)

                    # Check if the new line is still a valid list item
                    new_match = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', new_line)
                    if not new_match:
                        # The replacement completely broke the list structure - reconstruct it
                        # The new_line should have the same content but with links replaced
                        # We need to extract just the content (without marker/indent) from new_line
                        # Try to find where the original content started
                        marker_end_pos = len(orig_indent) + len(orig_marker) + len(orig_marker_space)

                        # If new_line is shorter than marker_end_pos, it means the marker is missing
                        # In that case, new_line should just be the content
                        if len(new_line) < marker_end_pos or not new_line[marker_end_pos:].lstrip():
                            # Marker is missing - new_line is likely just the content
                            new_content = new_line.lstrip()
                            # Remove any marker that might be at the start
                            new_content = re.sub(r'^[-*+]|\d+\.\s*', '', new_content).lstrip()
                        else:
                            # Marker might still be there, extract content after it
                            new_content = new_line[marker_end_pos:].lstrip()
                            # If there's still a marker in the content, remove it
                            new_content = re.sub(r'^[-*+]|\d+\.\s*', '', new_content).lstrip()

                        # Reconstruct the line with original structure
                        new_line = orig_indent + orig_marker + orig_marker_space + new_content
                        # Preserve newline if original had one
                        if line.endswith('\n') and not new_line.endswith('\n'):
                            new_line += '\n'
                    elif new_match.group(2) != orig_marker:
                        # Marker changed - restore original marker
                        new_content = new_match.group(4)
                        new_line = orig_indent + orig_marker + orig_marker_space + new_content
                        if line.endswith('\n') and not new_line.endswith('\n'):
                            new_line += '\n'
                    else:
                        # New line is still a valid list item, but verify indentation
                        new_indent = new_match.group(1)
                        if orig_indent != new_indent:
                            # Restore original indentation
                            new_content = new_match.group(4)
                            new_line = orig_indent + orig_marker + orig_marker_space + new_content
                            if line.endswith('\n') and not new_line.endswith('\n'):
                                new_line += '\n'

            lines[line_idx] = new_line

        # Add reference definitions
        # Organize: text-based refs first (in document order), then numbered refs
        if place_at_beginning:
            # Place all definitions at the beginning
            # Remove any leading blank lines and front matter
            insert_pos = 0
            # Skip YAML front matter if present
            if lines and lines[0].strip() == '---':
                # Find end of front matter
                for i in range(1, len(lines)):
                    if lines[i].strip() == '---':
                        insert_pos = i + 1
                        break

            # Ensure blank line after front matter or at start
            if insert_pos < len(lines) and lines[insert_pos].strip():
                lines.insert(insert_pos, '\n')
                insert_pos += 1

            # Add text-based reference definitions first (in document order)
            for ref_id in text_ref_order:
                url, title = text_ref_to_url[ref_id]
                if title:
                    lines.insert(insert_pos, f'[{ref_id}]: {url} "{title}"\n')
                else:
                    lines.insert(insert_pos, f'[{ref_id}]: {url}\n')
                insert_pos += 1

            # Add numeric reference definitions next (in order)
            if url_to_ref:
                for (url, title), ref_num in sorted(url_to_ref.items(), key=lambda x: x[1]):
                    if title:
                        lines.insert(insert_pos, f'[{ref_num}]: {url} "{title}"\n')
                    else:
                        lines.insert(insert_pos, f'[{ref_num}]: {url}\n')
                    insert_pos += 1

            # Add blank line after definitions
            if (text_ref_to_url or url_to_ref) and insert_pos < len(lines) and lines[insert_pos].strip():
                lines.insert(insert_pos, '\n')
        else:
            # Place all definitions at bottom (default behavior)
            while lines and not lines[-1].strip():
                lines.pop()

            if text_ref_to_url or url_to_ref:
                lines.append('\n')
                
            # Add text-based reference definitions first (in document order)
            for ref_id in text_ref_order:
                url, title = text_ref_to_url[ref_id]
                if title:
                    lines.append(f'[{ref_id}]: {url} "{title}"\n')
                else:
                    lines.append(f'[{ref_id}]: {url}\n')

            # Add numeric reference definitions next (in order)
            if url_to_ref:
                for (url, title), ref_num in sorted(url_to_ref.items(), key=lambda x: x[1]):
                    if title:
                        lines.append(f'[{ref_num}]: {url} "{title}"\n')
                    else:
                        lines.append(f'[{ref_num}]: {url}\n')

    return lines

def process_file(filepath, wrap_width, overwrite=False, skip_rules=None, skip_string=None, reverse_emphasis=False):
    """Process a single markdown file

    Args:
        filepath: Path to the markdown file
        wrap_width: Width to wrap text at
        overwrite: If True, overwrite the file. If False, output to STDOUT.
        skip_rules: Set of rule numbers to skip
        skip_string: Original skip string (for checking sub-keywords like em-dash, guillemet)
        reverse_emphasis: If True, reverse emphasis markers (__ → ** for bold, * → _ for italic)

    Returns:
        True if changes were made, False otherwise
    """
    if skip_rules is None:
        skip_rules = set()

    # Check for sub-keywords in skip_string
    skip_em_dash = skip_string and 'em-dash' in skip_string
    skip_guillemet = skip_string and 'guillemet' in skip_string
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False

    output = []
    in_code_block = False
    in_math_block = False  # Track if we're inside a display math block ($$...$$)
    i = 0
    changes_made = False
    consecutive_blank_lines = 0
    current_list_indent_unit = None  # Cache the indent unit for the current list block
    list_context_stack = []  # Track list nesting: [(level, type, number), ...]

    while i < len(lines):
        line = lines[i]
        original_line = line

        # Normalize line endings to Unix (\n)
        if 1 not in skip_rules:
            if line.endswith('\r\n'):
                line = line[:-2] + '\n'
                changes_made = True
            elif line.endswith('\r'):
                line = line[:-1] + '\n'
                changes_made = True
            elif not line.endswith('\n'):
                line = line + '\n'
                changes_made = True

        stripped = line.strip()

        # Track code block state
        if is_code_block(line):
            # Normalize fenced code block language identifier spacing
            if 17 not in skip_rules:
                normalized_code = normalize_fenced_code_lang(line)
                if normalized_code != line:
                    line = normalized_code
                    changes_made = True

            # Determine if this is the opening or closing fence before toggling
            is_opening = not in_code_block
            in_code_block = not in_code_block

            # Ensure blank line before code block (unless at start)
            if 6 not in skip_rules and is_opening:
                if output and output[-1].strip():
                    last = output[-1].strip()
                    if not last.startswith('```'):
                        output.append('\n')
                        changes_made = True

            # If this is the closing fence, remove trailing blank lines inside the code block
            if not is_opening:
                while output and not output[-1].strip():
                    # Do not remove the opening fence if the block was empty
                    if output[-1].strip().startswith('```'):
                        break
                    output.pop()
                    changes_made = True

            output.append(line)

            # Ensure blank line after code block
            if 7 not in skip_rules:
                if not in_code_block and i + 1 < len(lines) and lines[i + 1].strip():
                    output.append('\n')
                    changes_made = True
            i += 1
            continue

        # Don't process inside code blocks
        if in_code_block:
            output.append(line)
            consecutive_blank_lines = 0
            i += 1
            continue

        # Normalize emoji names (spellcheck and correct)
        if 23 not in skip_rules:
            if not in_math_block:
                normalized_emoji = normalize_emoji_names(line)
                if normalized_emoji != line:
                    line = normalized_emoji
                    changes_made = True

        # Normalize typography (curly quotes, dashes, ellipses, guillemets)
        if 24 not in skip_rules:
            normalized_typography = normalize_typography(line, skip_em_dash=skip_em_dash, skip_guillemet=skip_guillemet)
            if normalized_typography != line:
                line = normalized_typography
                changes_made = True

        # Normalize bold/italic markers
        if 25 not in skip_rules:
            normalized_bold_italic = normalize_bold_italic(line, reverse_emphasis=reverse_emphasis)
            if normalized_bold_italic != line:
                line = normalized_bold_italic
                changes_made = True

        # Normalize IAL spacing (before other processing)
        if 16 not in skip_rules:
            normalized_ial = normalize_ial_spacing(line)
            if normalized_ial != line:
                line = normalized_ial
                changes_made = True

        # Normalize reference-style link definitions
        if 18 not in skip_rules:
            normalized_ref = normalize_reference_link(line)
            if normalized_ref != line:
                line = normalized_ref
                changes_made = True

        # Handle display math blocks ($$...$$) - track state for multi-line
        if 21 not in skip_rules:
            stripped_line = line.strip()
            if stripped_line == '$$':
                # Toggle math block state
                is_opening = not in_math_block
                in_math_block = not in_math_block

                if is_opening:
                    # Ensure blank line before opening $$ (unless at start)
                    if output and output[-1].strip():
                        output.append('\n')
                        changes_made = True

                    # Opening $$ - no space after
                    output.append('$$')
                    # Check if next line has leading space and remove it
                    if i + 1 < len(lines) and lines[i + 1].strip() and lines[i + 1][0] == ' ':
                        # Next line starts with space - we'll handle it when we process that line
                        pass
                    output.append('\n')
                else:
                    # Closing $$ - remove trailing space from previous line, no space before
                    if output and output[-1].rstrip().endswith(' '):
                        # Remove trailing space from previous line
                        output[-1] = output[-1].rstrip() + '\n'
                        changes_made = True
                    output.append('$$\n')

                    # Ensure blank line after math block if next line is non-empty
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        output.append('\n')
                        changes_made = True

                i += 1
                continue
            elif in_math_block:
                # Inside math block - check if this is first or last line
                # First line: previous output line was opening $$
                is_first_line = (output and output[-1].rstrip() == '$$')
                # Last line: next input line is closing $$
                is_last_line = (i + 1 < len(lines) and lines[i+1].strip() == '$$')

                if is_first_line:
                    # First line: remove leading whitespace only
                    normalized = line.lstrip()
                    if not normalized.endswith('\n'):
                        normalized += '\n'
                    output.append(normalized)
                    if line != normalized:
                        changes_made = True
                elif is_last_line:
                    # Last line: remove trailing whitespace only
                    normalized = line.rstrip()
                    if not normalized.endswith('\n'):
                        normalized += '\n'
                    output.append(normalized)
                    if line != normalized:
                        changes_made = True
                else:
                    # Middle line: keep as is
                    output.append(line)
                i += 1
                continue
            else:
                # Normalize inline math and single-line display math
                normalized_math = normalize_math_spacing(line, is_in_code_block=in_code_block)
                if normalized_math != line:
                    line = normalized_math
                    changes_made = True

        # Handle table normalization (before other processing that might affect table structure)
        if 22 not in skip_rules:
            # Detect if we're at the start of a table block
            # A table block starts with a line containing pipes (table row or separator)
            if '|' in stripped and not is_code_block(line) and not in_math_block:
                # Collect all consecutive table lines
                table_lines = []
                table_start = i
                j = i

                # Collect lines until we hit a non-table line or blank line
                while j < len(lines):
                    current_line = lines[j]
                    current_stripped = current_line.strip()

                    # Stop if blank line (tables are separated by blank lines)
                    if not current_stripped:
                        break

                    # Stop if code block delimiter
                    if is_code_block(current_line):
                        break

                    # Continue if it's a table-related line (has pipes)
                    if '|' in current_stripped:
                        table_lines.append(current_line)
                        j += 1
                    else:
                        # Not a table line, but might be part of table if it's just whitespace
                        # Actually, blank lines break tables, so stop here
                        break

                # If we collected at least 2 lines, try to normalize
                if len(table_lines) >= 2:
                    normalized_table = normalize_table_formatting(table_lines)
                    if normalized_table:
                        # Replace original table lines with normalized ones
                        for k, norm_line in enumerate(normalized_table):
                            if table_start + k < len(lines):
                                if lines[table_start + k] != norm_line:
                                    changes_made = True
                        # Output normalized table
                        output.extend(normalized_table)
                        # Skip to after the table
                        i = j
                        consecutive_blank_lines = 0
                        continue

        # Handle headlines (headers)
        if is_headline(line):
            # Clear list context when encountering a headline (non-list element)
            list_context_stack = []
            current_list_indent_unit = None

            # Normalize headline spacing (exactly 1 space after #)
            if 4 not in skip_rules:
                normalized = normalize_headline_spacing(line)
                if normalized != line:
                    line = normalized
                    changes_made = True

            output.append(line)
            # Ensure blank line after headline (unless at end or next line is also headline)
            if 5 not in skip_rules:
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip() and not is_headline(next_line) and not is_code_block(next_line):
                        # Check if there's already a blank line
                        if next_line.strip():
                            output.append('\n')
                            changes_made = True
            consecutive_blank_lines = 0
            i += 1
            continue

        # Handle horizontal rules
        if is_horizontal_rule(line):
            # Clear list context when encountering a horizontal rule (non-list element)
            list_context_stack = []
            current_list_indent_unit = None

            # Ensure blank line before horizontal rule
            if 10 not in skip_rules:
                if output and output[-1].strip():
                    output.append('\n')
                    changes_made = True
            output.append(line)
            # Ensure blank line after horizontal rule
            if 11 not in skip_rules:
                if i + 1 < len(lines) and lines[i + 1].strip():
                    output.append('\n')
                    changes_made = True
            consecutive_blank_lines = 0
            i += 1
            continue

        # Don't wrap certain lines
        if should_preserve_line(line):
            output.append(line)
            i += 1
            continue

        # Handle list items
        if is_list_item(line):
            # Normalize task list checkbox (lowercase x)
            if 19 not in skip_rules:
                normalized_task = normalize_task_checkbox(line)
                if normalized_task != line:
                    line = normalized_task
                    changes_made = True

            # Detect the base indentation unit for this list (2 or 4 spaces)
            # Only detect if we don't have a cached value, or if this is the start of a new list
            if current_list_indent_unit is None:
                # Look ahead to find the first indented list item to determine the unit
                current_list_indent_unit = detect_list_indent_unit(lines, i)

            # Check for CommonMark interrupted list: bullet <-> numbered at same level
            # Do this BEFORE normalization so we can detect the original marker types
            list_indent_before = get_list_indent(line)
            match_current_orig = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', line)
            interruption_detected = False
            if match_current_orig and output:
                current_marker_orig = match_current_orig.group(2)
                current_is_numbered_orig = bool(re.match(r'^\d+\.', current_marker_orig))

                # Check previous output line (skip blank lines)
                prev_line = None
                for j in range(len(output) - 1, -1, -1):
                    if output[j].strip():
                        prev_line = output[j]
                        break

                if prev_line and is_list_item(prev_line):
                    prev_indent = get_list_indent(prev_line)
                    match_prev = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', prev_line)
                    if match_prev:
                        prev_marker = match_prev.group(2)
                        prev_is_numbered = bool(re.match(r'^\d+\.', prev_marker))

                        # If same level and marker type changed (bullet <-> numbered): split the list
                        # BUT only at top-level (level 0) - nested lists should just convert markers
                        if (prev_indent == list_indent_before and
                            prev_is_numbered != current_is_numbered_orig):
                            if current_list_indent_unit is None:
                                current_list_indent_unit = detect_list_indent_unit(lines, i)
                            interrupt_level = get_list_level(match_current_orig.group(1), current_list_indent_unit)
                            # Only interrupt at top-level (level 0)
                            if interrupt_level == 0:
                                interruption_detected = True
                                # Remove context for this level so the new list type starts fresh
                                list_context_stack = [ctx for ctx in list_context_stack if ctx[0] != interrupt_level]
                                # Insert: blank line, HTML comment, blank line
                                output.append('\n')
                                output.append('<!-- -->\n')
                                output.append('\n')
                                changes_made = True

            # Normalize list markers (renumber ordered lists, standardize bullet markers)
            # Do this before converting spaces to tabs so level calculation works correctly
            if 26 not in skip_rules:
                if current_list_indent_unit is None:
                    current_list_indent_unit = detect_list_indent_unit(lines, i)
                skip_list_reset = skip_rules and 27 in skip_rules
                normalized_line, list_context_stack, marker_changed = normalize_list_markers(
                    line, list_context_stack, current_list_indent_unit, skip_list_reset
                )
                # Always use normalized_line if it's different, even if marker didn't change
                # This ensures the line structure is consistent
                if normalized_line != line:
                    # Verify normalized line is still a valid list item
                    if is_list_item(normalized_line):
                        line = normalized_line
                        changes_made = True
                    # If normalization broke it, keep original

            # Convert list indentation spaces to tabs based on detected unit
            if 12 not in skip_rules:
                if current_list_indent_unit is None:
                    # Detect indent unit if not already detected
                    current_list_indent_unit = detect_list_indent_unit(lines, i)
                line_before_tabs = line  # Store line before tab conversion for comparison
                converted_line = spaces_to_tabs_for_list(line, current_list_indent_unit)
                # Only use converted line if it's still a valid list item
                if is_list_item(converted_line):
                    line = converted_line
                    if line != line_before_tabs:
                        changes_made = True
                # If conversion broke the line, keep the original

            list_indent = get_list_indent(line)

            # Ensure blank line before list (unless nested or after another list)
            if 8 not in skip_rules:
                if output and output[-1].strip():
                    prev_line = output[-1]
                    # Don't add blank line if previous line is also a list item
                    if not is_list_item(prev_line):
                        prev_stripped = prev_line.strip()
                        if not prev_stripped.startswith('>') and not prev_stripped.startswith('#'):
                            output.append('\n')
                            changes_made = True
                    else:
                        # Previous line is a list item - check if this is nested
                        prev_indent = get_list_indent(prev_line)
                        # If this item has more indentation than previous, it's nested - no blank line needed
                        if list_indent <= prev_indent:
                            # Same or less indentation - might need blank line, but only if not continuing list
                            pass  # Let it continue without blank line

            # Process list item content
            # Match with or without space after marker
            # Note: line should always match since we're inside the is_list_item block
            match = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', line)
            if not match:
                # Line should match - if it doesn't, something went wrong in processing
                # Try to recover by checking if it's still a list item
                if is_list_item(line):
                    # Still a list item but regex doesn't match - try to fix it
                    # Extract what we can from the line
                    stripped = line.lstrip()
                    # Try to find the marker
                    marker_match = re.match(r'^([-*+]|\d+\.)', stripped)
                    if marker_match:
                        marker = marker_match.group(1)
                        # Find where content starts (after marker and optional space)
                        content_start = len(marker_match.group(0))
                        if content_start < len(stripped) and stripped[content_start] == ' ':
                            content_start += 1
                        content = stripped[content_start:] if content_start < len(stripped) else ''
                        # Reconstruct with proper structure
                        indent = line[:len(line) - len(stripped)]
                        marker_space = ' '
                        line = indent + marker + marker_space + content
                        if not line.endswith('\n') and original_line.endswith('\n'):
                            line += '\n'
                        # Try the match again
                        match = re.match(r'^(\s*)([-*+]|\d+\.)(\s*)(.*)$', line)
                        if not match:
                            # Still doesn't match - append as-is to avoid data loss
                            output.append(line)
                    else:
                        # Can't find marker - append as-is to avoid data loss
                        output.append(line)
                else:
                    # No longer a list item - this shouldn't happen, but append anyway
                    output.append(line)
            else:
                indent = match.group(1)
                marker = match.group(2)
                marker_space = match.group(3)
                content = match.group(4)
                # Normalize: ensure exactly one space after marker
                if 13 not in skip_rules:
                    if marker_space != ' ':
                        marker_space = ' '
                        line = indent + marker + marker_space + content + ('\n' if line.endswith('\n') else '')
                        changes_made = True
                prefix = indent + marker + marker_space

                # Wrap content if needed
                if 14 not in skip_rules:
                    if len(line.rstrip()) > wrap_width and content:
                        wrapped = wrap_text(content, wrap_width, prefix)
                        for j, wrapped_line in enumerate(wrapped):
                            if j == 0:
                                # First line already has prefix from wrap_text
                                output.append(wrapped_line + '\n')
                            else:
                                # Continuation lines need extra indentation to match prefix
                                # Calculate continuation indent: same as prefix but as spaces
                                cont_indent = ' ' * len(prefix)
                                # Remove prefix from wrapped_line (it was added by wrap_text)
                                if wrapped_line.startswith(prefix):
                                    content_part = wrapped_line[len(prefix):].lstrip()
                                else:
                                    content_part = wrapped_line
                                # Add continuation indent and content
                                output.append(cont_indent + content_part + '\n')
                        changes_made = True
                    else:
                        output.append(line)
                else:
                    output.append(line)

            # Ensure blank line after list (unless next line is also a list or nested)
            if 9 not in skip_rules:
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip() and not is_list_item(next_line):
                        # Next line is not a list item - reset indent unit cache and list context for next list
                        current_list_indent_unit = None
                        list_context_stack = []
                        next_indent = get_list_indent(next_line) if next_line.strip() else 0
                        if next_indent <= list_indent and not next_line.strip().startswith('>'):
                            # Check if we need a blank line
                            if not (i + 2 < len(lines) and is_list_item(lines[i + 2])):
                                # Only add if next non-empty line isn't a list continuation
                                pass  # We'll handle this in the next iteration
                    elif not next_line.strip():
                        # Blank line - might be end of list, but don't reset yet
                        pass
                else:
                    # End of file - reset for next list
                    current_list_indent_unit = None
                    list_context_stack = []
            else:
                # Reset cache when list ends
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip() and not is_list_item(next_line):
                        current_list_indent_unit = None
                        list_context_stack = []
                    else:
                        current_list_indent_unit = None
                        list_context_stack = []
            i += 1
            continue

        # Handle blockquotes
        if is_blockquote(line):
            # Clear list context when encountering a blockquote (non-list element)
            list_context_stack = []
            current_list_indent_unit = None

            # Normalize blockquote spacing
            if 20 not in skip_rules:
                normalized_bq = normalize_blockquote_spacing(line)
                if normalized_bq != line:
                    line = normalized_bq
                    changes_made = True

            prefix = get_blockquote_prefix(line)
            content = line[len(prefix):].lstrip()

            if 14 not in skip_rules:
                if content and len(line.rstrip()) > wrap_width:
                    wrapped = wrap_text(content, wrap_width, prefix + ' ')
                    for j, wrapped_line in enumerate(wrapped):
                        if j > 0:
                            wrapped_line = prefix + ' ' + wrapped_line[len(prefix) + 1:]
                        output.append(wrapped_line + '\n')
                    changes_made = True
                else:
                    output.append(line)
            else:
                output.append(line)
            i += 1
            continue

        # Regular paragraph text
        if stripped:
            # Clear list context when encountering paragraph text (non-list element)
            # But only if this is not indented (which would be part of a list item)
            line_indent = len(line) - len(line.lstrip())
            if line_indent == 0 or not is_list_item(line):
                list_context_stack = []
                current_list_indent_unit = None

            # Ensure blank line before paragraph if previous was code block or list
            if output and output[-1].strip():
                prev = output[-1].strip()
                if prev.startswith('```') or is_list_item(output[-1]):
                    output.append('\n')
                    changes_made = True

            # Normalize trailing whitespace (preserve exactly 2 spaces)
            if 2 not in skip_rules:
                normalized = normalize_trailing_whitespace(line)
                if normalized != line:
                    line = normalized
                    changes_made = True

            # Wrap if needed
            if 14 not in skip_rules:
                if len(line.rstrip()) > wrap_width:
                    wrapped = wrap_text(stripped, wrap_width)
                    for wrapped_line in wrapped:
                        output.append(wrapped_line + '\n')
                    changes_made = True
                else:
                    output.append(line)
            else:
                output.append(line)
            consecutive_blank_lines = 0
        else:
            # Handle blank lines - collapse multiple (max 1 consecutive, except in code blocks)
            if 3 not in skip_rules:
                consecutive_blank_lines += 1
                if consecutive_blank_lines <= 1:
                    output.append('\n')
                # If more than 1, skip it (collapse)
                else:
                    changes_made = True
            else:
                # Don't collapse, just output all blank lines
                output.append('\n')
                consecutive_blank_lines = 0

        i += 1

    # Process link conversions (rules 28, 29, 30)
    # Rule 30 (inline-links) is disabled by default and overrides rule 28 if enabled
    # Rule 28 (reference-links) is enabled by default
    # Rule 29 (links-at-end) is enabled by default - puts links at end
    # If rule 29 is skipped AND rule 28 is enabled, put links at beginning
    # If rule 29 is included, rule 28 is included by default
    # If rule 30 is included, both rule 28 and 29 are skipped
    if skip_rules is None:
        skip_rules = set()

    # If inline-links is enabled, skip reference-links and links-at-end
    use_inline = 30 not in skip_rules
    if use_inline:
        skip_rules.add(28)
        skip_rules.add(29)

    # If links-at-end is included, reference-links is included by default
    if 29 not in skip_rules:
        skip_rules.discard(28)  # Enable reference-links if links-at-end is enabled

    use_reference = 28 not in skip_rules and not use_inline
    # place_at_beginning = True if links-at-end is skipped AND reference-links is enabled
    place_at_beginning = (29 in skip_rules) and use_reference

    if use_inline or use_reference:
        output = convert_links_in_document(output, use_inline, use_reference, place_at_beginning)
        changes_made = True

    # Ensure exactly one blank line at end of file
    if 15 not in skip_rules:
        # Remove trailing blank lines
        while output and output[-1].strip() == '':
            output.pop()
            changes_made = True
        # Add exactly one blank line at end
        if output and output[-1].strip():
            output.append('\n')
            changes_made = True

    # Write output
    if overwrite:
        # Write back to file if changes were made
        if changes_made:
            try:
                with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                    f.writelines(output)
                return True
            except Exception as e:
                print(f"Error writing {filepath}: {e}", file=sys.stderr)
                return False
        return False
    else:
        # Output to STDOUT
        sys.stdout.writelines(output)
        return changes_made

def get_config_path():
    """Get the config directory and file path

    Returns:
        tuple of (config_dir Path, config_file Path or None)
    """
    # Determine config directory
    config_dir = os.environ.get('XDG_CONFIG_HOME')
    if not config_dir:
        config_dir = os.path.expanduser('~/.config')
    config_dir = Path(config_dir) / 'md-fixup'

    # Try config.yml first, then config.yaml
    config_file = None
    for filename in ['config.yml', 'config.yaml']:
        candidate = config_dir / filename
        if candidate.exists():
            config_file = candidate
            break

    return config_dir, config_file

def init_config_file(force=False, local=False):
    """Initialize the config file with all rules enabled by name

    Args:
        force: If True, create config even if it exists
        local: If True, create .md-fixup in current directory instead of global config

    Returns:
        Path to created config file, or None if not created
    """
    if yaml is None:
        return None

    if local:
        # Local config: .md-fixup in current directory
        config_file = Path('.md-fixup')
        if config_file.exists() and not force:
            return None
    else:
        # Global config: ~/.config/md-fixup/config.yml
        config_dir, config_file = get_config_path()
        if config_file and not force:
            return None
        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / 'config.yml'

    # Generate config with all rules enabled
    all_rules = sorted([desc[1] for desc in LINTING_RULES.values()])

    config_content = {
        'width': DEFAULT_WRAP_WIDTH,
        'overwrite': False,
        'rules': {
            'skip': 'all',
            'include': all_rules
        }
    }

    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_content, f, default_flow_style=False, sort_keys=False)
        return config_file
    except Exception:
        return None

def _parse_config_rules(config):
    """Parse rules section from config dict

    Returns:
        set of rule numbers to skip
    """
    result = set()
    if 'rules' in config and isinstance(config['rules'], dict):
        rules_config = config['rules']

        # Handle skip: all + include: [...] pattern
        if rules_config.get('skip') == 'all':
            # Start with all rules disabled
            all_rule_nums = set(LINTING_RULES.keys())
            result = all_rule_nums.copy()

            # Then include the specified rules
            if 'include' in rules_config:
                include_list = rules_config['include']
                if not isinstance(include_list, list):
                    include_list = [include_list]

                for item in include_list:
                    # Handle group keywords
                    if item == 'code-block-newlines':
                        result.discard(6)
                        result.discard(7)
                    elif item == 'display-math-newlines':
                        result.discard(21)
                    elif item in KEYWORD_TO_RULE:
                        result.discard(KEYWORD_TO_RULE[item])
                    elif item.isdigit() and int(item) in LINTING_RULES:
                        result.discard(int(item))

        # Handle simple skip: [...] pattern
        elif 'skip' in rules_config:
            skip_list = rules_config['skip']
            if not isinstance(skip_list, list):
                skip_list = [skip_list]

            for item in skip_list:
                # Handle group keywords
                if item == 'code-block-newlines':
                    result.update({6, 7})
                elif item == 'display-math-newlines':
                    result.add(21)
                elif item in KEYWORD_TO_RULE:
                    result.add(KEYWORD_TO_RULE[item])
                elif item.isdigit() and int(item) in LINTING_RULES:
                    result.add(int(item))

        # Handle include: [...] pattern (without skip: all)
        if 'include' in rules_config and rules_config.get('skip') != 'all':
            include_list = rules_config['include']
            if not isinstance(include_list, list):
                include_list = [include_list]

            for item in include_list:
                # Handle group keywords
                if item == 'code-block-newlines':
                    result.discard(6)
                    result.discard(7)
                elif item == 'display-math-newlines':
                    result.discard(21)
                elif item in KEYWORD_TO_RULE:
                    result.discard(KEYWORD_TO_RULE[item])
                elif item.isdigit() and int(item) in LINTING_RULES:
                    result.discard(int(item))

    return result

def load_config():
    """Load configuration from .md-fixup (local) or XDG_CONFIG_HOME/md-fixup/config.yml (global)

    Returns:
        dict with keys: width, overwrite, skip_rules (set of rule numbers)
        Returns None if config file doesn't exist or YAML is not available
        Local config (.md-fixup) takes precedence over global config
    """
    if yaml is None:
        return None

    # Check for local config first (.md-fixup in current directory)
    local_config = Path('.md-fixup')
    if local_config.exists():
        try:
            with open(local_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            if config:
                return {
                    'width': config.get('width'),
                    'overwrite': config.get('overwrite'),
                    'skip_rules': _parse_config_rules(config),
                }
        except Exception:
            pass  # Fall through to global config

    # Fall back to global config
    config_dir, config_file = get_config_path()

    if not config_file:
        return None

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config:
            return None

        return {
            'width': config.get('width'),
            'overwrite': config.get('overwrite'),
            'skip_rules': _parse_config_rules(config),
        }
    except Exception as e:
        # Silently ignore config file errors
        return None

def main():
    """Main entry point"""
    rules_list = '\n'.join(f'  {num}. {desc[0]} ({desc[1]})' for num, desc in sorted(LINTING_RULES.items()))
    parser = argparse.ArgumentParser(
        description='Markdown linter that wraps text and ensures proper formatting',
        prog='md-fixup',
        epilog=f'''
Available linting rules (use with --skip):
{rules_list}

Sub-keywords (for specific rule features):
  - em-dash: Skip em dash conversion (use with typography rule)
  - guillemet: Skip guillemet conversion (use with typography rule)

Examples:
  %(prog)s file.md
  %(prog)s --width 80 file1.md file2.md
  %(prog)s --width 72 *.md
  find . -name "*.md" | %(prog)s --width 100
  %(prog)s  # Processes all .md files in current directory
  %(prog)s --skip 2,3 file.md  # Skip trailing whitespace and blank line collapse
  %(prog)s --skip wrap,end-newline file.md  # Skip wrapping and end newline (using keywords)
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'md-fixup v{VERSION}'
    )
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=None,
        metavar='X',
        help=f'Text wrap width in characters (default: {DEFAULT_WRAP_WIDTH}, or from config file)'
    )
    parser.add_argument(
        '-o', '--overwrite',
        action='store_true',
        help='Overwrite files in place. If not specified, output to STDOUT (or use config file setting).'
    )
    parser.add_argument(
        '-s', '--skip',
        type=str,
        metavar='X[,X]',
        help='Comma-separated list of rule numbers or keywords to skip (e.g., --skip 2,3 or --skip wrap,end-newline). See available rules below.'
    )
    parser.add_argument(
        '--init-config',
        action='store_true',
        help='Initialize the global config file with all rules enabled by name (creates ~/.config/md-fixup/config.yml)'
    )
    parser.add_argument(
        '--init-config-local',
        action='store_true',
        help='Initialize a local config file with all rules enabled by name (creates .md-fixup in current directory)'
    )
    parser.add_argument(
        '--reverse-emphasis',
        action='store_true',
        help='Reverse emphasis markers: use ** for bold and _ for italic (instead of __ for bold and * for italic)'
    )
    parser.add_argument(
        'files',
        nargs='*',
        metavar='FILE',
        help='Markdown files to process. If not provided, reads from STDIN (one file path per line). If STDIN is empty, processes all .md files in current directory.'
    )

    args = parser.parse_args()

    # Handle --init-config flag
    if args.init_config:
        # Check if a config file already exists
        config_dir, existing_config = get_config_path()
        if existing_config:
            if not sys.stdin.isatty():
                print(f"Config file already exists at: {existing_config}", file=sys.stderr)
                print("Refusing to overwrite config in non-interactive mode.", file=sys.stderr)
                sys.exit(1)
            print(f"Config file already exists at: {existing_config}", file=sys.stderr)
            response = input("Overwrite existing config file? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print("Aborted. Existing config file left unchanged.", file=sys.stderr)
                sys.exit(1)
        config_file = init_config_file(force=True, local=False)
        if config_file:
            print(f"Created config file at: {config_file}", file=sys.stderr)
            print("Edit this file to customize which rules are enabled.", file=sys.stderr)
            sys.exit(0)
        else:
            print("Error: Could not create config file. Is PyYAML installed?", file=sys.stderr)
            sys.exit(1)

    # Handle --init-config-local flag
    if args.init_config_local:
        # Check if .md-fixup already exists
        local_config = Path('.md-fixup')
        if local_config.exists():
            if not sys.stdin.isatty():
                print(f"Config file already exists at: {local_config.absolute()}", file=sys.stderr)
                print("Refusing to overwrite config in non-interactive mode.", file=sys.stderr)
                sys.exit(1)
            print(f"Config file already exists at: {local_config.absolute()}", file=sys.stderr)
            response = input("Overwrite existing config file? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print("Aborted. Existing config file left unchanged.", file=sys.stderr)
                sys.exit(1)
        config_file = init_config_file(force=True, local=True)
        if config_file:
            print(f"Created local config file at: {config_file.absolute()}", file=sys.stderr)
            print("Edit this file to customize which rules are enabled.", file=sys.stderr)
            sys.exit(0)
        else:
            print("Error: Could not create config file. Is PyYAML installed?", file=sys.stderr)
            sys.exit(1)

    # Auto-init config if it doesn't exist and running interactively
    config_dir, config_file = get_config_path()
    if not config_file and sys.stdout.isatty():
        config_file = init_config_file(force=False)
        if config_file:
            print(f"Created initial config file at: {config_file}", file=sys.stderr)
            print("Edit this file to customize which rules are enabled.", file=sys.stderr)

    # Load config file (if available)
    config = load_config()

    # Merge config with CLI args (CLI overrides config)
    wrap_width = args.width if args.width is not None else (config['width'] if config and config.get('width') is not None else DEFAULT_WRAP_WIDTH)
    # For overwrite: CLI flag always wins if present, otherwise use config, otherwise False
    overwrite = args.overwrite if args.overwrite else (config['overwrite'] if config and config.get('overwrite') is not None else False)
    files = args.files

    # Start with config skip_rules, then merge CLI skip rules
    # Rule 30 (inline-links) is disabled by default unless explicitly enabled
    skip_rules = config['skip_rules'].copy() if config and config.get('skip_rules') else set()
    # If no config or rule 30 not explicitly enabled, disable it by default
    if not config or 30 not in (config.get('skip_rules') or set()):
        # Check if rule 30 is in the include list (if using skip: all pattern)
        if config and config.get('rules', {}).get('skip') == 'all':
            include_list = config.get('rules', {}).get('include', [])
            if 'inline-links' not in include_list and 30 not in include_list:
                skip_rules.add(30)  # Disable inline-links by default
        elif not config:
            # No config file - disable inline-links by default
            skip_rules.add(30)

    # Parse skip rules from CLI (accepts both numbers and keywords)
    # Also supports sub-keywords: em-dash, guillemet (for typography rule)
    # Note: skip_rules already contains config values, don't reset it
    if args.skip:
        skip_values = [x.strip() for x in args.skip.split(',')]
        for value in skip_values:
            # Group keywords that map to multiple underlying rules
            if value == 'code-block-newlines':
                # Skip both before/after code block rules
                skip_rules.update({6, 7})
                continue
            if value == 'display-math-newlines':
                # Skip display math block spacing and surrounding newlines
                skip_rules.add(21)
                continue

            # Check for sub-keywords first (these don't map directly to rule numbers)
            if value in ('em-dash', 'guillemet'):
                # These are handled separately in process_file via skip_string
                continue

            # Try to parse as number first
            try:
                rule_num = int(value)
                if rule_num not in LINTING_RULES:
                    print(f"Error: Invalid rule number: {rule_num}", file=sys.stderr)
                    print(f"Valid rule numbers are: {sorted(LINTING_RULES.keys())}", file=sys.stderr)
                    sys.exit(1)
                skip_rules.add(rule_num)
            except ValueError:
                # Not a number, treat as keyword
                if value in KEYWORD_TO_RULE:
                    skip_rules.add(KEYWORD_TO_RULE[value])
                else:
                    print(f"Error: Invalid keyword: {value}", file=sys.stderr)
                    valid_keywords = ', '.join(
                        sorted(KEYWORD_TO_RULE.keys())
                        + ['em-dash', 'guillemet', 'code-block-newlines', 'display-math-newlines', 'emphasis']
                    )
                    print(f"Valid keywords are: {valid_keywords}", file=sys.stderr)
                    sys.exit(1)

    # If no files provided as arguments, check STDIN
    if not files and not sys.stdin.isatty():
        # Read all STDIN content
        stdin_content = sys.stdin.read()
        stdin_lines = stdin_content.splitlines()

        if stdin_lines:
            # Check if first line looks like a file path (contains path separator or ends with .md)
            first_line = stdin_lines[0].strip()
            looks_like_file_path = (
                '/' in first_line or
                '\\' in first_line or
                first_line.endswith('.md') or
                Path(first_line).exists()
            )

            if looks_like_file_path:
                # Treat as file paths (one per line)
                for line in stdin_lines:
                    filepath = line.strip()
                    if filepath:
                        files.append(filepath)
            else:
                # Treat as markdown content - process directly
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
                    tmp.write(stdin_content)
                    tmp_path = tmp.name

                try:
                    process_file(tmp_path, wrap_width, overwrite=False, skip_rules=skip_rules, skip_string=args.skip, reverse_emphasis=args.reverse_emphasis)
                finally:
                    os.unlink(tmp_path)
                sys.exit(0)

    # If still no files, find all markdown files
    if not files:
        root = Path('.')
        for md_file in root.rglob('*.md'):
            # Skip vendor, build, git directories
            if any(part in str(md_file) for part in ['vendor', 'build', '.git', 'node_modules']):
                continue
            files.append(str(md_file))

    if not files:
        print("No files to process.", file=sys.stderr)
        sys.exit(1)

    if overwrite:
        changed_files = []
        for filepath in sorted(files):
            if process_file(filepath, wrap_width, overwrite=True, skip_rules=skip_rules, skip_string=args.skip, reverse_emphasis=args.reverse_emphasis):
                changed_files.append(filepath)

        if changed_files:
            print(f"Modified {len(changed_files)} file(s):")
            for f in changed_files:
                print(f"  {f}")
        else:
            print("No files needed changes.")
    else:
        # Output to STDOUT - process all files sequentially
        for filepath in sorted(files):
            process_file(filepath, wrap_width, overwrite=False, skip_rules=skip_rules, skip_string=args.skip, reverse_emphasis=args.reverse_emphasis)

if __name__ == '__main__':
    main()
