Read contract/rules.json and contract/disputes.json. Do not change them.
Write referee.py with one function:

    rule(state, action) -> {"allowed": bool, "rule": str, "penalty": int}

Also let me run it from the terminal like this:
    python referee.py <top_card> <card_to_play> "<hand>"
for example: python referee.py 7H 5S "5S 9C KD"

Then run `python check.py` and fix referee.py until every dispute passes.
If two disputes can't both pass, stop and write QUESTIONS.md explaining why.