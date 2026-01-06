use clap::{Arg, Command};
use regex::Regex;
use serde::Deserialize;
use std::collections::HashSet;
use std::fs;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};

const VERSION: &str = "0.1.5";
const DEFAULT_WRAP_WIDTH: usize = 60;

// Valid GitHub emoji names (normalized: lowercase, hyphens to underscores)
const VALID_EMOJI_NAMES: &[&str] = &[
    "+1", "100", "1234", "8ball", "_1", "a", "ab", "abc", "abcd", "accept", "aerial_tramway",
    "airplane", "alarm_clock", "alien", "ambulance", "anchor", "angel", "anger", "angry",
    "anguished", "ant", "apple", "aquarius", "aries", "arrow_backward", "arrow_double_down",
    "arrow_double_up", "arrow_down", "arrow_down_small", "arrow_forward", "arrow_heading_down",
    "arrow_heading_up", "arrow_left", "arrow_lower_left", "arrow_lower_right", "arrow_right",
    "arrow_right_hook", "arrow_up", "arrow_up_down", "arrow_up_small", "arrow_upper_left",
    "arrow_upper_right", "arrows_clockwise", "arrows_counterclockwise", "art", "articulated_lorry",
    "astonished", "atm", "b", "baby", "baby_bottle", "baby_chick", "baby_symbol", "back",
    "baggage_claim", "balloon", "ballot_box_with_check", "bamboo", "banana", "bangbang", "bank",
    "bar_chart", "barber", "baseball", "basketball", "bath", "bathtub", "battery", "bear", "bee",
    "beer", "beers", "beetle", "beginner", "bell", "bento", "bicyclist", "bike", "bikini", "bird",
    "birthday", "black_circle", "black_joker", "black_large_square", "black_medium_small_square",
    "black_medium_square", "black_nib", "black_small_square", "black_square_button", "blossom",
    "blowfish", "blue_book", "blue_car", "blue_heart", "blush", "boar", "boat", "bomb", "book",
    "bookmark", "bookmark_tabs", "books", "boom", "boot", "bouquet", "bow", "bowling", "boy",
    "bread", "bride_with_veil", "bridge_at_night", "briefcase", "broken_heart", "bug", "bulb",
    "bullettrain_front", "bullettrain_side", "bus", "busstop", "bust_in_silhouette",
    "busts_in_silhouette", "cactus", "cake", "calendar", "calling", "camel", "camera", "cancer",
    "candy", "capital_abcd", "capricorn", "car", "card_index", "carousel_horse", "cat", "cat2",
    "cd", "chart", "chart_with_downwards_trend", "chart_with_upwards_trend", "checkered_flag",
    "cherries", "cherry_blossom", "chestnut", "chicken", "children_crossing", "chocolate_bar",
    "christmas_tree", "church", "cinema", "circus_tent", "city_sunrise", "city_sunset", "cl",
    "clap", "clapper", "clipboard", "clock1", "clock10", "clock11", "clock12", "clock130",
    "clock2", "clock230", "clock3", "clock330", "clock4", "clock430", "clock5", "clock530",
    "clock6", "clock630", "clock7", "clock730", "clock8", "clock830", "clock9", "clock930",
    "closed_book", "closed_lock_with_key", "closed_umbrella", "cloud", "clubs", "cn", "cocktail",
    "coffee", "cold_sweat", "collision", "computer", "confetti_ball", "confounded", "confused",
    "congratulations", "construction", "construction_worker", "convenience_store", "cookie",
    "cool", "cop", "copyright", "corn", "couple", "couple_with_heart", "couplekiss", "cow",
    "cow2", "credit_card", "crescent_moon", "crossed_flags", "crown", "cry", "crying_cat_face",
    "crystal_ball", "cupid", "curly_loop", "currency_exchange", "curry", "custard", "customs",
    "dancer", "dancers", "dango", "dart", "dash", "date", "de", "deciduous_tree",
    "department_store", "diamond_shape_with_a_dot_inside", "diamonds", "disappointed",
    "disappointed_relieved", "dizzy", "dizzy_face", "do_not_litter", "dog", "dog2", "dollar",
    "dolls", "dolphin", "donut", "door", "doughnut", "dragon", "dragon_face", "dress",
    "dromedary_camel", "droplet", "dvd", "ear", "ear_of_rice", "earth_africa", "earth_americas",
    "earth_asia", "egg", "eggplant", "eight", "eight_pointed_black_star", "eight_spoked_asterisk",
    "electric_plug", "elephant", "email", "end", "envelope", "envelope_with_arrow", "es", "euro",
    "european_castle", "european_post_office", "evergreen_tree", "exclamation", "expressionless",
    "eyeglasses", "eyes", "facepunch", "factory", "fallen_leaf", "family", "fast_forward", "fax",
    "fearful", "feelsgood", "feet", "ferris_wheel", "file_folder", "finnadie", "fire", "fireworks",
    "first_quarter_moon", "first_quarter_moon_with_face", "fish", "fish_cake",
    "fishing_pole_and_fish", "fist", "five", "flags", "flashlight", "flipper", "floppy_disk",
    "flower_playing_cards", "flushed", "foggy", "football", "footprints", "fork_and_knife",
    "fountain", "four", "four_leaf_clover", "fr", "free", "fried_shrimp", "fries", "frog",
    "frowning", "fu", "fuelpump", "full_moon", "full_moon_with_face", "game_die", "gb", "gem",
    "gemini", "ghost", "gift", "gift_heart", "girl", "globe_with_meridians", "goat", "goberserk",
    "godmode", "golf", "grapes", "green_apple", "green_book", "green_heart", "grey_exclamation",
    "grey_question", "grimacing", "grin", "grinning", "guardsman", "guitar", "gun", "haircut",
    "hamburger", "hammer", "hamster", "hand", "handbag", "hankey", "hatched_chick",
    "hatching_chick", "headphones", "hear_no_evil", "heart", "heart_decoration", "heart_eyes",
    "heart_eyes_cat", "heartbeat", "heartpulse", "hearts", "heavy_check_mark",
    "heavy_division_sign", "heavy_dollar_sign", "heavy_exclamation_mark", "heavy_minus_sign",
    "heavy_multiplication_x", "heavy_plus_sign", "helicopter", "herb", "hibiscus",
    "high_brightness", "high_heel", "hocho", "honey_pot", "honeybee", "horse", "horse_racing",
    "hospital", "hotel", "hotsprings", "hourglass", "hourglass_flowing_sand", "house",
    "house_with_garden", "hushed", "ice_cream", "icecream", "id", "ideograph_advantage", "imp",
    "inbox_tray", "incoming_envelope", "information_desk_person", "information_source", "innocent",
    "interrobang", "iphone", "it", "izakaya_lantern", "jack_o_lantern", "japan", "japanese_castle",
    "japanese_goblin", "japanese_ogre", "jeans", "joy", "joy_cat", "jp", "key", "keycap_ten",
    "kimono", "kiss", "kissing", "kissing_cat", "kissing_closed_eyes", "kissing_heart",
    "kissing_smiling_eyes", "koala", "koko", "kr", "large_blue_circle", "large_blue_diamond",
    "large_orange_diamond", "last_quarter_moon", "last_quarter_moon_with_face", "laughing",
    "leaves", "ledger", "left_luggage", "left_right_arrow", "leftwards_arrow_with_hook", "lemon",
    "leo", "leopard", "libra", "light_rail", "link", "lips", "lipstick", "lock",
    "lock_with_ink_pen", "lollipop", "loop", "loudspeaker", "love_hotel", "love_letter",
    "low_brightness", "m", "mag", "mag_right", "mahjong", "mailbox", "mailbox_closed",
    "mailbox_with_mail", "mailbox_with_no_mail", "man", "man_with_gua_pi_mao", "man_with_turban",
    "mans_shoe", "maple_leaf", "mask", "massage", "meat_on_bone", "mega", "melon", "memo", "mens",
    "metal", "metro", "microphone", "microscope", "milky_way", "minibus", "minidisc",
    "mobile_phone_off", "money_with_wings", "moneybag", "monkey", "monkey_face", "monorail",
    "moon", "mortar_board", "mount_fuji", "mountain_bicyclist", "mountain_cableway",
    "mountain_railway", "mouse", "mouse2", "movie_camera", "moyai", "muscle", "mushroom",
    "musical_keyboard", "musical_note", "musical_score", "mute", "nail_care", "name_badge",
    "neckbeard", "necktie", "negative_squared_cross_mark", "neutral_face", "new", "new_moon",
    "new_moon_with_face", "newspaper", "ng", "nine", "no_bell", "no_bicycles", "no_entry",
    "no_entry_sign", "no_good", "no_mobile_phones", "no_mouth", "no_pedestrians", "no_smoking",
    "non_potable_water", "nose", "notebook", "notebook_with_decorative_cover", "notes",
    "nut_and_bolt", "o", "o2", "ocean", "octocat", "octopus", "oden", "office", "ok", "ok_hand",
    "ok_woman", "older_man", "older_woman", "on", "oncoming_automobile", "oncoming_bus",
    "oncoming_police_car", "oncoming_taxi", "one", "open_book", "open_file_folder", "open_hands",
    "open_mouth", "ophiuchus", "orange_book", "outbox_tray", "ox", "package", "page_facing_up",
    "page_with_curl", "pager", "palm_tree", "panda_face", "paperclip", "parking",
    "part_alternation_mark", "partly_sunny", "passport_control", "paw_prints", "peach", "pear",
    "pencil", "pencil2", "penguin", "pensive", "performing_arts", "persevere", "person_frowning",
    "person_with_blond_hair", "person_with_pouting_face", "phone", "pig", "pig2", "pig_nose",
    "pill", "pineapple", "pisces", "pizza", "point_down", "point_left", "point_right", "point_up",
    "point_up_2", "police_car", "poodle", "poop", "post_office", "postal_horn", "postbox",
    "potable_water", "pouch", "poultry_leg", "pound", "pray", "princess", "punch", "purple_heart",
    "purse", "pushpin", "put_litter_in_its_place", "question", "rabbit", "rabbit2", "racehorse",
    "radio", "radio_button", "rage", "rage1", "rage2", "rage3", "rage4", "railway_car", "rainbow",
    "raised_hand", "raised_hands", "raising_hand", "ram", "ramen", "rat", "recycle", "red_car",
    "red_circle", "registered", "relaxed", "relieved", "repeat", "repeat_one", "restroom",
    "revolving_hearts", "rewind", "ribbon", "rice", "rice_ball", "rice_cracker", "rice_scene",
    "ring", "rocket", "roller_coaster", "rooster", "rose", "rotating_light", "round_pushpin",
    "rowboat", "ru", "rugby_football", "runner", "running", "running_shirt_with_sash", "sa",
    "sagittarius", "sailboat", "sake", "sandal", "santa", "satellite", "satisfied", "saxophone",
    "school", "school_satchel", "scissors", "scorpius", "scream", "scream_cat", "scroll", "seat",
    "secret", "see_no_evil", "seedling", "seven", "shaved_ice", "sheep", "shell", "ship",
    "shipit", "shirt", "shit", "shoe", "shower", "signal_strength", "six", "six_pointed_star",
    "ski", "skull", "sleeping", "sleepy", "slot_machine", "small_blue_diamond",
    "small_orange_diamond", "small_red_triangle", "small_red_triangle_down", "smile", "smile_cat",
    "smiley", "smiley_cat", "smirk", "smirk_cat", "smoking", "snail", "snake", "snowboarder",
    "snowflake", "snowman", "sob", "soccer", "soon", "sos", "sound", "space_invader", "spades",
    "spaghetti", "sparkle", "sparkler", "sparkles", "sparkling_heart", "speak_no_evil", "speaker",
    "speech_balloon", "speedboat", "squirrel", "star", "star2", "stars", "station",
    "statue_of_liberty", "steam_locomotive", "stew", "straight_ruler", "strawberry",
    "stuck_out_tongue", "stuck_out_tongue_closed_eyes", "stuck_out_tongue_winking_eye",
    "sun_with_face", "sunflower", "sunglasses", "sunny", "sunrise", "sunrise_over_mountains",
    "surfer", "sushi", "suspect", "suspension_railway", "sweat", "sweat_drops", "sweat_smile",
    "sweet_potato", "swimmer", "symbols", "syringe", "tada", "tanabata_tree", "tangerine",
    "taurus", "taxi", "tea", "telephone", "telephone_receiver", "telescope", "tennis", "tent",
    "thought_balloon", "three", "thumbsdown", "thumbsup", "ticket", "tiger", "tiger2",
    "tired_face", "tm", "toilet", "tokyo_tower", "tomato", "tongue", "top", "tophat", "tractor",
    "traffic_light", "train", "train2", "tram", "triangular_flag_on_post", "triangular_ruler",
    "trident", "triumph", "trolleybus", "trophy", "tropical_drink", "tropical_fish", "truck",
    "trumpet", "tshirt", "tulip", "turtle", "tv", "twisted_rightwards_arrows", "two",
    "two_hearts", "two_men_holding_hands", "two_women_holding_hands", "u5272", "u5408", "u55b6",
    "u6307", "u6708", "u6709", "u6e80", "u7121", "u7533", "u7981", "u7a7a", "uk", "umbrella",
    "unamused", "underage", "unlock", "up", "us", "v", "vertical_traffic_light", "vhs",
    "vibration_mode", "video_camera", "video_game", "violin", "virgo", "volcano", "vs",
    "walking", "waning_crescent_moon", "waning_gibbous_moon", "warning", "watch", "water_buffalo",
    "watermelon", "wave", "wavy_dash", "waxing_crescent_moon", "waxing_gibbous_moon", "wc",
    "weary", "wedding", "whale", "whale2", "wheelchair", "white_check_mark", "white_circle",
    "white_flower", "white_large_square", "white_medium_small_square", "white_medium_square",
    "white_small_square", "white_square_button", "wind_chime", "wine_glass", "wink", "wolf",
    "woman", "womans_clothes", "womans_hat", "womens", "worried", "wrench", "x", "yellow_heart",
    "yen", "yum", "zap", "zero", "zzz",
];

