import argparse
import json
from pathlib import Path
from typing import Any


WEIGHTS = {
    "price": 0.50,
    "lead_time": 0.30,
    "payment_terms": 0.20,
}


def load_quote(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        quote = json.load(file)

    required_fields = [
        "name",
        "currency",
        "price",
        "lead_time_weeks",
        "payment_days",
    ]

    missing = [field for field in required_fields if field not in quote]
    if missing:
        raise ValueError(
            f"{path}: missing required field(s): {', '.join(missing)}"
        )

    if quote["price"] <= 0:
        raise ValueError(f"{path}: price must be greater than 0")

    if quote["lead_time_weeks"] <= 0:
        raise ValueError(f"{path}: lead_time_weeks must be greater than 0")

    if quote["payment_days"] < 0:
        raise ValueError(f"{path}: payment_days cannot be negative")

    return quote


def validate_currencies(quotes: list[dict[str, Any]]) -> str:
    currencies = {quote["currency"].upper() for quote in quotes}
    if len(currencies) != 1:
        raise ValueError(
            "All quotations must use the same currency in rfqdiff v0.1. "
            "Currency normalization will be added later."
        )
    return next(iter(currencies))


def score_quotes(quotes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    min_price = min(quote["price"] for quote in quotes)
    min_lead_time = min(quote["lead_time_weeks"] for quote in quotes)
    max_payment_days = max(quote["payment_days"] for quote in quotes)

    scored_quotes = []

    for quote in quotes:
        price_score = (min_price / quote["price"]) * WEIGHTS["price"] * 100
        lead_time_score = (
            min_lead_time / quote["lead_time_weeks"]
        ) * WEIGHTS["lead_time"] * 100

        if max_payment_days == 0:
            payment_score = WEIGHTS["payment_terms"] * 100
        else:
            payment_score = (
                quote["payment_days"] / max_payment_days
            ) * WEIGHTS["payment_terms"] * 100

        total_score = price_score + lead_time_score + payment_score

        scored_quote = quote.copy()
        scored_quote["score"] = round(total_score, 1)
        scored_quotes.append(scored_quote)

    return sorted(scored_quotes, key=lambda item: item["score"], reverse=True)


def money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def print_report(quotes: list[dict[str, Any]], currency: str) -> None:
    print("\nRFQDIFF v0.1")
    print("=" * 86)
    print(
        f"{'Supplier':<24}"
        f"{'Price':>18}"
        f"{'Lead time':>14}"
        f"{'Payment':>14}"
        f"{'Score':>12}"
    )
    print("-" * 86)

    for quote in quotes:
        print(
            f"{quote['name']:<24}"
            f"{money(quote['price'], currency):>18}"
            f"{str(quote['lead_time_weeks']) + ' weeks':>14}"
            f"{str(quote['payment_days']) + ' days':>14}"
            f"{str(quote['score']) + '/100':>12}"
        )

    winner = quotes[0]
    cheapest = min(quotes, key=lambda item: item["price"])
    fastest = min(quotes, key=lambda item: item["lead_time_weeks"])
    best_terms = max(quotes, key=lambda item: item["payment_days"])

    print("\nDecision summary")
    print("-" * 86)
    print(f"Recommended supplier : {winner['name']} ({winner['score']}/100)")
    print(f"Lowest price         : {cheapest['name']} ({money(cheapest['price'], currency)})")
    print(
        f"Fastest lead time    : {fastest['name']} "
        f"({fastest['lead_time_weeks']} weeks)"
    )
    print(
        f"Best payment terms   : {best_terms['name']} "
        f"({best_terms['payment_days']} days)"
    )

    print("\nScoring weights")
    print(
        "Price 50% | Lead time 30% | Payment terms 20%\n"
        "Lower price and lead time score higher; longer payment terms score higher."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare supplier quotations from JSON files."
    )
    parser.add_argument(
        "quotes",
        nargs="+",
        type=Path,
        help="Paths to supplier quotation JSON files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if len(args.quotes) < 2:
        raise SystemExit("rfqdiff needs at least two supplier quotation files.")

    try:
        quotes = [load_quote(path) for path in args.quotes]
        currency = validate_currencies(quotes)
        scored_quotes = score_quotes(quotes)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"Error: {error}") from error

    print_report(scored_quotes, currency)


if __name__ == "__main__":
    main()
