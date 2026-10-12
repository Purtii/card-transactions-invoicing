"""Pasul 1: creează tabelele în Supabase, folosind schema.sql."""
from pathlib import Path

from db import get_connection

sql = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")

with get_connection() as conn:
    conn.execute(sql)

print("Tabelele au fost create: customer, cards, card_transactions, invoice_header.")