fn valid_emoji_names_set() -> HashSet<&'static str> {
    VALID_EMOJI_NAMES.iter().copied().collect()
}

fn is_code_block(line: &str) -> bool {
    let stripped = line.trim();
    stripped.starts_with("```") || stripped.starts_with("~~~")
}

fn is_list_item(line: &str) -> bool {
    let stripped = line.trim_start();
    Regex::new(r"^[-*+]\s+|^[-*+][^\s]|^\d+\.\s+")
        .unwrap()
        .is_match(stripped)
}

fn is_headline(line: &str) -> bool {
    let stripped = line.trim();
    // Match # followed by either whitespace or content (to catch malformed headlines like #BadHeader)
    Regex::new(r"^#+\s").unwrap().is_match(stripped) || Regex::new(r"^#+[^\s#]").unwrap().is_match(stripped)
}

fn is_horizontal_rule(line: &str) -> bool {
    let stripped = line.trim();
    Regex::new(r"^[-*_]{3,}$").unwrap().is_match(stripped)
}

fn normalize_trailing_whitespace(line: &str) -> String {
    let has_newline = line.ends_with('\n');
    let line_no_nl = line.trim_end_matches('\n');

    let trailing_spaces = line_no_nl.len() - line_no_nl.trim_end_matches(' ').len();
    let result = if trailing_spaces == 2 {
        format!("{}  ", line_no_nl.trim_end_matches('\t'))
    } else {
        line_no_nl.trim_end().to_string()
    };

    if has_newline {
        format!("{}\n", result)
    } else {
        result
    }
}

fn normalize_headline_spacing(line: &str) -> String {
    let has_newline = line.ends_with('\n');
    let line_no_nl = line.trim_end_matches('\n');

    let re = Regex::new(r"^(#+)(\s*)(.*)$").unwrap();
    if let Some(caps) = re.captures(line_no_nl) {
        let hashes = caps.get(1).unwrap().as_str();
        let spaces = caps.get(2).unwrap().as_str();
        let content = caps.get(3).unwrap().as_str();

        if spaces != " " {
            let result = format!("{} {}", hashes, content);
            return if has_newline {
                format!("{}\n", result)
            } else {
                result
            };
        }
    }
    line.to_string()
}

fn normalize_ial_spacing(line: &str) -> String {
    let has_newline = line.ends_with('\n');
    let line_no_nl = line.trim_end_matches('\n');

    let re = Regex::new(r"(\{:?\s*)([^}]*?)(\s*\})").unwrap();
    let result = re.replace_all(line_no_nl, |caps: &regex::Captures| {
        let opening = caps.get(1).unwrap().as_str();
        let content = caps.get(2).unwrap().as_str();

        let normalized_content = content.split_whitespace().collect::<Vec<_>>().join(" ");

        if opening.contains(':') {
            format!("{{: {}}}", normalized_content)
        } else {
            format!("{{{}}}", normalized_content)
        }
    });

    if has_newline {
        format!("{}\n", result)
    } else {
        result.to_string()
    }
}

fn normalize_fenced_code_lang(line: &str) -> String {
    let re = Regex::new(r"^(```|~~~)\s+([^\s`~]+)").unwrap();
    re.replace(line, |caps: &regex::Captures| {
        let fence = caps.get(1).unwrap().as_str();
        let lang = caps.get(2).unwrap().as_str();
        format!("{}{}", fence, lang)
    })
    .to_string()
}

fn normalize_reference_link(line: &str) -> String {
    let re = Regex::new(r"^(\[[^\]]+\])\s*:\s*").unwrap();
    re.replace(line, |caps: &regex::Captures| {
        format!("{}: ", caps.get(1).unwrap().as_str())
    })
    .to_string()
}

fn normalize_task_checkbox(line: &str) -> String {
    let re = Regex::new(r"^(\s*[-*+])\s+(\[[Xx]\])\s+").unwrap();
    re.replace(line, |caps: &regex::Captures| {
        format!("{} [x] ", caps.get(1).unwrap().as_str())
    })
    .to_string()
}

fn normalize_blockquote_spacing(line: &str) -> String {
    let re = Regex::new(r"^(\s*)>([^\s>])").unwrap();
    re.replace(line, |caps: &regex::Captures| {
        let indent = caps.get(1).unwrap().as_str();
        let content = caps.get(2).unwrap().as_str();
        format!("{}> {}", indent, content)
    })
    .to_string()
}

fn normalize_math_spacing(line: &str, is_in_code_block: bool) -> String {
    if is_in_code_block {
        return line.to_string();
    }

    let has_newline = line.ends_with('\n');
    let line_no_nl = line.trim_end_matches('\n');

    // Display math: $$...$$
    let display_math_re = Regex::new(r"\$\$([\s\S]*?)\$\$").unwrap();
    let result = display_math_re.replace_all(line_no_nl, |caps: &regex::Captures| {
        let content = caps.get(1).unwrap().as_str();
        let lines: Vec<&str> = content.split('\n').collect();

        let normalized = if lines.len() > 1 {
            let mut lines = lines;
            if !lines.is_empty() && lines[0].trim().is_empty() {
                lines.remove(0);
            }
            if !lines.is_empty() && lines[lines.len() - 1].trim().is_empty() {
                lines.pop();
            }
            if !lines.is_empty() {
                let first = lines[0].trim_start();
                let last_idx = lines.len() - 1;
                lines[last_idx] = lines[last_idx].trim_end();
                lines[0] = first;
            }
            lines.join("\n")
        } else {
            content.trim().to_string()
        };

        format!("$${}$$", normalized)
    });

    // Inline math: $...$ (conservative)
    // Skip if closing $ has space before it and non-space after it (likely not math, e.g., currency)
    let inline_math_re = Regex::new(r"\$([^\$]+?)\$").unwrap();
    let result_str = result.to_string(); // Convert to owned string for checking
    let result = inline_math_re.replace_all(&result_str, |caps: &regex::Captures| {
        let full_match = caps.get(0).unwrap();
        let content = caps.get(1).unwrap().as_str();
        let match_end = full_match.end();

        // Check if closing $ has space before it and non-space after it
        let has_space_before_closing = content.ends_with(' ') || content.ends_with('\t');
        let has_non_space_after = match_end < result_str.len() &&
            !result_str.chars().nth(match_end).map(|c| c.is_whitespace()).unwrap_or(true);

        // If closing $ has space before it AND non-space after it, skip normalization (not math)
        if has_space_before_closing && has_non_space_after {
            return full_match.as_str().to_string();
        }

        // Otherwise, check if it looks like currency
        let trimmed_content = content.trim();
        let currency_re = Regex::new(r"^[\d.,\s]+$").unwrap();
        if currency_re.is_match(trimmed_content) {
            format!("${}$", content)
        } else {
            format!("${}$", trimmed_content)
        }
    });

    if has_newline {
        format!("{}\n", result)
    } else {
        result.to_string()
    }
}

fn levenshtein_distance(s1: &str, s2: &str) -> usize {
    let s1_chars: Vec<char> = s1.chars().collect();
    let s2_chars: Vec<char> = s2.chars().collect();

    if s1_chars.len() < s2_chars.len() {
        return levenshtein_distance(s2, s1);
    }

    if s2_chars.is_empty() {
        return s1_chars.len();
    }

    let mut previous_row: Vec<usize> = (0..=s2_chars.len()).collect();

    for (i, &c1) in s1_chars.iter().enumerate() {
        let mut current_row = vec![i + 1];
        for (j, &c2) in s2_chars.iter().enumerate() {
            let insertions = previous_row[j + 1] + 1;
            let deletions = current_row[j] + 1;
            let substitutions = previous_row[j] + if c1 == c2 { 0 } else { 1 };
            current_row.push(insertions.min(deletions).min(substitutions));
        }
        previous_row = current_row;
    }

    previous_row[s2_chars.len()]
}

fn normalize_emoji_name(name: &str) -> String {
    name.trim_matches(':')
        .to_lowercase()
        .replace('-', "_")
}

fn find_best_emoji_match(name: &str, max_distance: usize, valid_set: &HashSet<&str>) -> Option<&'static str> {
    let normalized = normalize_emoji_name(name);

    if valid_set.contains(normalized.as_str()) {
        return VALID_EMOJI_NAMES.iter().find(|&&n| n == normalized).copied();
    }

    let mut candidates: Vec<(usize, usize, &str)> = Vec::new();
    for &emoji_name in VALID_EMOJI_NAMES {
        let distance = levenshtein_distance(&normalized, emoji_name);
        if distance <= max_distance {
            candidates.push((distance, emoji_name.len(), emoji_name));
        }
    }

    if candidates.is_empty() {
        return None;
    }

    candidates.sort_by_key(|&(dist, len, _)| (dist, len));
    Some(candidates[0].2)
}

