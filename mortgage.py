#!/usr/bin/env python3
"""Mortgage payoff calculator.

Figure out how much time is left on your mortgage,
and how much time could be taken off by making additional payments.

"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List


@dataclass
class ExtraPayment:
    """Track extra payments for the first `count` months."""

    count: int
    amount: Decimal

    @classmethod
    def parse(cls, value: str) -> ExtraPayment:
        if not (match := re.match(r"(\d+):(\d+(?:\.\d{2})?)", value)):
            raise ValueError(f"Payment needs to be in form X:####.##: {value}")
        return ExtraPayment(count=int(match.group(1)), amount=Decimal(match.group(2)))


@dataclass
class PeriodicPayment:
    """Extra principal payment made every `period` months."""

    period: int
    payment: Decimal

    @classmethod
    def parse(cls, value: str) -> PeriodicPayment:
        if not (match := re.match(r"(\d+):(\d+(?:\.\d{2})?)", value)):
            raise ValueError(f"Payment needs to be in form X:####.##: {value}")
        return PeriodicPayment(
            period=int(match.group(1)), payment=Decimal(match.group(2))
        )


def main():
    parser = argparse.ArgumentParser(description="Calculate mortgage payoff schedule")
    parser.add_argument(
        "--balance",
        type=Decimal,
        required=True,
        metavar="####.##",
        help="Starting mortgage balance",
    )
    parser.add_argument(
        "--payment",
        type=Decimal,
        required=True,
        metavar="####.##",
        help="Monthly P&I payment (without escrow)",
    )
    parser.add_argument(
        "--rate",
        type=Decimal,
        required=True,
        metavar="#.##",
        help="Interest rate as percent",
    )
    parser.add_argument(
        "--extra-payments",
        nargs="+",
        metavar="X:###.##",
        type=ExtraPayment.parse,
        help="Extra principal payment for the first X months",
    )
    parser.add_argument(
        "--periodic-payments",
        nargs="+",
        metavar="Y:###.##",
        type=PeriodicPayment.parse,
        help="Periodic principal payment every Y months",
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Print monthly details"
    )

    args = parser.parse_args()

    calculate(
        args.balance,
        args.payment,
        args.rate / 100,
        extra_payments=args.extra_payments,
        periodic_payments=args.periodic_payments,
        verbose=args.verbose,
    )


def calculate(
    balance: Decimal,
    payment: Decimal,
    rate: Decimal,
    *,
    extra_payments: List[ExtraPayment] = None,
    periodic_payments: List[PeriodicPayment] = None,
    verbose: bool = False,
    starting: date = None,
):
    if extra_payments is None:
        extra_payments = []
    if periodic_payments is None:
        periodic_payments = []

    print(f"Balance: {balance:,.2f}")
    print(f"Payment: {payment:,.2f}")
    print(f"Rate: {rate * 100:.3f}%")
    print("Initial extra payments:")
    for p in extra_payments:
        print(f"  {p.amount:,.2f} for {p.count} months")
    print("Periodic extra payments:")
    for p in periodic_payments:
        print(f"  {p.payment:,.2f} every {p.period} months")
    print()

    if verbose:
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

        # add up the extra principal for this month
        principal_extra = 0

        for idx in range(len(extra_payments)):
            # using index since I will be modifying the list as the payments complete
            extra_payment = extra_payments[idx]
            if extra_payment.count < 1:
                # this should have already been caught
                del extra_payments[idx]
                continue
            principal_extra += extra_payment.amount
            extra_payment.count -= 1
            if extra_payment.count == 0:
                del extra_payments[idx]

        for periodic_payment in periodic_payments:
            if count % periodic_payment.period != 0:
                continue
            principal_extra += periodic_payment.payment

        if principal_payment > balance:
            principal_payment = balance
            principal_extra = 0
        elif principal_payment + principal_extra > balance:
            principal_extra = balance - principal_payment

        totals["payments"] += interest_payment + principal_payment + principal_extra

        balance -= principal_payment + principal_extra

        if verbose:
            print(
                f"{month:%b %Y}  {principal_payment:10.2f}  {interest_payment:10.2f}  "
                f"{balance:10.2f}  {principal_payment + principal_extra:10.2f}"
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
