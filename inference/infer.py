"""
RAIR Benchmark Inference Demo
=============================
End-to-end example: load dataset from HuggingFace → build prompt → run inference
with Qwen2.5-VL-7B-Instruct (a multimodal LLM that accepts both text and images).

Requirements:
    pip install datasets transformers torch accelerate qwen-vl-utils Pillow

Usage:
    python infer_demo.py \
        --subset General_Subset \
        --lang en \
        --task relevance_judge \
        --num_samples 5 \
        --model Qwen/Qwen2.5-VL-7B-Instruct
"""

import argparse
import base64
import json
import re
import sys
import os
from io import BytesIO

import torch
from PIL import Image
from datasets import load_dataset
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

# ─── HuggingFace access ────────────────────────────────────────────────────────
HF_REPO_ID = "chenJi/RAIR"
HF_TOKEN = os.environ.get("HF_TOKEN", None)
if not HF_TOKEN:
    raise EnvironmentError("Please set the HF_TOKEN environment variable: export HF_TOKEN='your_token'")

# ─── Prompt template directory (relative to this script) ───────────────────────
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prompt_template")


# =============================================================================
#  Utilities
# =============================================================================

def load_prompt_template(task: str, lang: str) -> str:
    """Load a prompt template by task name and language."""
    lang_dir = "English" if lang == "en" else "Chinese"
    path = os.path.join(TEMPLATE_DIR, lang_dir, f"{task}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt template not found: {path}")

    namespace = {}
    with open(path, "r", encoding="utf-8") as f:
        exec(f.read(), namespace)
    return namespace["prompt_template"]


def parse_cpv_sku(cpv_sku_str: str):
    """Parse the cpv_sku JSON string and split into cpv_info and sku_info."""
    try:
        data = json.loads(cpv_sku_str) if cpv_sku_str else {}
    except json.JSONDecodeError:
        data = {}
    # For simplicity, treat the whole dict as both cpv and sku info
    info_str = ", ".join(f"{k}: {v}" for k, v in data.items()) if data else "N/A"
    return info_str, info_str


def decode_image(image_base64: str) -> Image.Image:
    """Decode a base64 string to a PIL Image."""
    img_bytes = base64.b64decode(image_base64)
    return Image.open(BytesIO(img_bytes)).convert("RGB")


def build_prompt(template: str, sample: dict) -> str:
    """Fill the prompt template with sample fields."""
    cpv_info, sku_info = parse_cpv_sku(sample.get("cpv_sku", ""))
    return template.format(
        query=sample.get("query", ""),
        title=sample.get("title", ""),
        shop_name=sample.get("shop_name", ""),
        cpv_info=cpv_info,
        sku_info=sku_info,
    )


def extract_label(text: str) -> str:
    """Extract the predicted relevance label (L1-L4) from model output."""
    match = re.search(r"\b(L[1-4])\b", text)
    return match.group(1) if match else "N/A"


# =============================================================================
#  Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="RAIR Benchmark Inference Demo")
    parser.add_argument("--subset", type=str, default="General_Subset",
                        choices=["General_Subset", "Hard_Subset", "Visual_Subset"],
                        help="Dataset subset to load")
    parser.add_argument("--lang", type=str, default="en", choices=["en", "zh"],
                        help="Prompt language: en (English) or zh (Chinese)")
    parser.add_argument("--task", type=str, default="relevance_judge",
                        choices=["relevance_judge", "hard_query_classify", "visual_salient"],
                        help="Evaluation task / prompt template to use")
    parser.add_argument("--num_samples", type=int, default=5,
                        help="Number of samples to run inference on")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-VL-7B-Instruct",
                        help="HuggingFace model name")
    parser.add_argument("--max_new_tokens", type=int, default=1024,
                        help="Max new tokens for generation")
    args = parser.parse_args()

    # ── 1. Load dataset ─────────────────────────────────────────────────────────
    print(f"[1/4] Loading dataset: {HF_REPO_ID} / {args.subset} ...")
    ds = load_dataset(HF_REPO_ID, args.subset, token=HF_TOKEN, split="train")
    print(f"       Loaded {len(ds)} samples.")

    # ── 2. Load prompt template ─────────────────────────────────────────────────
    print(f"[2/4] Loading prompt template: {args.task} ({args.lang}) ...")
    template = load_prompt_template(args.task, args.lang)
    print(f"       Template loaded ({len(template)} chars).")

    # ── 3. Load model ───────────────────────────────────────────────────────────
    print(f"[3/4] Loading model: {args.model} ...")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    processor = AutoProcessor.from_pretrained(args.model, trust_remote_code=True)
    print(f"       Model loaded on {model.device}.")

    # ── 4. Inference ────────────────────────────────────────────────────────────
    num = min(args.num_samples, len(ds))
    print(f"[4/4] Running inference on {num} samples ...\n")
    print("=" * 80)

    correct = 0
    for i in range(num):
        sample = ds[i]
        prompt_text = build_prompt(template, sample)
        groundtruth = sample.get("groundtruth", "N/A")

        # Decode image
        image = decode_image(sample["image_base64"])

        # Build Qwen2.5-VL message format
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text",  "text": prompt_text},
                ],
            }
        ]

        # Prepare inputs
        text_input = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text_input],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(model.device)

        # Generate
        with torch.no_grad():
            output_ids = model.generate(**inputs, max_new_tokens=args.max_new_tokens)

        # Decode — only the generated part
        generated_ids = output_ids[0][inputs.input_ids.shape[1]:]
        response = processor.decode(generated_ids, skip_special_tokens=True)

        # Extract label
        pred_label = extract_label(response)
        is_correct = pred_label == groundtruth
        if is_correct:
            correct += 1

        # Print result
        print(f"Sample {i + 1}/{num}")
        print(f"  Query       : {sample['query']}")
        print(f"  Title       : {sample['title'][:80]}...")
        print(f"  Groundtruth : {groundtruth}")
        print(f"  Prediction  : {pred_label} {'✓' if is_correct else '✗'}")
        print(f"  Response    : {response[:200]}...")
        print("-" * 80)

    # ── Summary ─────────────────────────────────────────────────────────────────
    accuracy = correct / num * 100 if num > 0 else 0
    print(f"\nAccuracy: {correct}/{num} = {accuracy:.1f}%")


if __name__ == "__main__":
    main()
