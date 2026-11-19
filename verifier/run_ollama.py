"""Ask a local Ollama model to draft claims for each scenario, then verify them.
Run on a machine with Ollama:  python3 run_ollama.py llama3.2:3b [http://localhost:11434]
Prints what was blocked and why. Without human labels this measures how often the
model overreaches according to the rules, not clinical correctness."""
import json, sys, urllib.request
from verifier import verify, render
from scenarios import SCENARIOS, PLAN

MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:3b"
HOST = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:11434"

PROMPT = """Você redige o resumo semanal de exercício domiciliar para uma terapeuta ocupacional.
Plano: {plan}
Eventos observados (JSON): {events}
Responda SOMENTE com uma lista JSON de afirmações. Cada afirmação tem:
 text (português), kind (reps | sessions_done | not_observed | not_done | independent | progress | conflict),
 level (1 movimento, 2 exercício feito, 3 independência, 4 evolução funcional),
 value (número, quando houver), session (quando houver), evidence (lista de ids de eventos),
 flags_conflict (true se a frase menciona divergência).
Escreva de 4 a 6 afirmações úteis para a terapeuta."""

def ask(events):
    body = json.dumps({"model": MODEL, "stream": False, "format": "json",
                       "prompt": PROMPT.format(plan=json.dumps(PLAN), events=json.dumps(events, ensure_ascii=False))}).encode()
    req = urllib.request.Request(HOST + "/api/generate", body, {"Content-Type": "application/json"})
    raw = json.loads(urllib.request.urlopen(req, timeout=300).read())["response"]
    data = json.loads(raw)
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), [])
    keep = []
    for c in data:
        if isinstance(c, dict) and "kind" in c and "level" in c:
            c.setdefault("evidence", []); keep.append(c)
    return keep

n = blocked = 0
for name, sc in SCENARIOS.items():
    try:
        draft = ask(sc["events"])
    except Exception as e:
        print("%s: falha ao consultar o modelo ou ler o JSON: %s" % (name, e)); continue
    res = verify(draft, sc["events"], PLAN)
    print("\n=== %s (%d afirmações) ===" % (name, len(res)))
    for r in res:
        n += 1; blocked += not r["ok"]
        print(("passa " if r["ok"] else "barra ") + str(r["claim"].get("text"))[:80] +
              ("" if r["ok"] else "\n       motivo: " + "; ".join(r["reasons"])))
    print("\nEntregue:\n" + render(res))
print("\nModelo %s: %d afirmações, %d barradas (%.0f%%)" % (MODEL, n, blocked, 100 * blocked / max(1, n)))
