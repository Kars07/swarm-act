import json
import re

# Mocking the repair_and_parse_json function from service_beta.py
def repair_and_parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        pass
        
    start_idx = text.find('{')
    if start_idx == -1:
        return {}
    
    candidate = text[start_idx:].strip()
    
    end_idx = candidate.rfind('}')
    if end_idx != -1:
        try:
            return json.loads(candidate[:end_idx+1])
        except Exception:
            pass
            
    if candidate.endswith(']'):
        try:
            return json.loads(candidate + '}')
        except Exception:
            pass
            
    open_braces = candidate.count('{')
    close_braces = candidate.count('}')
    open_brackets = candidate.count('[')
    close_brackets = candidate.count(']')
    
    repaired = candidate
    quotes = repaired.count('"')
    if quotes % 2 != 0:
        repaired += '"'
        
    if open_brackets > close_brackets:
        repaired = repaired.rstrip(', \n\r')
        if not repaired.endswith('"') and not repaired.endswith(']'):
            last_quote = repaired.rfind('"')
            if last_quote != -1:
                repaired = repaired[:last_quote+1]
        repaired += ']'
        
    open_braces = repaired.count('{')
    close_braces = repaired.count('}')
    if open_braces > close_braces:
        repaired += '}' * (open_braces - close_braces)
        
    try:
        return json.loads(repaired)
    except Exception as e:
        print(f"Failed to repair JSON: {repaired}. Error: {e}")
        return {}

# Mocking the extract_ranked_items_fallback from service_beta.py
def extract_ranked_items_fallback(text: str) -> list:
    clean_text = text
    for tag in ["</thinking>", "</think>"]:
        if tag in clean_text:
            clean_text = clean_text.split(tag)[-1]
            break
            
    target_area = clean_text
    matches = list(re.finditer(r'"ranked_items"\s*:\s*', clean_text, re.IGNORECASE))
    if matches:
        target_area = clean_text[matches[-1].end():]
        start_bracket = target_area.find('[')
        if start_bracket != -1:
            bracket_count = 0
            end_bracket = -1
            for i, char in enumerate(target_area[start_bracket:]):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_bracket = start_bracket + i
                        break
            if end_bracket != -1:
                target_area = target_area[start_bracket:end_bracket+1]
            else:
                target_area = target_area[start_bracket:]
    else:
        tag_matches = list(re.finditer(r'<ranking_result>', clean_text, re.IGNORECASE))
        if tag_matches:
            target_area = clean_text[tag_matches[-1].end():]
            end_tag = re.search(r'</ranking_result>', target_area, re.IGNORECASE)
            if end_tag:
                target_area = target_area[:end_tag.start()]

    # Extract all possible candidates (both quoted strings and raw words)
    candidates = []
    
    # Extract quoted strings
    quoted = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', target_area)
    # Also extract raw words that look like base64 IDs or preset IDs
    raw_words = re.findall(r'\b[a-zA-Z0-9_\-]{10,40}\b', target_area)
    
    potential_ids = quoted + raw_words
    
    # Filter candidates by length and structure
    for q in potential_ids:
        q_clean = q.strip()
        if not q_clean:
            continue
        # Check if it matches a standard 22-char base64 Yelp ID
        is_base64_id = len(q_clean) == 22 and re.match(r'^[a-zA-Z0-9_\-]{22}$', q_clean)
        # Check if it matches a preset target ID pattern (e.g. ramen_shop_992, cafe_cafe_883)
        is_preset_id = re.match(r'^[a-zA-Z0-9]+_[a-zA-Z0-9_]+_\d+$', q_clean)
        
        if is_base64_id or is_preset_id:
            candidates.append(q_clean)
            
    # Remove duplicates while preserving order
    seen = set()
    final_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            final_candidates.append(c)
            
    return final_candidates

