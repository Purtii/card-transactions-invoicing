
import sys
from datetime import date, timedelta

from db import get_connection

PERIOD_LAST_DAY = 15   
DUE_DAYS = 15          


def parse_args() -> tuple[int, int]:
   
    if len(sys.argv) != 3:
        sys.exit("Folosire: python generate_invoices.py AN LUNA   (ex.: python generate_invoices.py 2026 9)")
    year, month = int(sys.argv[1]), int(sys.argv[2])
    if not 1 <= month <= 12:
        sys.exit("Luna trebuie să fie între 1 și 12.")
    return year, month


def main() -> None:
    year, month = parse_args()

    period_start = date(year, month, 1)
    period_end = date(year, month, PERIOD_LAST_DAY)
    issue_date = period_end + timedelta(days=1)
    due_date = issue_date + timedelta(days=DUE_DAYS)
    params = {
        "prefix": f"INV-{year}{month:02d}-",
        "start": period_start,
        "end": period_end,
        "end_exclusive": issue_date,   
        "issue": issue_date,
        "due": due_date,
    }

    with get_connection() as conn, conn.cursor() as cur:
        
        cur.execute(
            """insert into invoice_header
                 (customer_id, invoice_number, period_start, period_end,
                  issue_date, due_date, total_amount, currency)
               select cu.customer_id,
                      %(prefix)s::text || cu.customer_code,
                      %(start)s, %(end)s, %(issue)s, %(due)s,
                      sum(t.amount), t.currency
               from card_transactions t
               join cards c      on c.card_id = t.card_id
               join customer cu  on cu.customer_id = c.customer_id
               where t.status = 'APPROVED'
                 and t.transaction_date >= %(start)s
                 and t.transaction_date <  %(end_exclusive)s
               group by cu.customer_id, cu.customer_code, t.currency
               on conflict (customer_id, period_start, currency) do nothing""",
            params,
        )
        print(f"Facturi noi create: {cur.rowcount} (perioada {period_start} - {period_end}).")

      
        cur.execute(
            """select i.invoice_number, cu.full_name, i.issue_date, i.due_date, i.total_amount, i.currency
               from invoice_header i join customer cu on cu.customer_id = i.customer_id
               where i.period_start = %(start)s
               order by i.invoice_number""",
            params,
        )
        rows = cur.fetchall()
        print(f"\n{'Factura':<17}{'Client':<18}{'Emisă':<12}{'Scadentă':<12}{'Total':>10}")
        for number, name, issued, due, total, currency in rows:
            print(f"{number:<17}{name:<18}{issued!s:<12}{due!s:<12}{total:>10,.2f} {currency}")

      
        cur.execute(
            """select coalesce(sum(amount), 0) from card_transactions
               where status = 'APPROVED'
                 and transaction_date >= %(start)s and transaction_date < %(end_exclusive)s""",
            params,
        )
        expected = cur.fetchone()[0]
        invoiced = sum(r[4] for r in rows)
        verdict = "OK" if expected == invoiced else "DIFERĂ!"
        print(f"\nVerificare: facturat {invoiced:,.2f} / tranzacții APPROVED {expected:,.2f} -> {verdict}")


if __name__ == "__main__":
    main()