fn normalize_emoji_names(line: &str, valid_set: &HashSet<&str>) -> String {
    let re = Regex::new(r":([a-zA-Z0-9_+-]+):").unwrap();
    re.replace_all(line, |caps: &regex::Captures| {
        let emoji_name = caps.get(1).unwrap().as_str();
        let normalized = normalize_emoji_name(emoji_name);

        if valid_set.contains(normalized.as_str()) {
            return format!(":{}:", normalized);
        }

        if let Some(best_match) = find_best_emoji_match(emoji_name, 4, valid_set) {
            return format!(":{}:", best_match);
        }

        caps.get(0).unwrap().as_str().to_string()
    })
    .to_string()
}

fn normalize_typography(line: &str, skip_em_dash: bool, skip_guillemet: bool) -> String {
    let mut result = line.to_string();

    // Curly quotes to straight quotes
    result = result.replace('\u{201C}', "\"").replace('\u{201D}', "\""); // Left/Right double quote
    result = result.replace('\u{2018}', "'").replace('\u{2019}', "'"); // Left/Right single quote
    result = result.replace('\u{2013}', "--"); // En dash

    if !skip_em_dash {
        result = result.replace('\u{2014}', "---"); // Em dash
    }

    result = result.replace('\u{2026}', "..."); // Ellipsis

    if !skip_guillemet {
        result = result.replace('\u{00AB}', "\"").replace('\u{00BB}', "\""); // Guillemets
    }

    result
}

fn normalize_bold_italic(line: &str) -> String {
    // First, identify protected regions (code spans, emoji markers) in the ORIGINAL line
    // Code spans: `code` or ``code``
    let code_span_re = Regex::new(r"`+[^`]*`+").unwrap();
    // Emoji markers: :emoji_name: (case-insensitive, allows underscores, hyphens, plus signs)
    let emoji_re = Regex::new(r"(?i):[a-z0-9_+-]+:").unwrap();

    // Collect all protected regions from the original line
    let mut protected_ranges: Vec<(usize, usize)> = Vec::new();

    for mat in code_span_re.find_iter(line) {
        protected_ranges.push((mat.start(), mat.end()));
    }

    for mat in emoji_re.find_iter(line) {
        protected_ranges.push((mat.start(), mat.end()));
    }

    // Sort and merge overlapping ranges
    protected_ranges.sort_by_key(|r| r.0);
    let mut merged: Vec<(usize, usize)> = Vec::new();
    for (start, end) in protected_ranges {
        if let Some(last) = merged.last_mut() {
            if start <= last.1 {
                last.1 = last.1.max(end);
            } else {
                merged.push((start, end));
            }
        } else {
            merged.push((start, end));
        }
    }

    // Helper to check if a position is in a protected region
    let is_protected = |pos: usize| -> bool {
        merged.iter().any(|(start, end)| pos >= *start && pos < *end)
    };

    let mut result = line.to_string();

    // Triple asterisks: ***text*** → __*text*__
    let re1 = Regex::new(r"\*\*\*([^*]+?)\*\*\*").unwrap();
    result = re1.replace_all(&result, |caps: &regex::Captures| {
        let full_match = caps.get(0).unwrap();
        if is_protected(full_match.start()) {
            full_match.as_str().to_string()
        } else {
            format!("__*{}*__", &caps[1])
        }
    }).to_string();

    // Bold-italic nested: **_text_** → __*text*__
    let re2 = Regex::new(r"\*\*_([^_]+?)_\*\*").unwrap();
    result = re2.replace_all(&result, |caps: &regex::Captures| {
        let full_match = caps.get(0).unwrap();
        if is_protected(full_match.start()) {
            full_match.as_str().to_string()
        } else {
            format!("__*{}*__", &caps[1])
        }
    }).to_string();

    // Italic-bold nested: _**text**_ → *__text__*
    let re3 = Regex::new(r"_(\*\*[^*]+?\*\*)_").unwrap();
    result = re3.replace_all(&result, |caps: &regex::Captures| {
        let full_match = caps.get(0).unwrap();
        if is_protected(full_match.start()) {
            full_match.as_str().to_string()
        } else {
            format!("*{}*", &caps[1])
        }
    }).to_string();

    // Rebuild protected regions from current result (positions may have shifted)
    let mut protected_ranges_result: Vec<(usize, usize)> = Vec::new();
    for mat in code_span_re.find_iter(&result) {
        protected_ranges_result.push((mat.start(), mat.end()));
    }
    for mat in emoji_re.find_iter(&result) {
        protected_ranges_result.push((mat.start(), mat.end()));
    }
    protected_ranges_result.sort_by_key(|r| r.0);
    let mut merged_result: Vec<(usize, usize)> = Vec::new();
    for (start, end) in protected_ranges_result {
        if let Some(last) = merged_result.last_mut() {
            if start <= last.1 {
                last.1 = last.1.max(end);
            } else {
                merged_result.push((start, end));
            }
        } else {
            merged_result.push((start, end));
        }
    }
    let is_protected_result = |pos: usize| -> bool {
        merged_result.iter().any(|(start, end)| pos >= *start && pos < *end)
    };

    // Bold with ** → __ (avoid matching *** or **_)
    // Since Rust regex doesn't support lookbehind/lookahead, we'll manually check context
    let re4 = Regex::new(r"(\*\*)([^*]+?)(\*\*)").unwrap();
    let mut new_result = String::new();
    let mut last_end = 0;
    let result_bytes = result.as_bytes();

    for cap in re4.captures_iter(&result) {
        let full_match = cap.get(0).unwrap();
        let start = full_match.start();
        let end = full_match.end();

        // Add text before match
        new_result.push_str(&result[last_end..start]);

        // Check if in protected region
        if is_protected_result(start) {
            // Keep original
            new_result.push_str(full_match.as_str());
        } else {
            // Check context using byte indices: not preceded by * and not followed by *
            let preceded_by_star = start > 0 && result_bytes[start - 1] == b'*';
            let followed_by_star = end < result_bytes.len() && result_bytes[end] == b'*';

            if preceded_by_star || followed_by_star {
                // Keep original
                new_result.push_str(full_match.as_str());
            } else {
                // Replace **text** with __text__
                let content = cap.get(2).unwrap().as_str();
                new_result.push_str(&format!("__{}__", content));
            }
        }

        last_end = end;
    }
    new_result.push_str(&result[last_end..]);
    result = new_result;

    // Rebuild protected regions again for italic check
    let mut protected_ranges_result2: Vec<(usize, usize)> = Vec::new();
    for mat in code_span_re.find_iter(&result) {
        protected_ranges_result2.push((mat.start(), mat.end()));
    }
    for mat in emoji_re.find_iter(&result) {
        protected_ranges_result2.push((mat.start(), mat.end()));
    }
    protected_ranges_result2.sort_by_key(|r| r.0);
    let mut merged_result2: Vec<(usize, usize)> = Vec::new();
    for (start, end) in protected_ranges_result2 {
        if let Some(last) = merged_result2.last_mut() {
            if start <= last.1 {
                last.1 = last.1.max(end);
            } else {
                merged_result2.push((start, end));
            }
        } else {
            merged_result2.push((start, end));
        }
    }
    let is_protected_result2 = |pos: usize| -> bool {
        merged_result2.iter().any(|(start, end)| pos >= *start && pos < *end)
    };

    // Italics with _ → * (avoid matching __ or **_)
    let re5 = Regex::new(r"(_)([^_]+?)(_)").unwrap();
    let mut new_result = String::new();
    let mut last_end = 0;
    let result_bytes = result.as_bytes();

    for cap in re5.captures_iter(&result) {
        let full_match = cap.get(0).unwrap();
        let start = full_match.start();
        let end = full_match.end();

        // Add text before match
        new_result.push_str(&result[last_end..start]);

        // Check if in protected region
        if is_protected_result2(start) {
            // Keep original
            new_result.push_str(full_match.as_str());
        } else {
            // Check context using byte indices: not preceded by _ and not followed by _
            let preceded_by_underscore = start > 0 && result_bytes[start - 1] == b'_';
            let followed_by_underscore = end < result_bytes.len() && result_bytes[end] == b'_';

            if preceded_by_underscore || followed_by_underscore {
                // Keep original
                new_result.push_str(full_match.as_str());
            } else {
                // Replace _text_ with *text*
                let content = cap.get(2).unwrap().as_str();
                new_result.push_str(&format!("*{}*", content));
            }
        }

        last_end = end;
    }
    new_result.push_str(&result[last_end..]);
    result = new_result;

    result
}

fn is_separator_row(line: &str) -> bool {
    let stripped = line.trim();
    if !stripped.contains('|') {
        return false;
    }
    let chars: HashSet<char> = stripped.replace('|', "").chars().collect();
    let allowed: HashSet<char> = ": -".chars().collect();
    chars.is_subset(&allowed)
}

fn count_columns(line: &str) -> usize {
    let stripped = line.trim();
    if stripped.is_empty() {
        return 0;
    }

    let pipe_count = stripped.matches('|').count();
    if stripped.starts_with('|') {
        pipe_count.saturating_sub(1)
    } else {
        pipe_count + 1
    }
}

fn normalize_table_formatting(table_lines: &[String]) -> Option<Vec<String>> {
    if table_lines.is_empty() {
        return None;
    }

    let lines: Vec<String> = table_lines
        .iter()
        .filter_map(|l| {
            let trimmed = l.trim_end_matches('\n');
            if trimmed.is_empty() {
                None
            } else {
                Some(trimmed.to_string())
            }
        })
        .collect();

    if lines.len() < 2 {
        return None;
    }

    if !lines.iter().all(|l| l.contains('|')) {
        return None;
    }

    let mut separator_idx: Option<usize> = None;
    let mut is_headerless = false;
    let mut lines = lines;

    if is_separator_row(&lines[0]) {
        is_headerless = true;
        separator_idx = Some(0);
    } else {
        for (i, line) in lines.iter().enumerate() {
            if is_separator_row(line) {
                separator_idx = Some(i);
                break;
            }
        }
    }

    let separator_idx = if let Some(idx) = separator_idx {
        idx
    } else {
        let num_cols = count_columns(&lines[0]);
        if num_cols == 0 {
            return None;
        }
        let default_separator = format!(
            "|{}|",
            (0..num_cols).map(|_| " --- ").collect::<Vec<_>>().join("|")
        );
        lines.insert(1, default_separator);
        1
    };

    let formatline = lines[separator_idx].trim();
    if formatline.is_empty() {
        return None;
    }

    let mut formatline = formatline.to_string();
    if formatline.starts_with('|') {
        formatline.remove(0);
    }
    if formatline.ends_with('|') {
        formatline.pop();
    }

    let fstrings: Vec<&str> = formatline.split('|').collect();
    let mut justify = Vec::new();
    for cell in fstrings {
        let cell = cell.trim();
        let ends = if cell.is_empty() {
            String::new()
        } else {
            format!("{}{}", cell.chars().next().unwrap_or(' '), cell.chars().last().unwrap_or(' '))
        };
        if ends == "::" {
            justify.push("::");
        } else if ends == "-:" {
            justify.push("-:");
        } else {
            justify.push(":-");
        }
    }

    let columns = justify.len();
    let content_lines: Vec<&String> = lines
        .iter()
        .enumerate()
        .filter_map(|(i, line)| if i != separator_idx { Some(line) } else { None })
        .collect();

    let mut content = Vec::new();
    for line in content_lines {
        let mut stripped = line.trim().to_string();
        if stripped.is_empty() {
            continue;
        }
        if stripped.starts_with('|') {
            stripped.remove(0);
        }
        if stripped.ends_with('|') {
            stripped.pop();
        }
        let cells: Vec<String> = stripped
            .split('|')
            .map(|x| format!(" {} ", x.trim()))
            .collect();
        content.push(cells);
    }

    for row in &mut content {
        while row.len() < columns {
            row.push(" ".to_string());
        }
    }

    let mut widths = vec![2; columns];
    for row in &content {
        for (i, cell) in row.iter().enumerate().take(columns) {
            widths[i] = widths[i].max(cell.chars().count());
        }
    }

    let just = |s: &str, t: &str, n: usize| -> String {
        match t {
            "::" => {
                let padding = n.saturating_sub(s.chars().count());
                let left = padding / 2;
                let right = padding - left;
                format!("{}{}{}", " ".repeat(left), s, " ".repeat(right))
            }
            "-:" => {
                let padding = n.saturating_sub(s.chars().count());
                format!("{}{}", " ".repeat(padding), s)
            }
            _ => {
                let padding = n.saturating_sub(s.chars().count());
                format!("{}{}", s, " ".repeat(padding))
            }
        }
    };

    let mut formatted = Vec::new();
    for row in &content {
        let row_str: Vec<String> = row
            .iter()
            .zip(justify.iter())
            .zip(widths.iter())
            .map(|((s, t), n)| just(s, t, *n))
            .collect();
        formatted.push(format!("|{}|", row_str.join("|")));
    }

    let formatline = format!(
        "|{}|",
        justify
            .iter()
            .zip(widths.iter())
            .map(|(j, n)| {
                let j_str = *j;
                let dashes = n.saturating_sub(2);
                format!("{}{}{}", &j_str[0..1], "-".repeat(dashes), &j_str[j_str.len()-1..])
            })
            .collect::<Vec<_>>()
            .join("|")
    );

    if is_headerless {
        formatted.insert(0, formatline);
    } else {
        formatted.insert(1, formatline);
    }

    Some(formatted.iter().map(|l| format!("{}\n", l)).collect())
}