# Mocking extract_and_parse_beta_json from service_beta.py
def extract_and_parse_beta_json(text: str) -> dict:
    clean_text = text
    for tag in ["</thinking>", "</think>"]:
        if tag in clean_text:
            parts = clean_text.split(tag)
            clean_text = parts[-1]
    
    clean_text = clean_text.strip()
    brace_indices = [i for i, char in enumerate(clean_text) if char == '{']
    
    for idx in reversed(brace_indices):
        candidate_area = clean_text[idx:].strip()
        parsed_candidate = repair_and_parse_json(candidate_area)
        if parsed_candidate and "ranked_items" in parsed_candidate:
            return parsed_candidate
            
    return repair_and_parse_json(clean_text)

# Test cases reproducing the monologue truncation / pollution issues
test_cases = [
    # 1. Truncated output ending in the middle of a string item ID in ranked_items, NO </thinking> tag
    {
        "name": "Truncated ranked_items, no </thinking> tag",
        "text": """<thinking>
The user prefers highly rated items at this venue historically. Their ground truth item matches their historical variance for this specific venue type.
The review highlights the Chicken Salad Sandwich as a favorite.
The overall sentiment matches the "comforting" requirement.

3. **Construct Output:**
* Select the ground truth item.
* Format as JSON.

4. **Final Verification:**
* Does the item match the category? Yes (Southern Diner).
* Is the rating consistent? Yes (highly rated historically).
* Ensure no extra fields beyond required keys.

5. **Draft Response:**
```json
{
  "ranked_items": [
    {"rank": 0, "item_id": "Xy6ZDpUQbGcEqfuk7Yt8Bw", "title": "Tenderloin Sandwich", "rating": 4.9}, 
    "hRqCjvMgKd4rVzE_3kxPKA", "uHouVjnTkacJNLIwl14MtQ", "-eLWlMiEb2-XHFnsKdf5Sw", "_o_DMyjm5SItdOjgP_yWEA", "aAdGIK9ewmiWjRsXXB3iVg", "FUEmPFPGHG_7xpS-EqZGkw", "5ruzh2zl7Le2FSfsEsUeBQ", "frISccVgzRbuqobLGAGErQ", "dWoGD-mnt547-lDJInz3Ig", "hTwNVaygiKNOwnuDWBIEWA", "6NS4DHn6shzb4dp8_2n8Bg", "ugSVRAK2zk2gCuTr2agv-Q", "1PYqegXrLtDZHLSCzelEaw", "fNgCYGIIByu4t6Um2am2Kg", "fnweBo2FPvPEERgvThHLEw", "IZ_zXVF-2rMLdTHbhKyPJw"""
    },
    
    # 2. Output with </thinking> tag but truncated array inside JSON
    {
        "name": "Truncated array, with </thinking> tag",
        "text": """<thinking>
The user wants late-night comforting Southern Diner food.
</thinking>
{
  "ranked_items": [
    "Xy6ZDpUQbGcEqfuk7Yt8Bw",
    "hRqCjvMgKd4rVzE_3kxPKA",
    "uHouVjnTkacJNLIwl14MtQ"""
    },

    # 3. Output with monologue pollution like "Alpha Analysis" or "predicted_rating" in thinking block
    {
        "name": "Monologue pollution with single words",
        "text": """<thinking>
We have Alpha Analysis insight. The user prefers highly rated items at this venue historically.
Let's select the ground truth item and recommend some other items.
The target is cafe_cafe_883.
</thinking>
{
  "ranked_items": [
    "Cafe_Zupas", "cafe_cafe_883"
  ]
}"""
    }
]

print("=== Running Parser Diagnostics ===")
for tc in test_cases:
    print(f"\nTest Case: {tc['name']}")
    parsed = {}
    try:
        parsed = extract_and_parse_beta_json(tc['text'])
    except Exception as e:
        print(f"  Parse Error: {e}")
        
    if not parsed or "ranked_items" not in parsed or not parsed["ranked_items"]:
        try:
            fallback = extract_ranked_items_fallback(tc['text'])
            if fallback:
                parsed = {"ranked_items": fallback}
        except Exception as e:
            print(f"  Fallback Error: {e}")
            
    print(f"  Result payload: {parsed}")
