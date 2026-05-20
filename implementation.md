
Here is the accelerated, production-ready 9-day development plan.

### Phase 1: Infrastructure & Data Pipeline (Days 1-2)

Your primary goal here is to establish the Modal environment and curate the high-quality dataset needed for the subsequent stages.

* 
**Modal Environment Setup:** Define a Modal `Image` with Qwen 3.5 3B, Flash Attention 2, and BitsAndBytes NF4 quantization pre-installed.


* 
**Storage Configuration:** Mount a Modal `Volume` to persist the 2.5M interaction raw dataset and the shared Qwen 3.5 3B backbone weights, preventing memory duplication across runs.


* 
**Data Curation (Agent-α):** Build the custom pipeline to cluster users into 12 behavioral archetypes and inject synthetic temporal context (e.g., weather API data).


* 
**Data Curation (Agent-β):** Construct multi-turn session traces utilizing the 1:4:15:30 sampling ratio (1 positive, 4 hard negatives, 15 soft negatives, 30 random negatives) to force fine-grained discriminative reasoning.


* 
**Adapter Architecture:** Implement the multi-LoRA framework, freezing the Embedding and RMSNorm layers to prevent catastrophic forgetting of Qwen's instruction following.



### Phase 2: Supervised Fine-Tuning (SFT) (Days 3-4)

We will build custom SFT scripts to establish the baseline task capabilities for both agents.

* 
**Agent-α Training:** Train for 3 epochs using ChatML format, focusing on a weighted next-token prediction loss where rating tokens receive a 2x weight and generative review tokens receive a 1x weight.


* 
**Agent-β Training:** Train for 3 epochs enforcing a reasoning scratchpad via `<thinking>...<\thinking>` tags.


* 
**Auxiliary Loss Integration:** Add a listwise ranking loss computed on the score logits extracted from Agent-β's output JSON.


* 
**Output Enforcement:** Implement constrained decoding via grammar-based sampling to guarantee both agents emit valid, schema-compliant JSON.



### Phase 3: Preference Alignment (DPO → GRPO) (Days 5-6)

This phase stabilizes the policy and optimizes reasoning without the memory overhead of a critic model.

* 
**Dataset Generation:** Generate 100K preference pairs per task from the SFT checkpoints.


* 
**DPO Execution:** Run Direct Preference Optimization for 1 epoch independently per agent, strictly using a low temperature (β=0.1) for strong preference adherence.


* 
**GRPO Optimization:** Execute Group Relative Policy Optimization using a group size of G=6 for Agent-α and G=8 for Agent-β.


* 
**Reward Formulation:** Apply the GRPO reward function for Agent-β, utilizing NDCG@10, HitRate@10, a Diversity Bonus, and Reasoning Coherence, while keeping the KL Divergence Penalty at 0.01 to prevent drift.



### Phase 4: MARL Swarm Alignment (Days 7-8)

This is the core differentiator where the agents are trained as a joint policy rather than independent models.

* 
**COMA Credit Assignment:** Implement Counterfactual Multi-Agent Policy Gradients to isolate each agent's marginal contribution, establishing baselines for when Agent-α acts as an "average user" or Agent-β ignores Agent-α's signals.


* 
**Reward Shaping:** Implement the team reward (`R_swarm`), heavily emphasizing the 10% Consistency Bonus which forces Agent-β to utilize Agent-α's predictions.


* 
**Training Stability:** Enforce Agent Locking by alternating updates; freeze Agent-β while updating Agent-α for 100 steps, then reverse the process to prevent non-stationary policy chasing.


* 
**Communication Channel:** Utilize the 512-dim engineered behavioral vector from Agent-α, paired with Agent-β's learned attention mask, to facilitate cross-agent communication.



### Phase 5: Inference Orchestration & Submission (Day 9)

Finalize the production deployment on Modal using serverless endpoints.

* 
**Swarm Controller Setup:** Deploy the lightweight CPU orchestrator to manage the execution pipeline and inject Agent-α's 512-dim vector into Agent-β's context.


* 
**Adapter Hot-Swapping:** Implement the `set_adapter()` calls in the inference script to swap between Agent-α and Agent-β LoRA weights with sub-50ms context switching.


* 
**Consensus Override Engine:** Program the conflict resolution sub-routine to trigger a regeneration prompt ("Warning: User Model predicts strong dissatisfaction...") if Agent-α predicts a rating ≤ 2 but Agent-β ranks the item at position 1.


* 
**Evaluation:** Run final validation using BERTScore for Task A and NDCG@10 for Task B to finalize submission metrics.
