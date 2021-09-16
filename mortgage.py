"""Mortgage payoff calculator."""

import argparse
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal


def main():
    # TODO: argparse arguments
    pass


def calculate(
    balance: Decimal,
    payment: Decimal,
    rate: Decimal,
    *,
    extra: Decimal = 0,
    verbose: bool = False,
    starting: date = None,
):
    if verbose:
        print(f"Balance: {balance:,.2f}")
        print(f"Payment: {payment:,.2f}")
        print(f"Rate: {rate:.2f}")
        print()
        print(
            "{:8s}  {:>10s}  {:>10s}  {:>10s}  {:>10s}".format(
                "Month", "Principal", "Interest", "Balance", "Total Prin."
            )
        )

    totals = defaultdict(int)
    months = iter_months(starting)
    count = 0
    while balance > 0:
        month = next(months)
        count += 1
        interest_payment = balance * rate / 12
        totals["interest"] += interest_payment
        principal_payment = payment - interest_payment

        if principal_payment > balance:
            principal_payment = balance
            extra = 0

        totals["payments"] += interest_payment + principal_payment + extra

        balance -= principal_payment + extra

        if verbose:
            print(
                f"{month:%b %Y}  {principal_payment:10.2f}  {interest_payment:10.2f}  "
                f"{balance:10.2f}  {principal_payment + extra:10.2f}"
            )

    print(f"Total # of Payments: {count} ({count / 12:.2f} years)")
    print(f"Payoff month: {month:%b %Y}")
    print(f"Total Amount Paid: ${totals['payments']:,.2f}")
    print(f"Total Interest Paid: ${totals['interest']:,.2f}")


def iter_months(start: date = None):
    # Based on https://stackoverflow.com/a/5734564
    if not start:
        start = date.today()

    month_counter = start.year * 12 + start.month - 1

    while True:
        year, month = divmod(month_counter, 12)
        yield date(year, month + 1, 1)
        month_counter += 1


if __name__ == "__main__":
    sys.exit(main())
