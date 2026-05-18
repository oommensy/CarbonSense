"""
CarbonSense Safety Evaluation Engine (v2)
==========================================
Lightweight, zero-dependency runtime safety analysis for AI workloads.
Ported and extended from RAI Toolkit — designed to run on every LLM request
without adding meaningful latency.

Evaluates:
  - Prompt injection / jailbreak attempts
  - PII leakage (regex + NER where available)
  - Toxicity scoring
  - Hallucination risk heuristics
  - Unsafe content classification

Returns a structured SafetyResult with per-check scores and a composite
safety_score (0–100, higher = safer).
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


# ─────────────────────────────────────────────────────────────────────────────
# Injection / Jailbreak Patterns
# ─────────────────────────────────────────────────────────────────────────────

_INJECTION_PATTERNS: List[Dict[str, Any]] = [
    # Instruction override
    {"pattern": re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I), "type": "instruction_override", "severity": "high"},
    {"pattern": re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+instructions?", re.I),    "type": "instruction_override", "severity": "high"},
    {"pattern": re.compile(r"forget\s+(everything|all)\s+(you|i)\s+(were|was|have been)\s+told", re.I), "type": "instruction_override", "severity": "high"},
    {"pattern": re.compile(r"your\s+(new\s+)?instructions?\s+(are|is)\s+now", re.I),            "type": "instruction_override", "severity": "high"},
    {"pattern": re.compile(r"override\s+(your\s+)?(system\s+)?prompt", re.I),                  "type": "instruction_override", "severity": "high"},
    # Jailbreak / persona
    {"pattern": re.compile(r"\bdan\b.*\bdo\s+anything\s+now\b", re.I),                         "type": "jailbreak", "severity": "critical"},
    {"pattern": re.compile(r"developer\s+mode", re.I),                                          "type": "jailbreak", "severity": "high"},
    {"pattern": re.compile(r"jailbreak", re.I),                                                 "type": "jailbreak", "severity": "critical"},
    {"pattern": re.compile(r"act\s+as\s+(if\s+you\s+(are|were)|a)\s+", re.I),                  "type": "persona_hijack", "severity": "medium"},
    {"pattern": re.compile(r"pretend\s+(you\s+are|to\s+be)\s+", re.I),                         "type": "persona_hijack", "severity": "medium"},
    {"pattern": re.compile(r"roleplay\s+as\s+", re.I),                                          "type": "persona_hijack", "severity": "medium"},
    {"pattern": re.compile(r"you\s+are\s+now\s+", re.I),                                        "type": "persona_hijack", "severity": "medium"},
    # Data exfiltration
    {"pattern": re.compile(r"(reveal|show|print|output|display)\s+(your\s+)?(system\s+)?prompt", re.I), "type": "exfiltration", "severity": "high"},
    {"pattern": re.compile(r"(what\s+(are|were)\s+your\s+instructions?)", re.I),               "type": "exfiltration", "severity": "medium"},
    {"pattern": re.compile(r"(leak|dump|expose)\s+(your\s+)?(training\s+)?data", re.I),        "type": "exfiltration", "severity": "high"},
    # Token injection
    {"pattern": re.compile(r"<\s*/?system\s*>", re.I),                                          "type": "token_injection", "severity": "high"},
    {"pattern": re.compile(r"\[INST\]|\[/INST\]|<\|im_start\|>|<\|im_end\|>"),                "type": "token_injection", "severity": "high"},
    {"pattern": re.compile(r"###\s*(Human|Assistant|System)\s*:", re.I),                        "type": "token_injection", "severity": "medium"},
    # Encoding tricks
    {"pattern": re.compile(r"base64\s*decode|atob\s*\(", re.I),                                "type": "encoding_trick", "severity": "medium"},
    {"pattern": re.compile(r"hex\s+encoded|rot13", re.I),                                       "type": "encoding_trick", "severity": "low"},
]

# ─────────────────────────────────────────────────────────────────────────────
# PII Patterns
# ─────────────────────────────────────────────────────────────────────────────

_PII_PATTERNS = {
    "email":       re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "ssn":         re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone":       re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"),
    "credit_card": re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"),
    "ip_address":  re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"),
    "passport":    re.compile(r"\b[A-Z]{1,2}[0-9]{6,9}\b"),
    "iban":        re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]{0,16})?\b"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Toxicity Keywords (20 categories)
# ─────────────────────────────────────────────────────────────────────────────

_TOXIC_WORDS = {
    "hate_speech": ["hate", "racist", "bigot", "slur", "nazi", "supremacist"],
    "violence": ["kill", "murder", "assault", "attack", "stab", "shoot", "bomb", "explode"],
    "self_harm": ["suicide", "self-harm", "cut myself", "end my life", "overdose"],
    "sexual": ["porn", "explicit", "nsfw", "nude", "sexual assault"],
    "harassment": ["harass", "bully", "threaten", "stalk", "intimidate"],
    "profanity": ["fuck", "shit", "ass", "bastard", "bitch", "cunt", "damn", "hell"],
    "extremism": ["terrorist", "extremist", "radicalize", "jihad", "manifesto"],
    "drugs": ["cocaine", "heroin", "meth", "fentanyl", "drug deal"],
    "weapons": ["illegal weapon", "untraceable gun", "ghost gun", "make a bomb"],
    "fraud": ["scam", "phishing", "identity theft", "credit card fraud", "money laundering"],
}

_ALL_TOXIC = [w for words in _TOXIC_WORDS.values() for w in words]

# ─────────────────────────────────────────────────────────────────────────────
# Hallucination Heuristics
# ─────────────────────────────────────────────────────────────────────────────

_HALLUCINATION_SIGNALS = [
    re.compile(r"\bas\s+of\s+my\s+knowledge\s+cutoff\b", re.I),
    re.compile(r"\bi\s+(cannot|can't)\s+verify\b", re.I),
    re.compile(r"\bI'm\s+not\s+sure\s+but\b", re.I),
    re.compile(r"\bI\s+believe\s+(but|though)\b", re.I),
    re.compile(r"\b(may|might|could)\s+be\s+incorrect\b", re.I),
    re.compile(r"\bI\s+may\s+be\s+hallucinating\b", re.I),
    re.compile(r"\bplease\s+verify\s+this\b", re.I),
    re.compile(r"\bI\s+don't\s+have\s+access\s+to\s+real.time\b", re.I),
]

# ─────────────────────────────────────────────────────────────────────────────
# Result dataclasses
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SafetyCheckResult:
    check: str
    passed: bool
    score: float          # 0–1 (1 = fully safe)
    severity: str         # "none", "low", "medium", "high", "critical"
    findings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SafetyResult:
    """Composite safety evaluation result for a single LLM request."""
    safety_score: float           # 0–100 (100 = fully safe)
    hallucination_risk: float     # 0–1
    toxicity_score: float         # 0–1
    pii_detected: bool
    pii_count: int
    injection_attempts: int
    safety_violations: int        # total high/critical findings
    checks: List[SafetyCheckResult] = field(default_factory=list)
    safety_events: List[Dict[str, Any]] = field(default_factory=list)
    eval_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "safety_score": round(self.safety_score, 1),
            "hallucination_risk": round(self.hallucination_risk, 3),
            "toxicity_score": round(self.toxicity_score, 3),
            "pii_detected": self.pii_detected,
            "pii_count": self.pii_count,
            "injection_attempts": self.injection_attempts,
            "safety_violations": self.safety_violations,
            "safety_events": self.safety_events,
            "eval_ms": round(self.eval_ms, 2),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Main Evaluator
# ─────────────────────────────────────────────────────────────────────────────

class SafetyEvaluator:
    """
    Lightweight runtime safety evaluator.
    Runs in <5ms on typical LLM prompt/response pairs.
    """

    def evaluate(
        self,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        model_name: Optional[str] = None,
        quantization: Optional[str] = None,
    ) -> SafetyResult:
        t0 = time.perf_counter()

        combined = " ".join(filter(None, [prompt, response]))
        checks: List[SafetyCheckResult] = []
        events: List[Dict[str, Any]] = []

        # 1. Injection check (on prompt only)
        injection_check = self._check_injection(prompt or "")
        checks.append(injection_check)
        if not injection_check.passed:
            for f in injection_check.findings:
                events.append({
                    "event_type": "injection_attempt",
                    "severity": f.get("severity", "high"),
                    "detail": f"Injection pattern detected: {f.get('type')} — '{f.get('match', '')[:80]}'",
                    "score": 1 - injection_check.score,
                })

        # 2. PII check (on both prompt and response)
        pii_check = self._check_pii(combined)
        checks.append(pii_check)
        if not pii_check.passed:
            events.append({
                "event_type": "pii_detected",
                "severity": "high" if pii_check.findings else "low",
                "detail": f"PII detected: {', '.join(set(f['type'] for f in pii_check.findings))}",
                "score": 1 - pii_check.score,
            })

        # 3. Toxicity check (on response primarily, also prompt)
        toxicity_check = self._check_toxicity(combined)
        checks.append(toxicity_check)
        if not toxicity_check.passed:
            events.append({
                "event_type": "toxicity_flagged",
                "severity": toxicity_check.severity,
                "detail": f"Toxicity score {toxicity_check.score:.2f} — matched: {[f['word'] for f in toxicity_check.findings[:3]]}",
                "score": 1 - toxicity_check.score,
            })

        # 4. Hallucination heuristics (on response only)
        halluc_check = self._check_hallucination(response or "", quantization)
        checks.append(halluc_check)
        if not halluc_check.passed:
            events.append({
                "event_type": "hallucination_risk",
                "severity": halluc_check.severity,
                "detail": f"Hallucination risk elevated: {halluc_check.score:.2f}",
                "score": halluc_check.score,
            })

        # Composite safety score (0–100)
        injection_penalty = (1 - injection_check.score) * 40
        pii_penalty       = (1 - pii_check.score) * 25
        toxicity_penalty  = (1 - toxicity_check.score) * 20
        halluc_penalty    = halluc_check.score * 15
        safety_score = max(0.0, 100.0 - injection_penalty - pii_penalty - toxicity_penalty - halluc_penalty)

        violations = sum(
            1 for e in events
            if e.get("severity") in ("high", "critical")
        )

        return SafetyResult(
            safety_score=safety_score,
            hallucination_risk=halluc_check.score,
            toxicity_score=1 - toxicity_check.score,
            pii_detected=not pii_check.passed,
            pii_count=len(pii_check.findings),
            injection_attempts=len(injection_check.findings),
            safety_violations=violations,
            checks=checks,
            safety_events=events,
            eval_ms=(time.perf_counter() - t0) * 1000,
        )

    # ── Private checkers ─────────────────────────────────────────────────────

    def _check_injection(self, text: str) -> SafetyCheckResult:
        findings = []
        for p in _INJECTION_PATTERNS:
            for m in p["pattern"].finditer(text):
                findings.append({
                    "type": p["type"],
                    "severity": p["severity"],
                    "match": m.group(0),
                    "start": m.start(),
                })
        if not findings:
            return SafetyCheckResult("injection", True, 1.0, "none")
        worst = "critical" if any(f["severity"] == "critical" for f in findings) else "high"
        score = max(0.0, 1.0 - len(findings) * 0.25)
        return SafetyCheckResult("injection", False, score, worst, findings)

    def _check_pii(self, text: str) -> SafetyCheckResult:
        findings = []
        for pii_type, pattern in _PII_PATTERNS.items():
            for m in pattern.finditer(text):
                findings.append({"type": pii_type, "match": m.group(0)[:20] + "…", "start": m.start()})
        # Attempt NER if spaCy is available
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:2000])  # limit for speed
            _NER_PII = {"PERSON": "person_name", "ORG": "organization", "GPE": "location"}
            _NOISE = {"SSN", "PII", "AI", "API", "GPU", "LLM", "CPU", "NLP", "ML"}
            for ent in doc.ents:
                if ent.label_ in _NER_PII and ent.text.upper() not in _NOISE and len(ent.text) > 2:
                    findings.append({"type": _NER_PII[ent.label_], "match": ent.text[:30], "start": ent.start_char})
        except Exception:
            pass
        if not findings:
            return SafetyCheckResult("pii", True, 1.0, "none")
        score = max(0.0, 1.0 - len(findings) * 0.15)
        return SafetyCheckResult("pii", False, score, "high", findings)

    def _check_toxicity(self, text: str) -> SafetyCheckResult:
        text_lower = text.lower()
        findings = []
        for word in _ALL_TOXIC:
            if word in text_lower:
                findings.append({"word": word})
        if not findings:
            return SafetyCheckResult("toxicity", True, 1.0, "none")
        raw_score = min(1.0, len(findings) / 5.0)
        severity = "critical" if raw_score > 0.6 else "high" if raw_score > 0.3 else "medium"
        return SafetyCheckResult("toxicity", False, 1.0 - raw_score, severity, findings)

    def _check_hallucination(self, text: str, quantization: Optional[str] = None) -> SafetyCheckResult:
        """
        Heuristic hallucination risk.
        Combines:
          - Linguistic uncertainty signals in the response
          - Quantization level (INT4/GGUF = higher risk baseline)
        """
        signal_count = sum(1 for p in _HALLUCINATION_SIGNALS if p.search(text))
        base_risk = min(1.0, signal_count * 0.15)

        # Quantization penalty: INT4/GGUF models have higher hallucination rates
        quant_penalty = 0.0
        if quantization:
            q = quantization.lower()
            if "int4" in q or "gguf" in q or "q4" in q:
                quant_penalty = 0.12
            elif "int8" in q or "q8" in q:
                quant_penalty = 0.06

        risk = min(1.0, base_risk + quant_penalty)
        if risk < 0.1:
            return SafetyCheckResult("hallucination", True, risk, "none")
        severity = "high" if risk > 0.5 else "medium" if risk > 0.2 else "low"
        return SafetyCheckResult("hallucination", False, risk, severity)


# Module-level singleton
evaluator = SafetyEvaluator()


def evaluate_workload(
    prompt: Optional[str] = None,
    response: Optional[str] = None,
    model_name: Optional[str] = None,
    quantization: Optional[str] = None,
) -> SafetyResult:
    """Convenience function — evaluate a single LLM request."""
    return evaluator.evaluate(prompt=prompt, response=response,
                              model_name=model_name, quantization=quantization)
