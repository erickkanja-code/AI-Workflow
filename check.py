"""Checks the contract from the chat AI, then runs every dispute against referee.py."""
import json, sys

rules = json.load(open("contract/rules.json"))
disputes = json.load(open("contract/disputes.json"))
rule_ids = {r["id"] for r in rules}

# 1. Is the contract usable? (catches bad output from the chat AI)
problems = []
for d in disputes:
    for key in ("id", "state", "action", "expected"):
        if key not in d:
            problems.append(f"{d.get('id', '?')}: missing '{key}'")
    if d.get("expected", {}).get("rule") not in rule_ids:
        problems.append(f"{d.get('id')}: cites a rule that doesn't exist")
if problems:
    print("Contract is broken, send it back to the chat AI:")
    print("\n".join(problems))
    sys.exit(1)

# 2. Does the referee agree with the players on every dispute?
from referee import rule

failed = 0
for d in disputes:
    got = rule(d["state"], d["action"])
    ok = got == d["expected"]
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {d['id']}  {d['question']}")
    if not ok:
        print(f"      expected {d['expected']}\n      got      {got}")

print(f"\n{len(disputes) - failed}/{len(disputes)} disputes settled correctly")
sys.exit(1 if failed else 0)