# RAIR Benchmark Dataset

RAIR (Relevance Assessment for Image Retrieval) is a benchmark dataset for evaluating query-product relevance in e-commerce search scenarios. The dataset contains paired data of user queries and product information (titles, images, attributes, etc.), with four-level human-annotated relevance labels (L1–L4). It also provides VQA-based image understanding results and annotation rule explanations, enabling the assessment of multimodal large language models on e-commerce search relevance judgment tasks.

## Access

The dataset is hosted on Hugging Face (private repository, access token required):

- **Repository**: [https://huggingface.co/datasets/chenJi/RAIR](https://huggingface.co/datasets/chenJi/RAIR)
- **Access Token**: Please contact the authors or request access on the HuggingFace repository page.

### Loading

First, set your HuggingFace token as an environment variable:

```bash
export HF_TOKEN="your_huggingface_token_here"
```

Then load the dataset in Python:

```python
import os
from datasets import load_dataset

token = os.environ["HF_TOKEN"]

# Load a specific subset
ds = load_dataset("chenJi/RAIR", "General_Subset", token=token)
ds = load_dataset("chenJi/RAIR", "Hard_Subset", token=token)
ds = load_dataset("chenJi/RAIR", "Visual_Subset", token=token)
```

## Dataset Composition

The RAIR Benchmark contains a total of **48,949** annotated samples, divided into three subsets:

| Subset | Samples | Size | Description |
|--------|---------|------|-------------|
| **General_Subset** | 32,123 | 46.72 GB | General evaluation set covering diverse product categories, used to assess model's overall relevance judgment capability |
| **Hard_Subset** | 10,931 | 15.96 GB | Hard subset containing more challenging query-product pairs (e.g., ambiguous queries, blurred category boundaries) |
| **Visual_Subset** | 5,895 | 8.37 GB | Visual subset where product image information is essential for accurate relevance judgment |

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
| **L4** | Fully Relevant | The product exactly matches the query intent in both category and attributes |
| **L3** | Partially Relevant | The product is in the correct category but has minor attribute mismatches (e.g., searching for "long-sleeve" but returning "mid-sleeve") |
| **L2** | Category Mismatch but Related | The product does not match the query category but is semantically related (e.g., searching for "toilet stool" but returning "child toilet seat") |
| **L1** | Completely Irrelevant | The product has no relevance to the query at all |

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
| `visual_salient` | Determine whether visual (image) information is strictly necessary for making the relevance judgment, outputting 1 (yes) or 0 (no) |

## Inference Demo

An end-to-end inference demo is provided in `inference/infer.py`, using [Qwen2.5-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) as the default multimodal LLM.

### Requirements

```bash
pip install datasets transformers torch accelerate qwen-vl-utils Pillow
```

### Usage

```bash
export HF_TOKEN="your_huggingface_token_here"

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
