# RAIR Benchmark Dataset

RAIR (**R**ule-**A**ware benchmark with **I**mage for **R**elevance) is a large-scale Chinese benchmark for evaluating query-product relevance in e-commerce search, derived from real-world industrial scenarios. The dataset contains paired data of user queries and product information (titles, images, attributes, etc.), with four-level human-annotated relevance labels (L1–L4). It also provides an explicit rule system that standardizes relevance adjudication into reproducible protocols, along with VQA-based image understanding results, enabling the assessment of LLMs and VLMs on e-commerce relevance judgment tasks.

## Access

The dataset is hosted on Hugging Face:

- **Repository**: [https://huggingface.co/datasets/chenJi/RAIR](https://huggingface.co/datasets/chenJi/RAIR)

### Loading


Then load the dataset in Python:

```python
import os
from datasets import load_dataset

# Load a specific subset
ds = load_dataset("chenJi/RAIR", "General_Subset")
ds = load_dataset("chenJi/RAIR", "Hard_Subset")
ds = load_dataset("chenJi/RAIR", "Visual_Subset")
```

## Dataset Composition

The RAIR Benchmark spans 14 real-world e-commerce industries and contains a total of **54,539** annotated samples, divided into three subsets:

| Subset | Samples | Description |
|--------|---------|-------------|
| **General_Subset** | 37,713 | General Subset with industry-balanced sampling, used to evaluate models' fundamental relevance judgment capabilities |
| **Hard_Subset** | 10,931 | Hard Subset targeting reasoning-heavy and knowledge-dependent cases to probe the limits of current models |
| **Visual_Subset** | 5,895 | Visually Salient Subset for cases where visual evidence is important for reliable judgment, enabling targeted evaluation of multimodal integration |

## Data Statistics & Distributions

Detailed statistics of the benchmark are provided in [docs/data_statistics.md](docs/data_statistics.md), including:

- Ground-truth label distribution (L1–L4)
- Hard Subset challenging query intent distribution (DJ / ER / SS / QA / NC / MA)
- Industry distribution of the General Subset ([figure](docs/figures/industry_distribution.png))
- Relevance rule framework and rule activation distribution ([figure](docs/figures/rule_framework.png))
- Definitions of the 16 intent dimensions

## Data Schema

Each sample contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | User search query |
| `title` | string | Product title |
| `item_id` | int | Unique product identifier |
| `groundtruth` | string | Human-annotated relevance label: L1 / L2 / L3 / L4 |
| `shop_name` | string | Shop name |
| `vqa_result` | string | VQA model's image understanding description of the product main image |
| `rule_list` | string | List of annotation rules and explanations used for labeling |
| `cpv_sku` | string | Product CPV/SKU attribute information (JSON format) |
| `subset` | string | Subset identifier |
| `image_base64` | string | Base64-encoded product main image |

## Relevance Label Definitions

| Label | Meaning | Description |
|-------|---------|-------------|
| **L4** | Perfect Match | Ideal alignment; the product completely satisfies the query intent |
| **L3** | Partial Match | Semantic proximity without explicit conflict (e.g., *Red* vs. query "Burgundy Dress") |
| **L2** | Explicit Mismatch | Specific attribute conflicts (e.g., *Blue* vs. query "Burgundy Dress") |
| **L1** | Completely Inconsistent | Fundamental category errors (e.g., *Pants* vs. query "Burgundy Dress") |

For binary relevance evaluation, {L1, L2} are treated as irrelevant and {L3, L4} as relevant.

## Annotation Rules

The `Rules/` directory contains the detailed annotation guidelines used for labeling query-product relevance. Each relevance level (L1–L4) has its own JSON file with structured rule definitions.

```
Rules/
├── L1.json    # Completely Inconsistent
├── L2.json    # Explicit Mismatch
├── L3.json    # Partial Match
└── L4.json    # Perfect Match
```

Each JSON file contains an array of **rule sets**, organized by demand dimensions (e.g., IP, Brand, Category, Style, etc.). Each rule set includes:

| Field | Description |
|-------|-------------|
| `ruleSetName` | The demand dimension this rule set addresses (e.g., "IP需求", "品牌需求", "品类需求") |
| `rules` | Array of specific rules under this dimension |
| `rules[].summary` | Brief summary of the rule |
| `rules[].principle` | Core annotation principle |
| `rules[].details` | Concrete examples with detailed explanations |

Below is a summary of the rule sets covered per level:

| Level | Rule Sets (Demand Dimensions) |
|-------|-------------------------------|
| **L1** | IP, Accessory Matching, Brand, Category, Model/Spec, Shop, Special Cases |
| **L2** | IP, Accessory Matching, Brand, Category, Audience/Demographics, Style & Attributes, Season, Specs & Dimensions, Function, Shop, Set/Single, Special Cases |
| **L3** | Accessory Matching, Audience/Demographics, Style & Attributes, Season, Brand, Category, Specs & Dimensions, Function, Set/Single, Shop, Special Cases |
| **L4** | IP, Accessory Matching, Audience/Demographics, Brand, Category, Style & Attributes, Season, Function, Shop, Specs & Dimensions, Set/Single, Special Cases |

These rules are referenced in each sample's `rule_list` field, providing transparent annotation rationale for every labeled data point.

## Prompt Templates

The dataset includes prompt templates in both Chinese and English under the `prompt_template/` directory, designed for three evaluation tasks:

```
prompt_template/
├── Chinese/
│   ├── relevance_judge.py        # Relevance judgment (L1–L4)
│   ├── hard_query_classify.py    # Hard query intent classification
│   └── visual_salient.py         # Visual necessity assessment
└── English/
    ├── relevance_judge.py
    ├── hard_query_classify.py
    └── visual_salient.py
```

| Template | Task Description |
|----------|-----------------|
| `relevance_judge` | Assess the relevance between a user query and a product, outputting a label from L1 to L4 based on category, brand, style, and other key attributes |
| `hard_query_classify` | Classify hard query intent into one of 7 categories: Domain Jargon (DJ), Entity Relationship (ER), Solution Seeking (SS), Question Answering (QA), Negative Constraints (NC), Multi-Attribute (MA), or Other |
| `visual_salient` | Determine whether visual (image) information is important for making a reliable relevance judgment, outputting 1 (yes) or 0 (no) |

## Inference Demo

An end-to-end inference demo is provided in `inference/infer.py`, using [Qwen2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) as the default multimodal LLM.

### Requirements

```bash
pip install datasets transformers torch accelerate qwen-vl-utils Pillow
```

### Usage

```bash
python inference/infer.py \
    --subset General_Subset \
    --lang en \
    --task relevance_judge \
    --num_samples 5 \
    --model Qwen/Qwen2.5-VL-7B-Instruct
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--subset` | `General_Subset` | Dataset subset: `General_Subset`, `Hard_Subset`, or `Visual_Subset` |
| `--lang` | `en` | Prompt language: `en` (English) or `zh` (Chinese) |
| `--task` | `relevance_judge` | Task template: `relevance_judge`, `hard_query_classify`, or `visual_salient` |
| `--num_samples` | `5` | Number of samples to run inference on |
| `--model` | `Qwen/Qwen2.5-VL-7B-Instruct` | HuggingFace model identifier |
| `--max_new_tokens` | `1024` | Maximum new tokens for generation |

The demo will load the dataset from HuggingFace, build prompts using the selected template, decode product images from Base64, run multimodal inference, and report per-sample predictions along with overall accuracy.

## Data Example

```json
{
  "query": "狗胸背带大型犬",
  "title": "狗狗牵引绳泰迪胸背柯基法斗胸背带牵中型小型犬狗背心式狗绳项圈",
  "item_id": 623055365352,
  "groundtruth": "L4",
  "shop_name": "舒拜宠物用品旗舰店",
  "vqa_result": "一款骑士灰宠物牵引背带套装，包含1.5米牵引绳。背带设计有透气舒适材质，适用于宠物日常外出...",
  "rule_list": "1. 所属规则: 主配件匹配\n搜主件返回主件，搜配件返回配件判定为L4。\n...",
  "cpv_sku": "{\"是否可伸缩\":\"是\",\"品牌\":\"surepet/舒拜\",...}",
  "subset": "general_set_image",
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAIAAADwf7zU..."
}
```

## License

This dataset is intended for academic research purposes only.
