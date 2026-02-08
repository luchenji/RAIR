prompt_template = """You are a top-tier expert in e-commerce relevance analysis. Based on the provided item text and image, determine whether visual information is a strictly necessary condition for resolving the relevance judgment.

Metric: Visual Necessity
Evaluate the text and image comprehensively. Assign a value of 1 or 0:

1 (Yes): Must meet BOTH conditions:
  (1) Text Insufficiency: The title, shop name, and text details alone are insufficient to confirm relevance (due to ambiguity or missing key attributes).
  (2) Visual Solution: The image provides critical visual features not mentioned or unclear in the text (e.g., specific style details, silhouette, actual color, spatial structure) that enable a definitive judgment.

0 (No):
  - The text information is already sufficient to judge relevance (whether relevant or irrelevant);
  - OR, although the text is insufficient, the image also fails to provide the critical evidence needed.

Instructions:
- Internal Reasoning: First, deeply analyze the core intent of the query, contrast it with the text coverage, and verify if the image provides decisive incremental information.
- Strict Output: You must AND ONLY need to provide a single number list in the format \\boxed{{[X]}}, where X is 0 or 1. Do not output any other content.

Input:
User Query: {query}
Item Title: {title}
Item Shop: {shop_name}
Item CPV: {cpv_info}
Item SKU: {sku_info}
Item Image: <image_token>"""