fn detect_list_indent_unit(lines: &[String], start_idx: usize) -> usize {
    let mut list_start = start_idx;

    for i in (0..=start_idx).rev() {
        if i >= lines.len() {
            continue;
        }
        let line = &lines[i];
        if !is_list_item(line) {
            list_start = i + 1;
            break;
        }
        let re = Regex::new(r"^(\s*)([-*+]|\d+\.)").unwrap();
        if let Some(caps) = re.captures(line) {
            let indent = caps.get(1).unwrap().as_str();
            let space_count = indent.chars().filter(|&c| c != '\t').count();
            if space_count == 0 {
                list_start = i;
                break;
            }
        }
    }

    for i in (list_start + 1)..lines.len() {
        let line = &lines[i];
        if !is_list_item(line) {
            if !line.trim().is_empty() {
                break;
            }
            continue;
        }

        let re = Regex::new(r"^(\s*)([-*+]|\d+\.)").unwrap();
        if let Some(caps) = re.captures(line) {
            let indent = caps.get(1).unwrap().as_str();
            let space_count = indent.chars().filter(|&c| c != '\t').count();
            if space_count >= 2 {
                return if space_count >= 4 { 4 } else { 2 };
            }
        }
    }

    2
}

fn spaces_to_tabs_for_list(line: &str, indent_unit: usize) -> String {
    if !is_list_item(line) {
        return line.to_string();
    }

    let has_newline = line.ends_with('\n');
    let line_no_nl = line.trim_end_matches('\n');

    let re = Regex::new(r"^(\s*)([-*+]|\d+\.)(\s*)(.*)$").unwrap();
    if let Some(caps) = re.captures(line_no_nl) {
        let indent = caps.get(1).unwrap().as_str();
        let marker = caps.get(2).unwrap().as_str();
        let marker_space = caps.get(3).unwrap().as_str();
        let content = caps.get(4).unwrap().as_str();

        let marker_space = if marker_space != " " { " " } else { marker_space };

        if indent.contains('\t') {
            return line.to_string();
        }

        let space_count = indent.chars().filter(|&c| c != '\t').count();
        let tabs = "\t".repeat(space_count / indent_unit);

        let result = format!("{}{}{}{}", tabs, marker, marker_space, content);
        return if has_newline {
            format!("{}\n", result)
        } else {
            result
        };
    }

    line.to_string()
}

fn get_list_indent(line: &str) -> usize {
    let re = Regex::new(r"^(\s*)").unwrap();
    if let Some(caps) = re.captures(line) {
        caps.get(1).unwrap().as_str().len()
    } else {
        0
    }
}

#[derive(Clone, Copy, Debug)]
enum ListType {
    Numbered,
    Bulleted,
}

#[derive(Clone, Copy, Debug)]
struct ListContext {
    level: usize,
    list_type: ListType,
    current_number: Option<usize>,
}

fn get_list_level(indent_str: &str, indent_unit: usize) -> usize {
    let tab_count = indent_str.matches('\t').count();
    let space_count = indent_str.chars().filter(|&c| c != '\t').count();
    tab_count + (space_count / indent_unit)
}

fn normalize_list_markers(
    line: &str,
    list_context_stack: &mut Vec<ListContext>,
    indent_unit: usize,
    skip_list_reset: bool,
) -> (String, bool) {
    if !is_list_item(line) {
        return (line.to_string(), false);
    }

    // Remove newline for matching, but preserve it for output
    let line_no_nl = line.trim_end_matches('\n');
    let has_newline = line.ends_with('\n');

    let re = Regex::new(r"^(\s*)([-*+]|\d+\.)(\s*)(.*)$").unwrap();
    let caps = match re.captures(line_no_nl) {
        Some(c) => c,
        None => return (line.to_string(), false),
    };

    let indent = caps.get(1).unwrap().as_str();
    let marker = caps.get(2).unwrap().as_str();
    let marker_space = caps.get(3).unwrap().as_str();
    let content = caps.get(4).unwrap().as_str();

    let current_level = get_list_level(indent, indent_unit);
    let is_numbered = Regex::new(r"^\d+\.$").unwrap().is_match(marker);

    // Update the stack - remove contexts for deeper levels (but keep same or shallower)
    list_context_stack.retain(|ctx| ctx.level <= current_level);

    // Check if we have a context for this exact level
    let matching_context_idx = list_context_stack.iter().rposition(|ctx| ctx.level == current_level);

    let new_marker = if let Some(idx) = matching_context_idx {
        // Continue existing list at this level
        let ctx = &mut list_context_stack[idx];
        match ctx.list_type {
            ListType::Numbered => {
                ctx.current_number = Some(ctx.current_number.unwrap_or(0) + 1);
                format!("{}.", ctx.current_number.unwrap())
            }
            ListType::Bulleted => {
                match current_level {
                    0 => "*".to_string(),
                    1 => "-".to_string(),
                    _ => "+".to_string(),
                }
            }
        }
    } else {
        // New list at this level
        if is_numbered {
            // Extract starting number from marker (e.g., "7." -> 7)
            let start_number = if skip_list_reset {
                // If list-reset is disabled, preserve the starting number
                marker.trim_end_matches('.').parse::<usize>().unwrap_or(1)
            } else {
                // If list-reset is enabled (default), always start at 1
                1
            };
            list_context_stack.push(ListContext {
                level: current_level,
                list_type: ListType::Numbered,
                current_number: Some(start_number),
            });
            format!("{}.", start_number)
        } else {
            list_context_stack.push(ListContext {
                level: current_level,
                list_type: ListType::Bulleted,
                current_number: None,
            });
            match current_level {
                0 => "*".to_string(),
                1 => "-".to_string(),
                _ => "+".to_string(),
            }
        }
    };

    let changed = marker != &new_marker;
    let normalized = if has_newline {
        format!("{}{}{}{}\n", indent, new_marker, marker_space, content)
    } else {
        format!("{}{}{}{}", indent, new_marker, marker_space, content)
    };


    (normalized, changed)
}

fn is_blockquote(line: &str) -> bool {
    line.trim_start().starts_with('>')
}

fn get_blockquote_prefix(line: &str) -> String {
    let re = Regex::new(r"^(\s*)").unwrap();
    let spaces = if let Some(caps) = re.captures(line) {
        caps.get(1).unwrap().as_str()
    } else {
        ""
    };
    if line.trim_start().starts_with('>') {
        format!("{}>", spaces)
    } else {
        String::new()
    }
}

fn should_preserve_line(line: &str) -> bool {
    let stripped = line.trim();
    is_code_block(line)
        || stripped.starts_with('#')
        || is_horizontal_rule(line)
        || stripped.contains('|')  // Tables should not be wrapped
        // Note: blank lines are NOT preserved here - they go through blank line compression
}

fn wrap_text(text: &str, width: usize, prefix: &str) -> Vec<String> {
    if text.chars().count() <= width {
        return vec![text.to_string()];
    }

    let long_link_re = Regex::new(r"\[.*?\]\([^)]{20,}\)").unwrap();
    let long_code_re = Regex::new(r"`[^`]{20,}`").unwrap();

    if long_link_re.is_match(text) || long_code_re.is_match(text) {
        return vec![text.to_string()];
    }

    let words: Vec<&str> = text.split_whitespace().collect();
    let mut lines = Vec::new();
    let mut current_line = prefix.to_string();

    for word in words {
        let test_line = if current_line == prefix {
            format!("{}{}", current_line, word)
        } else {
            format!("{} {}", current_line, word)
        };

        if test_line.chars().count() <= width {
            current_line = test_line;
        } else {
            if current_line != prefix {
                lines.push(current_line.clone());
            }
            current_line = format!("{}{}", prefix, word);
        }
    }

    if current_line != prefix {
        lines.push(current_line);
    }

    if lines.is_empty() {
        vec![text.to_string()]
    } else {
        lines
    }
}

struct LintingRule {
    num: u8,
    description: &'static str,
    keyword: &'static str,
}

