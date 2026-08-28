import argparse
import csv
import json
from pathlib import Path
from typing import Any


VERSION = "0.2"

WEIGHTS = {
    "price": 0.50,
    "lead_time": 0.30,
    "payment_terms": 0.20,
}

REQUIRED_FIELDS = [
    "name",
    "currency",
    "price",
    "lead_time_weeks",
    "payment_days",
]


def _coerce_number(value: Any, field: str, source: str) -> int | float:
    if isinstance(value, bool):
        raise ValueError(f"{source}: {field} must be numeric")

    if isinstance(value, (int, float)):
        number = value
    else:
        try:
            number = float(str(value).strip())
        except (TypeError, ValueError) as error:
            raise ValueError(f"{source}: {field} must be numeric") from error

    if isinstance(number, float) and number.is_integer():
        return int(number)
    return number


def validate_quote(quote: dict[str, Any], source: str) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in quote]
    if missing:
        raise ValueError(
            f"{source}: missing required field(s): {', '.join(missing)}"
        )

    validated = quote.copy()
    validated["price"] = _coerce_number(validated["price"], "price", source)
    validated["lead_time_weeks"] = _coerce_number(
        validated["lead_time_weeks"], "lead_time_weeks", source
    )
    validated["payment_days"] = _coerce_number(
        validated["payment_days"], "payment_days", source
    )

    if validated["price"] <= 0:
        raise ValueError(f"{source}: price must be greater than 0")

    if validated["lead_time_weeks"] <= 0:
        raise ValueError(f"{source}: lead_time_weeks must be greater than 0")

    if validated["payment_days"] < 0:
        raise ValueError(f"{source}: payment_days cannot be negative")

    validated["currency"] = str(validated["currency"]).strip().upper()
    if not validated["currency"]:
        raise ValueError(f"{source}: currency cannot be empty")

    validated["name"] = str(validated["name"]).strip()
    if not validated["name"]:
        raise ValueError(f"{source}: name cannot be empty")

    return validated


def load_quote(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        quote = json.load(file)

    if not isinstance(quote, dict):
        raise ValueError(f"{path}: quotation JSON must contain one object")

    return validate_quote(quote, str(path))


def load_csv_quotes(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or []
        missing = [field for field in REQUIRED_FIELDS if field not in fieldnames]
        if missing:
            raise ValueError(
                f"{path}: missing required column(s): {', '.join(missing)}"
            )

        quotes = [
            validate_quote(dict(row), f"{path}: row {row_number}")
            for row_number, row in enumerate(reader, start=2)
            if any(value not in (None, "") for value in row.values())
        ]

    if not quotes:
        raise ValueError(f"{path}: no supplier quotations found")
    return quotes


def load_xlsx_quotes(path: Path) -> list[dict[str, Any]]:
    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise ValueError(
            "Excel import requires openpyxl. Install the project package dependencies first."
        ) from error

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook.active
        rows = worksheet.iter_rows(values_only=True)
        try:
            header_row = next(rows)
        except StopIteration as error:
            raise ValueError(f"{path}: workbook is empty") from error

        fieldnames = [
            str(value).strip() if value is not None else "" for value in header_row
        ]
        missing = [field for field in REQUIRED_FIELDS if field not in fieldnames]
        if missing:
            raise ValueError(
                f"{path}: missing required column(s): {', '.join(missing)}"
            )

        quotes = []
        for row_number, values in enumerate(rows, start=2):
            if not any(value not in (None, "") for value in values):
                continue
            row = dict(zip(fieldnames, values))
            quotes.append(validate_quote(row, f"{path}: row {row_number}"))
    finally:
        workbook.close()

    if not quotes:
        raise ValueError(f"{path}: no supplier quotations found")
    return quotes


def load_quotes(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return [load_quote(path)]
    if suffix == ".csv":
        return load_csv_quotes(path)
    if suffix == ".xlsx":
        return load_xlsx_quotes(path)
    raise ValueError(
        f"{path}: unsupported quotation format '{suffix or '<none>'}'. "
        "Use .json, .csv or .xlsx."
    )


def validate_currencies(quotes: list[dict[str, Any]]) -> str:
    currencies = {quote["currency"].upper() for quote in quotes}
    if len(currencies) != 1:
        raise ValueError(
            "All quotations must use the same currency. "
            "Normalize mixed-currency quotations first with currency-normalizer."
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

    return sorted(
        scored_quotes,
        key=lambda item: (-item["score"], item["name"].lower()),
    )


def build_result(
    scored_quotes: list[dict[str, Any]],
    currency: str,
) -> dict[str, Any]:
    winner = scored_quotes[0]
    cheapest = min(scored_quotes, key=lambda item: item["price"])
    fastest = min(scored_quotes, key=lambda item: item["lead_time_weeks"])
    best_terms = max(scored_quotes, key=lambda item: item["payment_days"])

    return {
        "tool": "rfqdiff",
        "version": VERSION,
        "currency": currency,
        "recommended_supplier": winner["name"],
        "suppliers": scored_quotes,
        "decision_summary": {
            "recommended_supplier": {
                "name": winner["name"],
                "score": winner["score"],
            },
            "lowest_price": {
                "name": cheapest["name"],
                "price": cheapest["price"],
            },
            "fastest_lead_time": {
                "name": fastest["name"],
                "lead_time_weeks": fastest["lead_time_weeks"],
            },
            "best_payment_terms": {
                "name": best_terms["name"],
                "payment_days": best_terms["payment_days"],
            },
        },
        "weights": WEIGHTS,
    }


def money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def print_report(quotes: list[dict[str, Any]], currency: str) -> None:
    print(f"\nRFQDIFF v{VERSION}")
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

    payload = build_result(quotes, currency)
    summary = payload["decision_summary"]
    winner = summary["recommended_supplier"]
    cheapest = summary["lowest_price"]
    fastest = summary["fastest_lead_time"]
    best_terms = summary["best_payment_terms"]

    print("\nDecision summary")
    print("-" * 86)
    print(f"Recommended supplier : {winner['name']} ({winner['score']}/100)")
    print(
        f"Lowest price         : {cheapest['name']} "
        f"({money(cheapest['price'], currency)})"
    )
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


def write_json(payload: dict[str, Any], path: Path) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare supplier quotations from JSON, CSV or Excel files."
    )
    parser.add_argument(
        "quotes",
        nargs="+",
        type=Path,
        help="Quotation files (.json, .csv or .xlsx). Tabular files may contain multiple suppliers.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Return a machine-readable comparison payload.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the machine-readable comparison payload to a JSON file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        quotes = [quote for path in args.quotes for quote in load_quotes(path)]
        if len(quotes) < 2:
            raise ValueError("rfqdiff needs at least two supplier quotations.")
        currency = validate_currencies(quotes)
        scored_quotes = score_quotes(quotes)
        payload = build_result(scored_quotes, currency)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"Error: {error}") from error

    if args.output:
        write_json(payload, args.output)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_report(scored_quotes, currency)


if __name__ == "__main__":
    main()
