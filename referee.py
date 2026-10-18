"""House-rules referee for Last Card. Rules live in contract/rules.json."""
import argparse
import json
import sys

POWER_RANKS = {"2", "8", "J", "A"}
SUITS = {"H", "D", "C", "S"}


def rank(card):
    return card[:-1]


def suit(card):
    return card[-1]


def check_play(state, card):
    """Return (allowed, rule) for the card alone, ignoring R5/R6/R7."""
    top = state["top_card"]
    active_suit = state.get("active_suit")

    # R4: a pending pickup from 2s can only be answered with another 2.
    if state.get("pending_draw", 0) > 0:
        return rank(card) == "2", "R4"
    # R2: Aces are wild whenever no pickup is pending.
    if rank(card) == "A":
        return True, "R2"
    # R3: a called suit replaces the top card entirely.
    if active_suit:
        return suit(card) == active_suit, "R3"
    # R1: match suit or rank.
    return suit(card) == suit(top) or rank(card) == rank(top), "R1"


def rule(state, action):
    card = action["play"]
    said_last_card = action.get("said_last_card", False)
    cards_left = len(state["hand"]) - 1

    allowed, decided_by = check_play(state, card)

    if not allowed:
        # R7: illegal plays are taken back with no penalty. Cite R7 when it is
        # what waives a last-card penalty; R4 stays the cited rule during a
        # pending pickup because it also decides what happens next (pick up).
        if cards_left == 1 and not said_last_card and decided_by != "R4":
            decided_by = "R7"
        return {"allowed": False, "rule": decided_by, "penalty": 0}

    # R5: no going out on a power card.
    if cards_left == 0:
        return {"allowed": rank(card) not in POWER_RANKS, "rule": "R5", "penalty": 0}

    # R6: must say "last card" when going down to one; saying it falsely is free.
    if cards_left == 1 or said_last_card:
        penalty = 2 if cards_left == 1 and not said_last_card else 0
        return {"allowed": True, "rule": "R6", "penalty": penalty}

    return {"allowed": True, "rule": decided_by, "penalty": 0}


def parse_card(text):
    card = text.strip().upper()
    if len(card) < 2 or suit(card) not in SUITS:
        raise argparse.ArgumentTypeError(f"not a card: {text!r} (expected e.g. 7H, 10S, AC)")
    return card


def main(argv=None):
    parser = argparse.ArgumentParser(description="Referee a single Last Card play.")
    parser.add_argument("top_card", type=parse_card)
    parser.add_argument("card_to_play", type=parse_card)
    parser.add_argument("hand", help='cards in hand before playing, e.g. "5S 9C KD"')
    parser.add_argument("--suit", choices=sorted(SUITS), type=str.upper,
                        help="suit called with an Ace, if any")
    parser.add_argument("--pending", type=int, default=0,
                        help="cards pending from 2s played on you")
    parser.add_argument("--said-last-card", action="store_true",
                        help='player said "last card" with this play')
    args = parser.parse_args(argv)

    hand = [parse_card(c) for c in args.hand.split()]
    if args.card_to_play not in hand:
        parser.error(f"{args.card_to_play} is not in the hand {hand}")

    state = {"top_card": args.top_card, "active_suit": args.suit,
             "pending_draw": args.pending, "hand": hand}
    action = {"play": args.card_to_play, "said_last_card": args.said_last_card}
    print(json.dumps(rule(state, action)))


if __name__ == "__main__":
    sys.exit(main())