const LINTING_RULES: &[LintingRule] = &[
    LintingRule { num: 1, description: "Normalize line endings to Unix", keyword: "line-endings" },
    LintingRule { num: 2, description: "Trim trailing whitespace (preserve exactly 2 spaces)", keyword: "trailing" },
    LintingRule { num: 3, description: "Collapse multiple blank lines (max 1 consecutive)", keyword: "blank-lines" },
    LintingRule { num: 4, description: "Normalize headline spacing (exactly 1 space after #)", keyword: "header-spacing" },
    LintingRule { num: 5, description: "Ensure blank line after headline", keyword: "header-newline" },
    LintingRule { num: 6, description: "Ensure blank line before code block", keyword: "code-before" },
    LintingRule { num: 7, description: "Ensure blank line after code block", keyword: "code-after" },
    LintingRule { num: 8, description: "Ensure blank line before list", keyword: "list-before" },
    LintingRule { num: 9, description: "Ensure blank line after list", keyword: "list-after" },
    LintingRule { num: 10, description: "Ensure blank line before horizontal rule", keyword: "rule-before" },
    LintingRule { num: 11, description: "Ensure blank line after horizontal rule", keyword: "rule-after" },
    LintingRule { num: 12, description: "Convert list indentation spaces to tabs", keyword: "list-tabs" },
    LintingRule { num: 13, description: "Normalize list marker spacing", keyword: "list-marker" },
    LintingRule { num: 14, description: "Wrap text at specified width", keyword: "wrap" },
    LintingRule { num: 15, description: "Ensure exactly one blank line at end of file", keyword: "end-newline" },
    LintingRule { num: 16, description: "Normalize IAL spacing", keyword: "ial-spacing" },
    LintingRule { num: 17, description: "Normalize fenced code block language identifier spacing", keyword: "code-lang-spacing" },
    LintingRule { num: 18, description: "Normalize reference-style link definition spacing", keyword: "ref-link-spacing" },
    LintingRule { num: 19, description: "Normalize task list checkbox (lowercase x)", keyword: "task-checkbox" },
    LintingRule { num: 20, description: "Normalize blockquote spacing", keyword: "blockquote-spacing" },
    LintingRule { num: 21, description: "Normalize display math block spacing", keyword: "math-spacing" },
    LintingRule { num: 22, description: "Normalize table formatting", keyword: "table-format" },
    LintingRule { num: 23, description: "Normalize emoji names (spellcheck and correct)", keyword: "emoji-spellcheck" },
    LintingRule { num: 24, description: "Normalize typography (curly quotes, dashes, ellipses, guillemets). Sub-keywords: em-dash, guillemet", keyword: "typography" },
    LintingRule { num: 25, description: "Normalize bold/italic markers (bold: __, italic: *)", keyword: "bold-italic" },
    LintingRule { num: 26, description: "Normalize list markers (renumber ordered lists, standardize bullet markers by level)", keyword: "list-markers" },
    LintingRule { num: 27, description: "Reset ordered lists to start at 1 (if disabled, preserve starting number)", keyword: "list-reset" },
];

fn parse_skip_rules(skip_str: &str) -> Result<(HashSet<u8>, bool, bool), String> {
    let mut skip_rules = HashSet::new();
    let mut skip_em_dash = false;
    let mut skip_guillemet = false;

    let values: Vec<&str> = skip_str.split(',').map(|s| s.trim()).collect();

    for value in values {
        // Group keywords that map to multiple underlying rules
        if value == "code-block-newlines" {
            // Skip both before/after code block rules
            skip_rules.insert(6);
            skip_rules.insert(7);
            continue;
        }
        if value == "display-math-newlines" {
            // Skip display math block spacing and surrounding newlines
            skip_rules.insert(21);
            continue;
        }

        if value == "em-dash" {
            skip_em_dash = true;
            continue;
        }
        if value == "guillemet" {
            skip_guillemet = true;
            continue;
        }

        if let Ok(rule_num) = value.parse::<u8>() {
            if LINTING_RULES.iter().any(|r| r.num == rule_num) {
                skip_rules.insert(rule_num);
            } else {
                return Err(format!("Invalid rule number: {}", rule_num));
            }
        } else if let Some(rule) = LINTING_RULES.iter().find(|r| r.keyword == value) {
            skip_rules.insert(rule.num);
        } else {
            return Err(format!("Invalid keyword: {}", value));
        }
    }

    Ok((skip_rules, skip_em_dash, skip_guillemet))
}

#[derive(Debug, Deserialize)]
struct Config {
    width: Option<usize>,
    overwrite: Option<bool>,
    rules: Option<RulesConfig>,
}

