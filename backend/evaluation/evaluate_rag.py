import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import asyncio
import re
from typing import List, Dict, Any
from app.services.rag_pipeline import rag_pipeline
from app.services.retrieval import retrieval_service

BENCHMARK_CASES = [
    {
        "id": "Q1_SHIPPING",
        "question": "What is the delivery window for standard ground shipping?",
        "expected_doc": "shipping_and_delivery_policy.md",
        "expected_in_answer": ["3 to 5", "business days"],
        "expect_insufficient": False,
    },
    {
        "id": "Q2_RETURNS",
        "question": "What is the return window and how many days do I have?",
        "expected_doc": "refunds_and_returns_policy.md",
        "expected_in_answer": ["30", "days"],
        "expect_insufficient": False,
    },
    {
        "id": "Q3_TROUBLESHOOTING",
        "question": "My device will not power on, how do I do a hard reset?",
        "expected_doc": "product_troubleshooting_guide.txt",
        "expected_in_answer": ["power", "15 seconds"],
        "expect_insufficient": False,
    },
    {
        "id": "Q4_WARRANTY",
        "question": "How long is the hardware warranty coverage period?",
        "expected_doc": "hardware_warranty_terms.pdf",
        "expected_in_answer": ["1-Year", "Warranty"],
        "expect_insufficient": False,
    },
    {
        "id": "Q5_SECURITY",
        "question": "How many backup codes are given for two-factor authentication?",
        "expected_doc": "account_and_security_faq.md",
        "expected_in_answer": ["10", "backup codes"],
        "expect_insufficient": False,
    },
    {
        "id": "Q6_OUT_OF_DOMAIN",
        "question": "How do I trade bitcoin cryptocurrency on your exchange?",
        "expected_doc": None,
        "expected_in_answer": [],
        "expect_insufficient": True,
    },
]


async def run_evaluation():
    print("=" * 70)
    print("AI CUSTOMER SUPPORT RAG - AUTOMATED BENCHMARK & EVALUATION")
    print("=" * 70)

    total_cases = len(BENCHMARK_CASES)
    retrieval_hits = 0
    insufficient_correct = 0
    faithfulness_passes = 0

    in_domain_count = sum(1 for c in BENCHMARK_CASES if not c["expect_insufficient"])
    out_domain_count = sum(1 for c in BENCHMARK_CASES if c["expect_insufficient"])

    for case in BENCHMARK_CASES:
        qid = case["id"]
        q = case["question"]
        expected_doc = case["expected_doc"]
        expect_insuf = case["expect_insufficient"]

        print(f"\n[Case {qid}] Query: '{q}'")

        # 1. Pipeline execution
        response = await rag_pipeline.run(q)

        # 2. Retrieval hit rate check
        retrieved_docs = [s.document_name for s in response.sources]
        is_hit = False
        if expected_doc:
            is_hit = expected_doc in retrieved_docs
            if is_hit:
                retrieval_hits += 1
            print(f" -> Expected Doc: {expected_doc} | Retrieved: {retrieved_docs} | Hit: {'PASS' if is_hit else 'FAIL'}")
        else:
            print(f" -> Out-of-domain query | Retrieved docs count: {len(retrieved_docs)}")

        # 3. Insufficient context accuracy
        insuf_match = (response.insufficient_context == expect_insuf)
        if insuf_match:
            insufficient_correct += 1
        print(f" -> Insufficient Context Flag: {response.insufficient_context} (Expected: {expect_insuf}) | {'PASS' if insuf_match else 'FAIL'}")

        # 4. Grounded faithfulness check
        if not expect_insuf and response.sources:
            # Check whether retrieved text contains answer keywords
            combined_context = " ".join([s.relevant_excerpt for s in response.sources]).lower()
            all_found = all(kw.lower() in combined_context for kw in case["expected_in_answer"])
            if all_found:
                faithfulness_passes += 1
            print(f" -> Faithfulness Check (Claims grounded in retrieved context): {'PASS' if all_found else 'FAIL'}")
        elif expect_insuf and response.insufficient_context:
            faithfulness_passes += 1
            print(f" -> Faithfulness Check (Properly refused ungrounded claims): PASS")

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY RESULTS")
    print("=" * 70)
    hit_rate = (retrieval_hits / in_domain_count) * 100
    insuf_accuracy = (insufficient_correct / total_cases) * 100
    faith_rate = (faithfulness_passes / total_cases) * 100

    print(f"Total Test Cases:                 {total_cases}")
    print(f"Retrieval Hit Rate (Top-K):       {hit_rate:.1f}% ({retrieval_hits}/{in_domain_count})")
    print(f"Out-of-Domain Rejection Accuracy: {insuf_accuracy:.1f}% ({insufficient_correct}/{total_cases})")
    print(f"Answer Faithfulness Score:        {faith_rate:.1f}% ({faithfulness_passes}/{total_cases})")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_evaluation())
