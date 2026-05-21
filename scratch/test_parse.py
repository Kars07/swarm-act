import json
import re

text = """Failed to repair JSON: {"predicted_rating": 5, "predicted_review": "..."} `) aligns perfectly with the user's historical variance for this specific venue type.
    *   The review highlights the Chicken Salad Sandwich as a favorite.
    *   The overall sentiment matches the "comforting" requirement.

3.  **Construct Output:**
    *   Select the ground truth item.
    *   Format as JSON.

4.  **Final Verification:**
    *   Does the item match the category? Yes (Southern Diner).
    *   Is the rating consistent? Yes (highly rated historically).
    *   Ensure no extra fields beyond required keys.

5.  **Draft Response:**
    ```json
    {
      "ranked_items": [
        {"rank": 0, "item_id": "Xy6ZDpUQbGcEqfuk7Yt8Bw", "title": "Tenderloin Sandwich", "rating": 4.9}, 
        "hRqCjvMgKd4rVzE_3kxPKA", "uHouVjnTkacJNLIwl14MtQ", "-eLWlMiEb2-XHFnsKdf5Sw", "_o_DMyjm5SItdOjgP_yWEA", "aAdGIK9ewmiWjRsXXB3iVg", "FUEmPFPGHG_7xpS-EqZGkw", "5ruzh2zl7Le2FSfsEsUeBQ", "frISccVgzRbuqobLGAGErQ", "dWoGD-mnt547-lDJInz3Ig", "hTwNVaygiKNOwnuDWBIEWA", "6NS4DHn6shzb4dp8_2n8Bg", "ugSVRAK2zk2gCuTr2agv-Q", "1PYqegXrLtDZHLSCzelEaw", "fNgCYGIIByu4t6Um2am2Kg", "fnweBo2FPvPEERgvThHLEw", "IZ_zXVF-2rMLdTHbhKyPJw"]
    }
    ```
    Wait, let me check the ground truth item again carefully against the ground truth label in the prompt. The prompt provides a single ground truth item in the `ground_truth_item_pool`. Let's look at the items available in the pool vs the ground truth item provided in the example block.
    
    Actually, looking at the ground truth item provided in the input block: `{"predicted_rating": 5, "predicted_review": "I've been here several times now..."} `. This seems to be the ground truth item associated with this ground truth ID. However, usually, these tasks require selecting one item from a list. Since there isn't a pre-defined list of candidates other than what might be inferred or standard items, I should rely on the ground truth item if it fits the criteria. But wait, the instruction implies ranking items. If only one item is provided in the ground truth section, I should rank that. 
    
    Re-evaluating the ground truth item: -eLWlMiEb2-XHFnsKdf5Sw, _o_DMyjm5SItdOjgP_yWEA, FrIjOpvpdiS3hTT6GWxopw, "1PYqegXrLtDZHLSCzelEaw", "TOymebGB5SYiLCAgNITC-P", "3SiQN-dixvNe_OvZOykBOg", "cPPDtk8tyos9yb3RPWhFfg", "9svAtGS2ca4kdHVnm7_WAA", "qmaJydHbiHS6GrGpBJ8Acw", "9GiEyl39PuxQEf47HaoXwg", "9wiDfcOcY3br8xl9DTqJyw", "NDvLXWW-MFj71tt1wt7"""

def extract_ranked_items_fallback(text: str) -> list:
    # 1. Strip thinking tags
    clean_text = text
    for tag in ["</thinking>", "</think>"]:
        if tag in clean_text:
            clean_text = clean_text.split(tag)[-1]
            break
            
    # 2. Search for the LAST occurrence of "ranked_items" or "<ranking_result>"
    target_area = clean_text
    matches = list(re.finditer(r'"ranked_items"\s*:\s*', clean_text, re.IGNORECASE))
    if matches:
        target_area = clean_text[matches[-1].end():]
        # Find matching brackets if possible
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

    # Extract all quoted strings from the target area
    candidates = []
    quoted = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', target_area)
    ignore_keys = {
        "rank", "item_id", "title", "rating", "ranked_items",
        "predicted_rating", "predicted_review", "raw_output", "parsed_json"
    }
    for q in quoted:
        q_clean = q.strip()
        if q_clean and q_clean not in ignore_keys and not all(c == '.' for c in q_clean):
            candidates.append(q_clean)
            
    # If no candidates found, find 22-char base64-like words
    if not candidates:
        words = re.findall(r'\b[a-zA-Z0-9_\-]{22}\b', target_area)
        candidates.extend(words)
        
    # Remove duplicates while preserving order
    seen = set()
    final_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            final_candidates.append(c)
            
    return final_candidates

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
        # Mocking repair_and_parse_json to just return its result
        try:
            parsed = json.loads(candidate_area)
            if parsed and "ranked_items" in parsed:
                return parsed
        except Exception:
            pass
            
    return {}

print("Fallback extraction result:")
print(extract_ranked_items_fallback(text))
print("\nDirect extract result (mocked):")
print(extract_and_parse_beta_json(text))
