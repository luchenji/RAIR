prompt_template = """You are an expert in e-commerce relevance analysis. Your task is to assess the relevance between a user Query and an item based on provided information.

Key Attributes: Pay attention to Category, Brand, Style Details, Material, Target Audience, Season, Model ID, Specifications, Color, Function, Accessories, Set/Single, Price, Year, Special Attributes, and IP image.

Instructions:
- Synthesize Information: Combine insights from the item Title, CPV (Color-Pattern-Version), and SKU.
- Chain of Thought (CoT): You must enclose your reasoning process within <think> and 

</think>
 tags before outputting the final result.
- Output Format: For L2 cases, specify the mismatch type in brackets, e.g., [L2-Style Mismatch].

Relevance Levels:
- L1 (Irrelevant): Complete category mismatch with no association.
- L2 (Partially Irrelevant): Category mismatch but related; or Category matches but key attributes (e.g., Brand, Spec, Gender) fail.
- L3 (Closely Relevant): Proximate category/attributes but lacks full intent alignment; or contains minor attribute conflicts.
- L4 (Perfectly Relevant): Completely satisfies the query intent.

Input:
User Query: {query}
Item Title: {title}
Item Shop: {shop_name}
Item CPV: {cpv_info}
Item SKU: {sku_info}"""