#[derive(Debug, Deserialize)]
struct RulesConfig {
    skip: Option<RulesList>,
    include: Option<RulesList>,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum RulesList {
    All,
    List(Vec<String>),
}

fn get_config_path() -> (PathBuf, Option<PathBuf>) {
    // Determine config directory
    let config_dir = if let Some(xdg_config) = std::env::var_os("XDG_CONFIG_HOME") {
        PathBuf::from(xdg_config)
    } else {
        let mut home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
        home.push(".config");
        home
    };
    let config_dir = config_dir.join("md-fixup");

    // Try config.yml first, then config.yaml
    let config_file = if config_dir.join("config.yml").exists() {
        Some(config_dir.join("config.yml"))
    } else if config_dir.join("config.yaml").exists() {
        Some(config_dir.join("config.yaml"))
    } else {
        None
    };

    (config_dir, config_file)
}

fn init_config_file(force: bool, local: bool) -> Option<PathBuf> {
    let config_file = if local {
        // Local config: .md-fixup in current directory
        PathBuf::from(".md-fixup")
    } else {
        // Global config: ~/.config/md-fixup/config.yml
        let (config_dir, existing_file) = get_config_path();
        if existing_file.is_some() && !force {
            return None;
        }
        // Create config directory if it doesn't exist
        if fs::create_dir_all(&config_dir).is_err() {
            return None;
        }
        config_dir.join("config.yml")
    };

    // Don't overwrite existing local config unless forced
    if local && config_file.exists() && !force {
        return None;
    }

    // Generate config with all rules enabled
    let all_rules: Vec<String> = LINTING_RULES.iter()
        .map(|r| r.keyword.to_string())
        .collect();

    // Build YAML content manually (simpler than using serde_yaml::Value)
    let mut yaml_content = format!("width: {}\n", DEFAULT_WRAP_WIDTH);
    yaml_content.push_str("overwrite: false\n");
    yaml_content.push_str("rules:\n");
    yaml_content.push_str("  skip: all\n");
    yaml_content.push_str("  include:\n");
    for rule in all_rules {
        yaml_content.push_str(&format!("    - {}\n", rule));
    }

    fs::write(&config_file, yaml_content).ok()?;
    Some(config_file)
}

fn load_config() -> Option<Config> {
    // Check for local config first (.md-fixup in current directory)
    let local_config = PathBuf::from(".md-fixup");
    if local_config.exists() {
        if let Ok(content) = fs::read_to_string(&local_config) {
            if let Ok(config) = serde_yaml::from_str(&content) {
                return Some(config);
            }
        }
    }

    // Fall back to global config
    let (_config_dir, config_file) = get_config_path();
    let config_file = config_file?;
    let content = fs::read_to_string(config_file).ok()?;
    serde_yaml::from_str(&content).ok()
}

fn parse_config_rules(config: &Config) -> HashSet<u8> {
    let mut skip_rules = HashSet::new();

    if let Some(rules_config) = &config.rules {
        // Handle skip: all + include: [...] pattern
        if let Some(RulesList::All) = rules_config.skip.as_ref() {
            // Start with all rules disabled
            skip_rules = LINTING_RULES.iter().map(|r| r.num).collect();

            // Then include the specified rules
            if let Some(RulesList::List(include_list)) = &rules_config.include {
                for item in include_list {
                    if item == "code-block-newlines" {
                        skip_rules.remove(&6);
                        skip_rules.remove(&7);
                    } else if item == "display-math-newlines" {
                        skip_rules.remove(&21);
                    } else if let Some(rule) = LINTING_RULES.iter().find(|r| r.keyword == item.as_str()) {
                        skip_rules.remove(&rule.num);
                    } else if let Ok(rule_num) = item.parse::<u8>() {
                        if LINTING_RULES.iter().any(|r| r.num == rule_num) {
                            skip_rules.remove(&rule_num);
                        }
                    }
                }
            }
        }
        // Handle simple skip: [...] pattern
        else if let Some(RulesList::List(skip_list)) = &rules_config.skip {
            for item in skip_list {
                if item == "code-block-newlines" {
                    skip_rules.insert(6);
                    skip_rules.insert(7);
                } else if item == "display-math-newlines" {
                    skip_rules.insert(21);
                } else if let Some(rule) = LINTING_RULES.iter().find(|r| r.keyword == item.as_str()) {
                    skip_rules.insert(rule.num);
                } else if let Ok(rule_num) = item.parse::<u8>() {
                    if LINTING_RULES.iter().any(|r| r.num == rule_num) {
                        skip_rules.insert(rule_num);
                    }
                }
            }
        }

        // Handle include: [...] pattern (without skip: all)
        if let Some(RulesList::List(include_list)) = &rules_config.include {
            if !matches!(rules_config.skip, Some(RulesList::All)) {
                for item in include_list {
                    if item == "code-block-newlines" {
                        skip_rules.remove(&6);
                        skip_rules.remove(&7);
                    } else if item == "display-math-newlines" {
                        skip_rules.remove(&21);
                    } else if let Some(rule) = LINTING_RULES.iter().find(|r| r.keyword == item.as_str()) {
                        skip_rules.remove(&rule.num);
                    } else if let Ok(rule_num) = item.parse::<u8>() {
                        if LINTING_RULES.iter().any(|r| r.num == rule_num) {
                            skip_rules.remove(&rule_num);
                        }
                    }
                }
            }
        }
    }

    skip_rules
}

fn process_file(
    filepath: &str,
    wrap_width: usize,
    overwrite: bool,
    skip_rules: &HashSet<u8>,
    skip_em_dash: bool,
    skip_guillemet: bool,
) -> Result<bool, String> {
    let content = fs::read_to_string(filepath)
        .map_err(|e| format!("Error reading {}: {}", filepath, e))?;

    let lines: Vec<String> = content.lines().map(|l| l.to_string()).collect();
    let mut output: Vec<String> = Vec::new();
    let mut in_code_block = false;
    let mut in_math_block = false;
    let mut i = 0;
    let mut changes_made = false;
    let mut consecutive_blank_lines = 0;
    let mut current_list_indent_unit: Option<usize> = None;
    let mut list_context_stack: Vec<ListContext> = Vec::new();
    let valid_emoji_set = valid_emoji_names_set();

    while i < lines.len() {
        let mut line = lines[i].clone();

        // Normalize line endings to Unix (\n)
        if !skip_rules.contains(&1) {
            if line.ends_with("\r\n") {
                line = line.trim_end_matches("\r\n").to_string() + "\n";
                changes_made = true;
            } else if line.ends_with('\r') {
                line = line.trim_end_matches('\r').to_string() + "\n";
                changes_made = true;
            } else if !line.ends_with('\n') {
                line.push('\n');
                changes_made = true;
            }
        }

        // Track code block state
        if is_code_block(&line) {
            if !skip_rules.contains(&17) {
                let normalized_code = normalize_fenced_code_lang(&line);
                if normalized_code != line {
                    line = normalized_code;
                    changes_made = true;
                }
            }

            // Determine if this is the opening or closing fence before toggling
            let is_opening = !in_code_block;
            in_code_block = !in_code_block;

            // Ensure blank line before code block (unless at start)
            if !skip_rules.contains(&6) && is_opening {
                if let Some(last_line) = output.last() {
                    if !last_line.trim().is_empty() {
                        let last = last_line.trim();
                        if !last.starts_with("```") {
                            output.push("\n".to_string());
                            changes_made = true;
                        }
                    }
                }
            }

            // If this is the closing fence, remove trailing blank lines inside the code block
            if !is_opening {
                while let Some(last_line) = output.last() {
                    if last_line.trim().is_empty() {
                        // Do not remove the opening fence if the block was empty
                        if last_line.trim().starts_with("```") {
                            break;
                        }
                        output.pop();
                        changes_made = true;
                    } else {
                        break;
                    }
                }
            }

            output.push(line.clone());

            if !skip_rules.contains(&7) {
                if !in_code_block && i + 1 < lines.len() && !lines[i + 1].trim().is_empty() {
                    output.push("\n".to_string());
                    changes_made = true;
                }
            }

            i += 1;
            continue;
        }

        // Don't process inside code blocks
        if in_code_block {
            output.push(line);
            consecutive_blank_lines = 0;
            i += 1;
            continue;
        }

        // Normalize emoji names
        if !skip_rules.contains(&23) {
            if !in_math_block {
                let normalized_emoji = normalize_emoji_names(&line, &valid_emoji_set);
                if normalized_emoji != line {
                    line = normalized_emoji;
                    changes_made = true;
                }
            }
        }

        // Normalize typography
        if !skip_rules.contains(&24) {
            let normalized_typography = normalize_typography(&line, skip_em_dash, skip_guillemet);
            if normalized_typography != line {
                line = normalized_typography;
                changes_made = true;
            }
        }

        // Normalize bold/italic markers
        if !skip_rules.contains(&25) {
            let normalized_bold_italic = normalize_bold_italic(&line);
            if normalized_bold_italic != line {
                line = normalized_bold_italic;
                changes_made = true;
            }
        }

        // Normalize IAL spacing
        if !skip_rules.contains(&16) {
            let normalized_ial = normalize_ial_spacing(&line);
            if normalized_ial != line {
                line = normalized_ial;
                changes_made = true;
            }
        }

        // Normalize reference-style link definitions
        if !skip_rules.contains(&18) {
            let normalized_ref = normalize_reference_link(&line);
            if normalized_ref != line {
                line = normalized_ref;
                changes_made = true;
            }
        }

        // Handle display math blocks ($$...$$)
        if !skip_rules.contains(&21) {
            let stripped_line = line.trim();
            if stripped_line == "$$" {
                let is_opening = !in_math_block;
                in_math_block = !in_math_block;

                if is_opening {
                    // Ensure blank line before opening $$ (unless at start)
                    if let Some(last_line) = output.last() {
                        if !last_line.trim().is_empty() {
                            output.push("\n".to_string());
                            changes_made = true;
                        }
                    }
                    output.push("$$\n".to_string());
                } else {
                    // Closing $$ - remove trailing space from previous line
                    if let Some(last) = output.last_mut() {
                        if last.trim_end().ends_with(' ') {
                            let trimmed = last.trim_end().to_string() + "\n";
                            *last = trimmed;
                            changes_made = true;
                        }
                    }
                    output.push("$$\n".to_string());

                    // Ensure blank line after math block if next line is non-empty
                    if i + 1 < lines.len() && !lines[i + 1].trim().is_empty() {
                        output.push("\n".to_string());
                        changes_made = true;
                    }
                }
                i += 1;
                continue;
            } else if in_math_block {
                let is_first_line = !output.is_empty() && output[output.len() - 1].trim_end() == "$$";
                let is_last_line = i + 1 < lines.len() && lines[i + 1].trim() == "$$";

                if is_first_line {
                    let normalized = line.trim_start().to_string();
                    let normalized = if normalized.ends_with('\n') {
                        normalized
                    } else {
                        normalized + "\n"
                    };
                    output.push(normalized.clone());
                    if line != normalized {
                        changes_made = true;
                    }
                } else if is_last_line {
                    let normalized = line.trim_end().to_string();
                    let normalized = if normalized.ends_with('\n') {
                        normalized
                    } else {
                        normalized + "\n"
                    };
                    output.push(normalized.clone());
                    if line != normalized {
                        changes_made = true;
                    }
                } else {
                    output.push(line.clone());
                }
                i += 1;
                continue;
            } else {
                let normalized_math = normalize_math_spacing(&line, in_code_block);
                if normalized_math != line {
                    line = normalized_math;
                    changes_made = true;
                }
            }
        }

        let stripped = line.trim();

        // Handle table normalization
        if !skip_rules.contains(&22) {
            if stripped.contains('|') && !is_code_block(&line) && !in_math_block {
                let mut table_lines = Vec::new();
                let table_start = i;
                let mut j = i;

                while j < lines.len() {
                    let current_line = &lines[j];
                    let current_stripped = current_line.trim();

                    if current_stripped.is_empty() {
                        break;
                    }

                    if is_code_block(current_line) {
                        break;
                    }

                    if current_stripped.contains('|') {
                        table_lines.push(current_line.clone());
                        j += 1;
                    } else {
                        break;
                    }
                }

                if table_lines.len() >= 2 {
                    if let Some(normalized_table) = normalize_table_formatting(&table_lines) {
                        for (k, norm_line) in normalized_table.iter().enumerate() {
                            if table_start + k < lines.len() {
                                if lines[table_start + k] != *norm_line {
                                    changes_made = true;
                                }
                            }
                        }
                        output.extend(normalized_table);
                        i = j;
                        consecutive_blank_lines = 0;
                        continue;
                    }
                }
            }
        }

        // Handle headlines
        if is_headline(&line) {
            // Clear list context when encountering a headline (non-list element)
            list_context_stack.clear();
            current_list_indent_unit = None;

            if !skip_rules.contains(&4) {
                let normalized = normalize_headline_spacing(&line);
                if normalized != line {
                    line = normalized;
                    changes_made = true;
                }
            }

            output.push(line.clone());

            if !skip_rules.contains(&5) {
                if i + 1 < lines.len() {
                    let next_line = &lines[i + 1];
                    if !next_line.trim().is_empty()
                        && !is_headline(next_line)
                        && !is_code_block(next_line)
                    {
                        if !next_line.trim().is_empty() {
                            output.push("\n".to_string());
                            changes_made = true;
                        }
                    }
                }
            }

            consecutive_blank_lines = 0;
            i += 1;
            continue;
        }

        // Handle horizontal rules
        if is_horizontal_rule(&line) {
            // Clear list context when encountering a horizontal rule (non-list element)
            list_context_stack.clear();
            current_list_indent_unit = None;

            if !skip_rules.contains(&10) {
                if !output.is_empty() && !output[output.len() - 1].trim().is_empty() {
                    output.push("\n".to_string());
                    changes_made = true;
                }
            }

            output.push(line.clone());

            if !skip_rules.contains(&11) {
                if i + 1 < lines.len() && !lines[i + 1].trim().is_empty() {
                    output.push("\n".to_string());
                    changes_made = true;
                }
            }

            consecutive_blank_lines = 0;
            i += 1;
            continue;
        }

        // Don't wrap certain lines
        if should_preserve_line(&line) {
            output.push(line);
            i += 1;
            continue;
        }

        // Handle list items
        if is_list_item(&line) {
            if !skip_rules.contains(&19) {
                let normalized_task = normalize_task_checkbox(&line);
                if normalized_task != line {
                    line = normalized_task;
                    changes_made = true;
                }
            }

            if current_list_indent_unit.is_none() {
                current_list_indent_unit = Some(detect_list_indent_unit(&lines, i));
            }

            // Check for CommonMark interrupted list: bullet <-> numbered at same level
            // Do this BEFORE normalization so we can detect the original marker types
            let line_no_nl = line.trim_end_matches('\n');
            let re_current_orig = Regex::new(r"^(\s*)([-*+]|\d+\.)(\s*)(.*)$").unwrap();
            if let Some(caps) = re_current_orig.captures(line_no_nl) {
                let current_indent_str = caps.get(1).unwrap().as_str();
                let current_marker_orig = caps.get(2).unwrap().as_str();
                let current_is_numbered_orig = Regex::new(r"^\d+\.$").unwrap().is_match(current_marker_orig);

                // Check previous output line (skip blank lines)
                let mut prev_line: Option<&String> = None;
                for j in (0..output.len()).rev() {
                    if !output[j].trim().is_empty() {
                        prev_line = Some(&output[j]);
                        break;
                    }
                }


                if let Some(prev) = prev_line {
                    if is_list_item(prev) {
                        let prev_no_nl = prev.trim_end_matches('\n');
                        let re_prev = Regex::new(r"^(\s*)([-*+]|\d+\.)(\s*)(.*)$").unwrap();
                        if let Some(prev_caps) = re_prev.captures(prev_no_nl) {
                            let prev_indent_str = prev_caps.get(1).unwrap().as_str();
                            let prev_marker = prev_caps.get(2).unwrap().as_str();
                            let prev_is_numbered = Regex::new(r"^\d+\.$").unwrap().is_match(prev_marker);

                            // Compare normalized indentation levels, not raw character counts
                            let indent_unit = current_list_indent_unit.unwrap_or_else(|| detect_list_indent_unit(&lines, i));
                            let prev_level = get_list_level(prev_indent_str, indent_unit);
                            let current_level = get_list_level(current_indent_str, indent_unit);

                            // If same level and marker type changed (bullet <-> numbered): split the list
                            // BUT only at top-level (level 0) - nested lists should just convert markers
                            if prev_level == current_level && prev_is_numbered != current_is_numbered_orig && current_level == 0 {
                                // Remove context for this level so the new list type starts fresh
                                let interrupt_level = current_level;
                                list_context_stack.retain(|ctx| ctx.level != interrupt_level);
                                // Insert: blank line, HTML comment, blank line
                                output.push("\n".to_string());
                                output.push("<!-- -->\n".to_string());
                                output.push("\n".to_string());
                                changes_made = true;
                            }
                        }
                    }
                }
            }

            // Normalize list markers (renumber ordered lists, standardize bullet markers)
            // Do this before converting spaces to tabs so level calculation works correctly
            if !skip_rules.contains(&26) {
                let indent_unit = current_list_indent_unit.unwrap_or_else(|| detect_list_indent_unit(&lines, i));

                // Don't clear list context on blank lines - blank lines are allowed within lists in CommonMark
                // Only clear if the next non-blank line after a blank line is NOT a list item or is at a different level
                // This is handled when we encounter non-list elements (paragraphs, headings, etc.)

                let skip_list_reset = skip_rules.contains(&27);
                let (normalized_line, marker_changed) = normalize_list_markers(&line, &mut list_context_stack, indent_unit, skip_list_reset);
                // Always use normalized_line to ensure context stack is updated correctly
                line = normalized_line;
                if marker_changed {
                    changes_made = true;
                }
            }

            if !skip_rules.contains(&12) {
                let new_line = spaces_to_tabs_for_list(&line, current_list_indent_unit.unwrap());
                if new_line != line {
                    line = new_line;
                    changes_made = true;
                }
            }

            let list_indent = get_list_indent(&line);

            if !skip_rules.contains(&8) {
                if !output.is_empty() && !output[output.len() - 1].trim().is_empty() {
                    let prev_line = &output[output.len() - 1];
                    if !is_list_item(prev_line) {
                        let prev_stripped = prev_line.trim();
                        if !prev_stripped.starts_with('>') && !prev_stripped.starts_with('#') {
                            output.push("\n".to_string());
                            changes_made = true;
                        }
                    }
                }
            }

            let re = Regex::new(r"^(\s*)([-*+]|\d+\.)(\s*)(.*)$").unwrap();
            if let Some(caps) = re.captures(&line) {
                let indent = caps.get(1).unwrap().as_str().to_string();
                let marker = caps.get(2).unwrap().as_str().to_string();
                let marker_space_str = caps.get(3).unwrap().as_str();
                let content = caps.get(4).unwrap().as_str().to_string();

                let (marker_space, needs_fix) = if !skip_rules.contains(&13) {
                    if marker_space_str != " " {
                        (" ".to_string(), true)
                    } else {
                        (marker_space_str.to_string(), false)
                    }
                } else {
                    (marker_space_str.to_string(), false)
                };

                if needs_fix {
                    line = format!("{}{}{}{}", indent, marker, marker_space, content);
                    if !line.ends_with('\n') {
                        line.push('\n');
                    }
                    changes_made = true;
                }

                let prefix = format!("{}{}{}", indent, marker, marker_space);

                if !skip_rules.contains(&14) {
                    if line.trim_end().chars().count() > wrap_width && !content.is_empty() {
                        let wrapped = wrap_text(&content, wrap_width, &prefix);
                        for (j, wrapped_line) in wrapped.iter().enumerate() {
                            if j > 0 {
                                let cont_indent = " ".repeat(prefix.chars().count());
                                let cont_line = format!("{}{}", cont_indent, &wrapped_line[prefix.chars().count()..]);
                                output.push(format!("{}\n", cont_line));
                            } else {
                                output.push(format!("{}\n", wrapped_line));
                            }
                        }
                        changes_made = true;
                    } else {
                        output.push(line.clone());
                    }
                } else {
                    output.push(line.clone());
                }
            } else {
                output.push(line.clone());
            }

            if !skip_rules.contains(&9) {
                if i + 1 < lines.len() {
                    let next_line = &lines[i + 1];
                    if !next_line.trim().is_empty() && !is_list_item(next_line) {
                        current_list_indent_unit = None;
                        list_context_stack.clear();
                        let next_indent = if next_line.trim().is_empty() {
                            0
                        } else {
                            get_list_indent(next_line)
                        };
                        if next_indent <= list_indent && !next_line.trim().starts_with('>') {
                            // Check if we need a blank line - handled in next iteration
                        }
                    } else if next_line.trim().is_empty() {
                        // Blank line - might be end of list
                    }
                } else {
                    current_list_indent_unit = None;
                    list_context_stack.clear();
                }
            } else {
                if i + 1 < lines.len() {
                    let next_line = &lines[i + 1];
                    if !next_line.trim().is_empty() && !is_list_item(next_line) {
                        current_list_indent_unit = None;
                        list_context_stack.clear();
                    } else {
                        current_list_indent_unit = None;
                        list_context_stack.clear();
                    }
                } else {
                    current_list_indent_unit = None;
                    list_context_stack.clear();
                }
            }

            i += 1;
            continue;
        }

        // Handle blockquotes
        if is_blockquote(&line) {
            // Clear list context when encountering a blockquote (non-list element)
            list_context_stack.clear();
            current_list_indent_unit = None;

            if !skip_rules.contains(&20) {
                let normalized_bq = normalize_blockquote_spacing(&line);
                if normalized_bq != line {
                    line = normalized_bq;
                    changes_made = true;
                }
            }

            let prefix = get_blockquote_prefix(&line);
            let content = line[prefix.len()..].trim_start();

            if !skip_rules.contains(&14) {
                if !content.is_empty() && line.trim_end().chars().count() > wrap_width {
                    let wrapped = wrap_text(content, wrap_width, &format!("{} ", prefix));
                    for (j, wrapped_line) in wrapped.iter().enumerate() {
                        if j > 0 {
                            let cont_line = format!("{} {}", prefix, &wrapped_line[(prefix.len() + 1)..]);
                            output.push(format!("{}\n", cont_line));
                        } else {
                            output.push(format!("{}\n", wrapped_line));
                        }
                    }
                    changes_made = true;
                } else {
                    output.push(line.clone());
                }
            } else {
                output.push(line.clone());
            }

            i += 1;
            continue;
        }

        // Regular paragraph text
        if !stripped.is_empty() {
            // Clear list context when encountering paragraph text (non-list element)
            // But only if this is not indented (which would be part of a list item)
            let line_indent = line.len() - line.trim_start().len();
            if line_indent == 0 || !is_list_item(&line) {
                list_context_stack.clear();
                current_list_indent_unit = None;
            }

            if !output.is_empty() && !output[output.len() - 1].trim().is_empty() {
                let prev = output[output.len() - 1].trim();
                if prev.starts_with("```") || is_list_item(&output[output.len() - 1]) {
                    output.push("\n".to_string());
                    changes_made = true;
                }
            }

            if !skip_rules.contains(&2) {
                let normalized = normalize_trailing_whitespace(&line);
                if normalized != line {
                    line = normalized;
                    changes_made = true;
                }
            }

            if !skip_rules.contains(&14) {
                if line.trim_end().chars().count() > wrap_width {
                    let stripped = line.trim();
                    let wrapped = wrap_text(stripped, wrap_width, "");
                    for wrapped_line in wrapped {
                        output.push(format!("{}\n", wrapped_line));
                    }
                    changes_made = true;
                } else {
                    output.push(line.clone());
                }
            } else {
                output.push(line.clone());
            }

            consecutive_blank_lines = 0;
        } else {
            // Handle blank lines - collapse multiple (max 1 consecutive, except in code blocks)
            if !skip_rules.contains(&3) {
                consecutive_blank_lines += 1;
                if consecutive_blank_lines <= 1 {
                    output.push("\n".to_string());
                } else {
                    // More than 1 consecutive blank line - skip it (collapse)
                    changes_made = true;
                }
            } else {
                output.push("\n".to_string());
                consecutive_blank_lines = 0;
            }
        }

        i += 1;
    }

    // Ensure exactly one blank line at end of file
    if !skip_rules.contains(&15) {
        while !output.is_empty() && output[output.len() - 1].trim().is_empty() {
            output.pop();
            changes_made = true;
        }
        if !output.is_empty() && !output[output.len() - 1].trim().is_empty() {
            output.push("\n".to_string());
            changes_made = true;
        }
    }

    // Write output
    if overwrite {
        if changes_made {
            let output_str = output.join("");
            fs::write(filepath, output_str)
                .map_err(|e| format!("Error writing {}: {}", filepath, e))?;
            Ok(true)
        } else {
            Ok(false)
        }
    } else {
        let output_str = output.join("");
        print!("{}", output_str);
        Ok(changes_made)
    }
}

fn find_markdown_files() -> Vec<String> {
    let mut files = Vec::new();
    let current_dir = Path::new(".");

    fn walk_dir(dir: &Path, files: &mut Vec<String>) {
        if let Ok(entries) = fs::read_dir(dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_dir() {
                    let path_str = path.to_string_lossy();
                    if path_str.contains("vendor")
                        || path_str.contains("build")
                        || path_str.contains(".git")
                        || path_str.contains("node_modules")
                    {
                        continue;
                    }
                    walk_dir(&path, files);
                } else if path.extension().and_then(|s| s.to_str()) == Some("md") {
                    if let Some(path_str) = path.to_str() {
                        files.push(path_str.to_string());
                    }
                }
            }
        }
    }

