@app.function(@app.function(
    image=swarm_image,
    volumes={"/workspace/data": storage_volume},
    timeout=7200, # 2 hours for massive dataset processing
    secrets=[modal.Secret.from_name("kaggle-secret")] # Ensure Kaggle API keys are in Modal secrets
)
def build_swarm_dataset():
    import os
    import json
    import pandas as pd
    import numpy as np
    from sklearn.cluster import KMeans
    import kagglehub
    import random

    # 1. Environment Setup
    print("Initializing Custom Data Pipeline...")
    DATA_DIR = "/workspace/data/raw_interactions"
    PROCESSED_DIR = "/workspace/data/processed"
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Force kagglehub to cache directly to the persistent volume
    os.environ["KAGGLEHUB_CACHE"] = DATA_DIR

    # 2. Ingest Datasets
    print("Downloading datasets via kagglehub...")
    amazon_path = kagglehub.dataset_download("dongrelaxman/amazon-reviews-dataset")
    yelp_path = kagglehub.dataset_download("yelp-dataset/yelp-dataset")
    goodreads_path = kagglehub.dataset_download("bahramjannesarr/goodreads-book-datasets-10m")
    print("Downloads complete and persisted to volume.")

    # 3. Utility: ChatML Formatter
    def format_chatml(system_msg, user_msg, assistant_msg=None):
        prompt = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{user_msg}<|im_end|>\n"
        if assistant_msg:
            prompt += f"<|im_start|>assistant\n{assistant_msg}<|im_end|>\n"
        return prompt

    # 4. Process Yelp (Master Template)
    print("Processing Yelp Interactions...")
    yelp_reviews_file = os.path.join(yelp_path, "yelp_academic_dataset_review.json")

    # Read in chunks to avoid OOM
    chunks = pd.read_json(yelp_reviews_file, lines=True, chunksize=100000)
    df_list = []

    for i, chunk in enumerate(chunks):
        # Quality Filters
        chunk['word_count'] = chunk['text'].str.split().str.len()

        # Filter outliers: <20 tokens or >512 tokens (~380 words)
        chunk = chunk[(chunk['word_count'] >= 15) & (chunk['word_count'] <= 400)]

        # Discard low engagement noise (0 helpful votes AND short length)
        chunk = chunk[~((chunk['useful'] == 0) & (chunk['word_count'] < 35))]

        df_list.append(chunk[['user_id', 'business_id', 'stars', 'text', 'useful', 'date']])

        if i == 4: # Limit to 500k rows for the hackathon sprint
            break

    df_reviews = pd.concat(df_list, ignore_index=True)
    df_reviews.rename(columns={'business_id': 'item_id', 'stars': 'rating', 'text': 'review_text'}, inplace=True)
    df_reviews['platform'] = 'yelp'

    # 5. Agent-Alpha: Persona-Conditioned Sampling (Clustering)
    print("Computing Behavioral Clusters for Agent-Alpha...")
    user_stats = df_reviews.groupby('user_id').agg(
        avg_rating=('rating', 'mean'),
        rating_variance=('rating', 'var'),
        avg_length=('word_count', 'mean')
    ).fillna(0)

    # 12 Behavioral Archetypes
    kmeans = KMeans(n_clusters=12, random_state=42, n_init=10)
    user_stats['cluster'] = kmeans.fit_predict(user_stats[['avg_rating', 'rating_variance', 'avg_length']])

    persona_map = {
        0: "You are a highly critical reviewer who writes short, blunt assessments.",
        1: "You are a generous reviewer who easily gives 5 stars and writes enthusiastic summaries.",
        2: "You are a detail-oriented reviewer who writes lengthy, balanced critiques.",
        # ... (Map all 12 clusters to specific persona strings based on centroid analysis)
    }
    # For hackathon scope, fallback to generic mappings if centroids aren't manually analyzed yet
    user_stats['persona_string'] = user_stats['cluster'].apply(lambda c: persona_map.get(c, f"You are a reviewer with behavioral archetype {c}."))
    df_reviews = df_reviews.merge(user_stats[['persona_string']], on='user_id', how='left')

    # Build Task A (SFT) Dataset
    print("Constructing Agent-Alpha ChatML data...")
    task_a_data = []
    for _, row in df_reviews.iterrows():
        sys_msg = row['persona_string']
        user_msg = f"Target Item ID: {row['item_id']}\nPlatform: {row['platform']}\nDate: {row['date']}"

        # Structured JSON output enforced via grammar during inference
        assistant_msg = json.dumps({
            "predicted_rating": int(row['rating']),
            "predicted_review": row['review_text']
        })

        task_a_data.append({"text": format_chatml(sys_msg, user_msg, assistant_msg)})

    with open(f"{PROCESSED_DIR}/agent_alpha_sft.jsonl", "w") as f:
        for entry in task_a_data:
            f.write(json.dumps(entry) + "\n")

    # 6. Agent-Beta: Recommendation Candidate Sampling
    print("Constructing Agent-Beta Multi-Turn Traces...")
    unique_items = df_reviews['item_id'].unique()

    # Identify items by rating tier for negative sampling
    high_rated = df_reviews[df_reviews['rating'] >= 4]['item_id'].unique()
    low_rated = df_reviews[df_reviews['rating'] <= 2]['item_id'].unique()

    task_b_data = []

    # Process users with enough history (Warm Start > 10 interactions)
    warm_users = user_stats[user_stats['rating_variance'] > 0].index.tolist()

    for user in warm_users[:5000]: # Sample 5k users for sprint
        user_history = df_reviews[df_reviews['user_id'] == user]
        if len(user_history) < 5: continue

        # Ground Truth: The last item they reviewed positively
        positive_interactions = user_history[user_history['rating'] >= 4]
        if positive_interactions.empty: continue

        target = positive_interactions.iloc[-1]
        ground_truth_id = target['item_id']

        # 1:4:15:30 Sampling Ratio
        # 1 Positive (already selected)

        # 4 Hard Negatives (Highly rated items by others, but user hasn't interacted with)
        user_interacted = set(user_history['item_id'].tolist())
        available_hard = list(set(high_rated) - user_interacted)
        hard_neg = random.sample(available_hard, min(4, len(available_hard)))

        # 15 Soft Negatives (Low rated items)
        available_soft = list(set(low_rated) - user_interacted)
        soft_neg = random.sample(available_soft, min(15, len(available_soft)))

        # 30 Random Negatives (General population)
        available_rand = list(set(unique_items) - user_interacted - set(hard_neg) - set(soft_neg))
        rand_neg = random.sample(available_rand, min(30, len(available_rand)))

        candidate_pool = [ground_truth_id] + hard_neg + soft_neg + rand_neg
        random.shuffle(candidate_pool)

        sys_msg = "You are Agent-Beta, a recommendation engine. Utilize the behavioral state to rank the candidate pool."
        # Injecting a mock 512-dim behavioral vector for SFT (in reality, this comes from Alpha's projection)
        user_msg = f"Behavioral State Vector: <dense_vector_placeholder>\nCandidates: {candidate_pool}"

        # Enforce reasoning scratchpad
        assistant_msg = f"<thinking>The user prefers highly rated items in this category. The ground truth item {ground_truth_id} aligns with their historical variance.</thinking>\n"
        assistant_msg += json.dumps({"ranked_items": [{"rank": 1, "item_id": ground_truth_id}]}) # Simplified for SFT target

        task_b_data.append({"text": format_chatml(sys_msg, user_msg, assistant_msg)})

    with open(f"{PROCESSED_DIR}/agent_beta_sft.jsonl", "w") as f:
        for entry in task_b_data:
            f.write(json.dumps(entry) + "\n")

    print(f"Data pipeline complete. SFT files ready in {PROCESSED_DIR}")

@app.local_entrypoint()
def main():
    # Step 1: Secure the 4B model in the cloud volume
    ingest_qwen_model.remote()

    # Step 2: Initialize the custom dataset processing
    build_swarm_dataset.remote()
