import os
import math
import time
import csv
from collections import Counter
from fastapi import FastAPI, Request
import httpx

app = FastAPI(title="iSTAV Gateway Choke Point")

# Framework Bounds (Strictly from .env)
TARGET_ENV_URL = os.environ.get("TARGET_ENV_URL", "http://istav_mock_env:80")
L1_CEIL = float(os.environ.get("L1_CEIL", "0.50"))
TAU_FLOOR = float(os.environ.get("TAU_FLOOR", "0.90"))
L4_FLOOR = float(os.environ.get("L4_FLOOR", "0.10"))
ALPHA = float(os.environ.get("ALPHA", "0.15"))

# Logging Parameters
EXPERIMENT_ID = os.getenv("EXPERIMENT_ID", "Unknown")
RUN_ID = os.getenv("RUN_ID", "Unknown")

# Layer Toggles
L1_ENFORCEMENT = os.environ.get("L1_ENFORCEMENT", "True") == "True"
L4_RESET_ENABLED = os.environ.get("L4_RESET", "False") == "True"

# Rolling Memory 
vocab_history = []
entropy_history = []
tau_eff = 1.0

# Initialize telemetry log
csv_file = "telemetry.csv"
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Iteration", "SD", "JD", "Tau_eff", "Action", "Tau_Floor", "L1_Ceil", "Latency_ms"])

def calculate_context_entropy(text: str) -> float:
    words = text.lower().split()
    if not words: return 0.0
    word_counts = Counter(words)
    total_words = len(words)
    return -sum((count / total_words) * math.log2(count / total_words) for count in word_counts.values())

def calculate_jaccard_distance(current_vocab: set, prev_vocab: set) -> float:
    if not prev_vocab: return 0.0
    intersection = current_vocab.intersection(prev_vocab)
    union = current_vocab.union(prev_vocab)
    return 1.0 - (len(intersection) / len(union)) if union else 0.0

@app.post("/post")
async def proxy_agent_payload(request: Request):
    global vocab_history, entropy_history, tau_eff
        
    payload = await request.json()
    content = payload.get("content", "")
    iteration = int(payload.get("iteration", 0))
    
    start_time = time.perf_counter()
    current_vocab = set(word.strip('.,!?"\'') for word in content.lower().split())
    
    # 1. Layer 1: Structural Telemetry (SD)
    current_entropy = calculate_context_entropy(content)
    historical_mean = sum(entropy_history) / len(entropy_history) if entropy_history else current_entropy
    sd = abs(current_entropy - historical_mean)
    
    entropy_history.append(current_entropy)
    if len(entropy_history) > 10:
        entropy_history.pop(0)
    
    # 2. Layer 3/4: Semantic Telemetry (JD)
    reference_vocab = set().union(*vocab_history) if vocab_history else current_vocab
    jd = calculate_jaccard_distance(current_vocab, reference_vocab)
    
    latency_ms = (time.perf_counter() - start_time) * 1000

    # 3. Dynamic Trust Degradation (The Heart)
    is_semantic_breach = jd > TAU_FLOOR and iteration > 1
    if is_semantic_breach:
        tau_eff = max(0.0, tau_eff - ALPHA)
    elif iteration > 1:
        tau_eff = min(1.0, tau_eff + 0.05) # Gradual recovery if payload is clean

    # Only update semantic memory if structurally and semantically safe
    if sd <= L1_CEIL and not is_semantic_breach:
        vocab_history.append(current_vocab)
        if len(vocab_history) > 4:
            vocab_history.pop(0)

    # 4. Deterministic Transport Attestation (Layer 1)
    if L1_ENFORCEMENT and sd > L1_CEIL:
        enforcement_status = "BLOCKED"
        forward_to_target = False
    else:
        enforcement_status = "FORWARDED"
        forward_to_target = True

    # 5. Record Telemetry
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([iteration, sd, jd, tau_eff, enforcement_status, TAU_FLOOR, L1_CEIL, round(latency_ms, 2)])

    metrics = {
        "sd": round(sd, 4),
        "jd": round(jd, 4),
        "tau_eff": round(tau_eff, 4),
        "latency_ms": round(latency_ms, 2)
    }
    
    # 6. Dispatch Response Logic
    
    # Check Layer 4 Mathematical Threshold Trigger First
    if tau_eff <= L4_FLOOR:
        if L4_RESET_ENABLED:
            tau_eff = 1.0
            entropy_history.clear()
            vocab_history.clear()
            return {"status_code": 423, "response_body": "Locked: Cognitive Reset Required", **metrics}
        
    # Check Layer 1 Hard Block
    if not forward_to_target:
        return {"status_code": 403, "response_body": "Forbidden: Attestation Failure", **metrics}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{TARGET_ENV_URL}", json=payload)
            status = response.status_code
        except Exception:
            status = 200
            
    return {"status_code": status, "response_body": "Success", **metrics}