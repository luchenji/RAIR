prompt_template = """You are a professional e-commerce analyst. Your task is to analyze the user Query and classify its intent into one of the following 6 categories.

Category Definitions:
1. Domain Jargon (DJ): Queries containing specialized model numbers, nicknames, or industry terms requiring external knowledge to map to a product category (e.g., "13900" → CPU).
2. Entity Relationship (ER): Queries seeking alternatives, comparisons, or specific relations between products (e.g., "SK-II substitute", "cheaper than iPhone").
3. Solution Seeking (SS): Queries describing a usage scenario or problem without specifying a concrete product (e.g., "gift for girlfriend", "bedroom noise reduction"). Note: Specific requests like "1.9m plastic bag" are NOT SS.
4. Question Answering (QA): Direct inquiries about product functions or knowledge (e.g., "Is Redmi a sub-brand of Xiaomi?", "how to clean suede").
5. Negative Constraints (NC): Queries explicitly excluding certain features or ingredients (e.g., "silicone-free shampoo", "non-stick pan").
6. Multi-Attribute (MA): Queries explicitly specifying hard constraints across multiple dimensions (e.g., "red nike running shoes size 42").
7. Other: Queries that do not fit into the above categories.

Instructions:
- Analyze Carefully: First, identify if the query requires external knowledge (DJ/ER), logical reasoning (SS/QA/NC), or strict multi-condition matching (MA).
- Strict Classification: The result must be exactly one of the above 7 options.
- Output Format: First output your reasoning process in <think> tags, then provide the final category wrapped in <answer> tags.

Input:
User Query: {query}"""
