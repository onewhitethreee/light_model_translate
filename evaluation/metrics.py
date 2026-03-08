from __future__ import annotations

import sacrebleu


def compute_bleu(hypothesis: str, reference: str) -> float:
    return sacrebleu.sentence_bleu(hypothesis, [reference]).score


def compute_chrf(hypothesis: str, reference: str) -> float:
    return sacrebleu.sentence_chrf(hypothesis, [reference]).score


def compute_corpus_bleu(hypotheses: list[str], references: list[str]) -> float:
    return sacrebleu.corpus_bleu(hypotheses, [references]).score


def compute_corpus_chrf(hypotheses: list[str], references: list[str]) -> float:
    return sacrebleu.corpus_chrf(hypotheses, [references]).score