    walk_dir(current_dir, &mut files);
    files
}

fn main() {
    let rules_list: String = LINTING_RULES
        .iter()
        .map(|r| format!("  {}. {} ({})", r.num, r.description, r.keyword))
        .collect::<Vec<_>>()
        .join("\n");

    let matches = Command::new("md-fixup")
        .about("Markdown linter that wraps text and ensures proper formatting")
        .disable_version_flag(true)
        .arg(
            Arg::new("version")
                .short('v')
                .long("version")
                .help("Print version information")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("width")
                .short('w')
                .long("width")
                .value_name("X")
                .help(format!("Text wrap width in characters (default: {}, or from config file)", DEFAULT_WRAP_WIDTH))
                .value_parser(clap::value_parser!(usize)),
        )
        .arg(
            Arg::new("overwrite")
                .short('o')
                .long("overwrite")
                .help("Overwrite files in place. If not specified, output to STDOUT (or use config file setting).")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("skip")
                .short('s')
                .long("skip")
                .value_name("X[,X]")
                .help("Comma-separated list of rule numbers or keywords to skip")
        )
        .arg(
            Arg::new("init-config")
                .long("init-config")
                .help("Initialize the global config file with all rules enabled by name")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("init-config-local")
                .long("init-config-local")
                .help("Initialize a local config file with all rules enabled by name (creates .md-fixup in current directory)")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("files")
                .help("Markdown files to process")
                .num_args(0..)
        )
        .after_help(format!(
            "\
Available linting rules (use with --skip):
{}

Group keywords (expand to multiple rules):
  - code-block-newlines: Skip all code block newline rules (6,7)
  - display-math-newlines: Skip display math newline handling (21)

Sub-keywords (for specific rule features):
  - em-dash: Skip em dash conversion (use with typography rule)
  - guillemet: Skip guillemet conversion (use with typography rule)

Examples:
  md-fixup file.md
  md-fixup --width 80 file1.md file2.md
  md-fixup --width 72 *.md
  find . -name \"*.md\" | md-fixup --width 100
  md-fixup  # Processes all .md files in current directory
  md-fixup --skip 2,3 file.md  # Skip trailing whitespace and blank line collapse
  md-fixup --skip wrap,end-newline file.md  # Skip wrapping and end newline (using keywords)
  md-fixup --init-config  # Create initial global config file with all rules enabled
",
            rules_list
        ))
        .get_matches();

    // Handle --version/-v flag
    if matches.get_flag("version") {
        println!("md-fixup v{}", VERSION);
        std::process::exit(0);
    }

    // Handle --init-config flag
    if matches.get_flag("init-config") {
        let (_config_dir, existing_config) = get_config_path();
        if let Some(existing) = existing_config {
            if !atty::is(atty::Stream::Stdin) {
                eprintln!("Config file already exists at: {}", existing.display());
                eprintln!("Refusing to overwrite config in non-interactive mode.");
                std::process::exit(1);
            }
            eprintln!("Config file already exists at: {}", existing.display());
            eprint!("Overwrite existing config file? [y/N]: ");
            use std::io::Write;
            io::stderr().flush().ok();
            let mut input = String::new();
            if io::stdin().read_line(&mut input).is_err() {
                eprintln!("Failed to read input. Aborting.");
                std::process::exit(1);
            }
            let resp = input.trim().to_lowercase();
            if resp != "y" && resp != "yes" {
                eprintln!("Aborted. Existing config file left unchanged.");
                std::process::exit(1);
            }
        }
        match init_config_file(true, false) {
            Some(config_file) => {
                eprintln!("Created config file at: {}", config_file.display());
                eprintln!("Edit this file to customize which rules are enabled.");
                std::process::exit(0);
            }
            None => {
                eprintln!("Error: Could not create config file.");
                std::process::exit(1);
            }
        }
    }

    // Handle --init-config-local flag
    if matches.get_flag("init-config-local") {
        let local_config = PathBuf::from(".md-fixup");
        if local_config.exists() {
            if !atty::is(atty::Stream::Stdin) {
                eprintln!("Config file already exists at: {}", local_config.canonicalize().unwrap_or(local_config.clone()).display());
                eprintln!("Refusing to overwrite config in non-interactive mode.");
                std::process::exit(1);
            }
            eprintln!("Config file already exists at: {}", local_config.canonicalize().unwrap_or(local_config.clone()).display());
            eprint!("Overwrite existing config file? [y/N]: ");
            use std::io::Write;
            io::stderr().flush().ok();
            let mut input = String::new();
            if io::stdin().read_line(&mut input).is_err() {
                eprintln!("Failed to read input. Aborting.");
                std::process::exit(1);
            }
            let resp = input.trim().to_lowercase();
            if resp != "y" && resp != "yes" {
                eprintln!("Aborted. Existing config file left unchanged.");
                std::process::exit(1);
            }
        }
        match init_config_file(true, true) {
            Some(config_file) => {
                eprintln!("Created local config file at: {}", config_file.canonicalize().unwrap_or(config_file.clone()).display());
                eprintln!("Edit this file to customize which rules are enabled.");
                std::process::exit(0);
            }
            None => {
                eprintln!("Error: Could not create config file.");
                std::process::exit(1);
            }
        }
    }

    // Auto-init config if it doesn't exist and running interactively
    let (_config_dir, config_file) = get_config_path();
    if config_file.is_none() && atty::is(atty::Stream::Stdout) {
        if let Some(config_file) = init_config_file(false, false) {
            eprintln!("Created initial config file at: {}", config_file.display());
            eprintln!("Edit this file to customize which rules are enabled.");
        }
    }

    // Load config file (if available)
    let config = load_config();

    // Merge config with CLI args (CLI overrides config)
    let wrap_width = matches
        .get_one::<usize>("width")
        .copied()
        .or_else(|| config.as_ref().and_then(|c| c.width))
        .unwrap_or(DEFAULT_WRAP_WIDTH);
    let overwrite = matches.get_flag("overwrite")
        || config.as_ref().and_then(|c| c.overwrite).unwrap_or(false);

    // Start with config skip_rules, then merge CLI skip rules
    let mut skip_rules = if let Some(ref cfg) = config {
        parse_config_rules(cfg)
    } else {
        HashSet::new()
    };

    let skip_str = matches.get_one::<String>("skip");
    let (cli_skip_rules, skip_em_dash, skip_guillemet) = if let Some(skip_str) = skip_str {
        match parse_skip_rules(skip_str) {
            Ok(result) => result,
            Err(e) => {
                eprintln!("{}", e);
                std::process::exit(1);
            }
        }
    } else {
        (HashSet::new(), false, false)
    };

    // Merge CLI skip rules into config skip rules (CLI overrides config)
    skip_rules.extend(cli_skip_rules);

    let mut files: Vec<String> = if let Some(file_args) = matches.get_many::<String>("files") {
        file_args.map(|s| s.to_string()).collect()
    } else {
        Vec::new()
    };

    // If no files provided, check STDIN or find all markdown files
    if files.is_empty() {
        let stdin = io::stdin();
        let mut stdin_lines = stdin.lock().lines();

        // Read all STDIN content
        let mut stdin_content = String::new();
        let mut stdin_lines_vec = Vec::new();
        let mut has_stdin = false;
        while let Some(Ok(line)) = stdin_lines.next() {
            stdin_content.push_str(&line);
            stdin_content.push('\n');
            stdin_lines_vec.push(line.clone());
            has_stdin = true;
        }

        if has_stdin && !stdin_lines_vec.is_empty() {
            // Check if first line looks like a file path
            let first_line = stdin_lines_vec[0].trim();
            let looks_like_file_path = first_line.contains('/')
                || first_line.contains('\\')
                || first_line.ends_with(".md")
                || Path::new(first_line).exists();

            if looks_like_file_path {
                // Treat as file paths (one per line)
                for line in stdin_lines_vec {
                    let filepath = line.trim();
                    if !filepath.is_empty() {
                        files.push(filepath.to_string());
                    }
                }
            } else {
                // Treat as markdown content - process directly
                use tempfile::NamedTempFile;
                use std::io::Write;

                let mut tmp = match NamedTempFile::new() {
                    Ok(t) => t,
                    Err(e) => {
                        eprintln!("Error creating temporary file: {}", e);
                        std::process::exit(1);
                    }
                };

                if let Err(e) = tmp.write_all(stdin_content.as_bytes()) {
                    eprintln!("Error writing to temporary file: {}", e);
                    std::process::exit(1);
                }

                // Flush to ensure all data is written
                if let Err(e) = tmp.flush() {
                    eprintln!("Error flushing temporary file: {}", e);
                    std::process::exit(1);
                }

                // Convert to TempPath so file persists after dropping the handle
                let tmp_path_obj = tmp.into_temp_path();
                let tmp_path = tmp_path_obj.to_string_lossy().to_string();

                match process_file(&tmp_path, wrap_width, false, &skip_rules, skip_em_dash, skip_guillemet) {
                    Ok(_) => {
                        // process_file already printed to stdout when overwrite=false
                        // tmp_path_obj will be automatically deleted when dropped
                        std::process::exit(0);
                    }
                    Err(e) => {
                        eprintln!("Error processing STDIN: {}", e);
                        std::process::exit(1);
                    }
                }
            }
        }

        // If no STDIN input, find all markdown files
        if files.is_empty() {
            files = find_markdown_files();
        }
    }

    if files.is_empty() {
        eprintln!("No files to process.");
        std::process::exit(1);
    }

    files.sort();

    if overwrite {
        let mut changed_files = Vec::new();
        for filepath in &files {
            match process_file(
                filepath,
                wrap_width,
                true,
                &skip_rules,
                skip_em_dash,
                skip_guillemet,
            ) {
                Ok(true) => changed_files.push(filepath.clone()),
                Ok(false) => {}
                Err(e) => {
                    eprintln!("{}", e);
                }
            }
        }

        if !changed_files.is_empty() {
            println!("Modified {} file(s):", changed_files.len());
            for f in &changed_files {
                println!("  {}", f);
            }
        } else {
            println!("No files needed changes.");
        }
    } else {
        for filepath in &files {
            if let Err(e) = process_file(
                filepath,
                wrap_width,
                false,
                &skip_rules,
                skip_em_dash,
                skip_guillemet,
            ) {
                eprintln!("{}", e);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn process_test_content(content: &str) -> String {
        let mut file = NamedTempFile::new().unwrap();
        write!(file, "{}", content).unwrap();
        file.flush().unwrap();
        let path = file.path().to_str().unwrap();

        let skip_rules = HashSet::new();
        // Use overwrite=true so the file is actually modified
        process_file(path, 60, true, &skip_rules, false, false).unwrap();

        fs::read_to_string(path).unwrap()
    }

    #[test]
    fn test_bullet_marker_normalization_by_level() {
        let input = "* First level\n    - Second level\n        + Third level\n";
        let output = process_test_content(input);
        // Note: spaces will be converted to tabs, so we check for correct markers
        assert!(output.contains("* First level"));
        assert!(output.contains("- Second level") || output.contains("\t- Second level"));
        assert!(output.contains("+ Third level") || output.contains("\t\t+ Third level"));
    }

    #[test]
    fn test_numbered_list_renumbering() {
        let input = "1. First\n3. Third\n5. Fifth\n";
        let output = process_test_content(input);
        assert!(output.contains("1. First"));
        assert!(output.contains("2. Third"));
        assert!(output.contains("3. Fifth"));
        assert!(!output.contains("3. Third"));
        assert!(!output.contains("5. Fifth"));
    }

    #[test]
    fn test_nested_numbered_lists() {
        let input = "1. First\n    1. Nested first\n    3. Nested third\n2. Second\n    1. Another nested first\n";
        let output = process_test_content(input);
        assert!(output.contains("1. First"));
        assert!(output.contains("2. Second"));
        // Nested lists should be renumbered independently
        assert!(output.contains("1. Nested first") || output.contains("\t1. Nested first"));
        assert!(output.contains("2. Nested third") || output.contains("\t2. Nested third"));
        assert!(output.contains("1. Another nested first") || output.contains("\t1. Another nested first"));
    }

    #[test]
    fn test_interrupted_list_detection() {
        let input = "1. First\n2. Second\n3. Third\n* An interrupted list\n";
        let output = process_test_content(input);
        assert!(output.contains("<!-- -->"));
        assert!(output.contains("* An interrupted list"));
        // Should be numbered before interruption
        assert!(output.contains("1. First"));
        assert!(output.contains("2. Second"));
        assert!(output.contains("3. Third"));
    }

    #[test]
    fn test_interrupted_list_reverse() {
        let input = "* First bullet\n- Second bullet\n+ Third bullet\n1. An interrupted numbered list\n";
        let output = process_test_content(input);
        assert!(output.contains("<!-- -->"));
        assert!(output.contains("1. An interrupted numbered list"));
    }

    #[test]
    fn test_bold_normalization() {
        let input = "This is **bold** text.\n";
        let output = process_test_content(input);
        assert!(output.contains("__bold__"));
        assert!(!output.contains("**bold**"));
    }

    #[test]
    fn test_italic_normalization() {
        let input = "This is _italic_ text.\n";
        let output = process_test_content(input);
        assert!(output.contains("*italic*"));
        assert!(!output.contains("_italic_"));
    }

    #[test]
    fn test_bold_italic_nested() {
        let input = "***bold italic***\n";
        let output = process_test_content(input);
        assert!(output.contains("__*bold italic*__"));
    }

    #[test]
    fn test_complex_scenario() {
        let input = "1. List item 1\n    * indented item\n    + another item\n        1. Testing something\n        3. Else\n1. Back to the root\n4. what?\n* An interrupted list\n";
        let output = process_test_content(input);

        // Check list normalization - output shows correct content
        assert!(output.contains("1. List item 1"));
        // "1. Back to the root" should become "2. Back to the root"
        // Output clearly shows "2. Back to the root", check flexibly for tabs/spaces
        assert!(output.contains("Back to the root"), "Missing 'Back to the root': {}", output);
        // Verify renumbering happened - check for "2." pattern (may have tabs before it)
        let re = Regex::new(r"2\.").unwrap();
        let count = re.find_iter(&output).count();
        assert!(count >= 2, "Expected at least 2 instances of '2.', found {}, output: {}", count, output);
        assert!(output.contains("3. what?"));

        // Check nested items (spaces converted to tabs)
        assert!(output.contains("1. Testing something") || output.contains("\t\t1. Testing something"));
        assert!(output.contains("2. Else") || output.contains("\t\t2. Else"));

        // Check interruption
        assert!(output.contains("<!-- -->"));
        assert!(output.contains("* An interrupted list"));
    }

    #[test]
    fn test_get_list_level() {
        assert_eq!(get_list_level("", 2), 0);
        assert_eq!(get_list_level("  ", 2), 1);
        assert_eq!(get_list_level("    ", 2), 2);
        assert_eq!(get_list_level("\t", 2), 1);
        assert_eq!(get_list_level("\t  ", 2), 2);
    }

    #[test]
    fn test_is_list_item() {
        assert!(is_list_item("* Item"));
        assert!(is_list_item("- Item"));
        assert!(is_list_item("+ Item"));
        assert!(is_list_item("1. Item"));
        assert!(is_list_item("   * Item"));
        assert!(is_list_item("\t* Item"));
        assert!(!is_list_item("Not a list"));
        assert!(!is_list_item(""));
    }

    #[test]
    fn test_table_not_wrapped() {
        let input = "| Very long column header | Short | Another header |\n| --- | --- | --- |\n| Cell with very long content that should not wrap | Data | More data |\n";
        // Use narrow width to ensure wrapping would happen for regular text
        let output = process_test_content_with_width(input, 20);

        // Table should be preserved - each row should be on a single line
        let table_lines: Vec<&str> = output.lines().filter(|line| line.contains('|') && !line.trim().is_empty()).collect();

        // All table lines should be single lines (not wrapped)
        for line in &table_lines {
            // Count pipes - should be consistent (table structure preserved)
            let pipe_count = line.matches('|').count();
            assert!(pipe_count > 0, "Table line should contain pipes: {}", line);
        }

        // Verify the long content is still intact
        assert!(output.contains("Very long column header"));
        assert!(output.contains("Cell with very long content that should not wrap"));
    }

    fn process_test_content_with_width(content: &str, width: usize) -> String {
        let mut file = NamedTempFile::new().unwrap();
        write!(file, "{}", content).unwrap();
        file.flush().unwrap();
        let path = file.path().to_str().unwrap();

        let skip_rules = HashSet::new();
        // Use overwrite=true so the file is actually modified
        process_file(path, width, true, &skip_rules, false, false).unwrap();

        fs::read_to_string(path).unwrap()
    }
}
