


import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd

from db import get_connection

EXCEL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("Transactions-Example.xlsx")

REQUIRED_COLUMNS = [
    "TransactionId", "TransactionDate", "CustomerCode", "CustomerName", "Email", "City",
    "CardNumber", "CardType", "CardExpiry", "Merchant", "Amount", "Currency", "Status",
]


def text(value):
    """Text curat; celulele goale devin NULL în baza de date."""
    return None if pd.isna(value) else str(value).strip() 




def read_transactions(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Transactions")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        sys.exit(f"Lipsesc coloane din tab-ul Transactions: {', '.join(missing)}")

    before = len(df)
    df = df.dropna(subset=["TransactionId", "CustomerCode", "CardNumber", "TransactionDate", "Amount"])
    df = df.drop_duplicates(subset="TransactionId")
    if len(df) < before:
        print(f"Atenție: {before - len(df)} rânduri ignorate (incomplete sau duplicate).")
    return df


def main() -> None:
    df = read_transactions(EXCEL)
    print(f"Citit din Excel: {len(df)} tranzacții.")

    with get_connection() as conn, conn.cursor() as cur:
       
        customers = df[["CustomerCode", "CustomerName", "Email", "City"]].drop_duplicates("CustomerCode")
        cur.executemany(
            """insert into customer (customer_code, full_name, email, city)
               values (%s, %s, %s, %s)
               on conflict (customer_code) do nothing""",
            [(text(r.CustomerCode), text(r.CustomerName), text(r.Email), text(r.City))
             for r in customers.itertuples(index=False)],
        )
      
        cur.execute("select customer_code, customer_id from customer")
        customer_ids = dict(cur.fetchall())

        cards = df[["CardNumber", "CustomerCode", "CardType", "CardExpiry"]].drop_duplicates("CardNumber")
        cur.executemany(
            """insert into cards (customer_id, card_number, card_type, card_expiry)
               values (%s, %s, %s, %s)
               on conflict (card_number) do nothing""",
            [(customer_ids[text(r.CustomerCode)], text(r.CardNumber), text(r.CardType), text(r.CardExpiry))
             for r in cards.itertuples(index=False)],
        )
        cur.execute("select card_number, card_id from cards")
        card_ids = dict(cur.fetchall())

     
        cur.executemany(
            """insert into card_transactions
                 (transaction_id, card_id, transaction_date, merchant, amount, currency, status)
               values (%s, %s, %s, %s, %s, %s, %s)
               on conflict (transaction_id) do nothing""",
            [(int(r.TransactionId), card_ids[text(r.CardNumber)],
              pd.Timestamp(r.TransactionDate).to_pydatetime(), text(r.Merchant),
              Decimal(str(r.Amount)).quantize(Decimal("0.01")), text(r.Currency), text(r.Status))
             for r in df.itertuples(index=False)],
        )

        print("În baza de date acum:")
        for table in ("customer", "cards", "card_transactions"):
            cur.execute(f"select count(*) from {table}")
           
            print(f"  {table}: {cur.fetchone()[0]}")


if __name__ == "__main__":
    main()
