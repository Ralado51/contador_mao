"""Measure the verifier against the labeled drafts.
Overreach rate = share of delivered claims that a therapist would reject."""
from verifier import verify, render
from scenarios import SCENARIOS, PLAN

tot = dict(n=0, bad=0, bad_pass=0, good_block=0, delivered=0)
for name, sc in SCENARIOS.items():
    res = verify(sc["draft"], sc["events"], PLAN)
    print("\n=== %s ===" % name)
    for r in res:
        exp, ok = r["claim"]["expect"], r["ok"]
        mark = "OK " if exp == ok else "ERR"
        print("%s %s %-62s %s" % (mark, "passa " if ok else "barra ", r["claim"]["text"][:62],
                                  "" if ok else "| " + "; ".join(r["reasons"])))
        tot["n"] += 1; tot["bad"] += (not exp)
        tot["bad_pass"] += (ok and not exp); tot["good_block"] += (exp and not ok)
        tot["delivered"] += ok
    print("\nRelatório entregue ao terapeuta:\n" + render(res))

print("\n=== resumo ===")
print("afirmações:", tot["n"], "| exageradas no rascunho:", tot["bad"])
print("taxa de exagero SEM verificador: %.0f%%" % (100 * tot["bad"] / tot["n"]))
print("taxa de exagero COM verificador: %.0f%% (%d exageradas passaram)" % (
      100 * tot["bad_pass"] / max(1, tot["delivered"]), tot["bad_pass"]))
print("afirmações corretas barradas indevidamente:", tot["good_block"])
