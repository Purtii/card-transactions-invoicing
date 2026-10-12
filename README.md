# Test tehnic: tranzacții card -> SQL -> facturi (Python + Supabase)

## Ce face proiectul

1. **Încarcă** datele din tab-ul `Transactions` al fișierului Excel în 3 tabele PostgreSQL
   (`customer`, `cards`, `card_transactions`), conform structurilor din celelalte tab-uri.
2. **Generează facturi** (`invoice_header`) pentru fiecare client, pentru primele 15 zile ale unei luni.

## Cum se rulează

```
python -m venv .venv
.venv\Scripts\activate            (Windows)   |   source .venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
```

1. Copiază `.env.example` ca `.env` și pune connection string-ul Supabase (Session pooler).
2. `python create_tables.py`: creează tabelele (șterge și recreează, deci pornește mereu de la zero).
3. `python load_data.py`: încarcă datele din Excel.
4. `python generate_invoices.py 2026 9`: generează facturile pentru 1-15 septembrie 2026.

Scripturile 2 și 3 pot fi rulate de mai multe ori fără să dubleze datele.

## Cum este gândit (și de ce)

- **Python + pandas** pentru citirea Excelului: e cel mai direct mod de a citi un tab și de a elimina duplicatele.
- **Tabele normalizate**: un client are mai multe carduri, un card are mai multe tranzacții. Excelul repetă
  numele clientului pe fiecare rând; în baza de date apare o singură dată (`customer`).
- **Chei generate de baza de date** (`identity`) pentru client, card și factură. Legătura cu Excelul se face prin
  `customer_code` și `card_number`, declarate `unique`. `transaction_id` vine din API și se păstrează ca atare.
- **Ordinea încărcării** respectă cheile străine: clienți -> carduri -> tranzacții.
- **Suma ca `numeric(12,2)`** și `Decimal` în Python, ca să nu apară erori de rotunjire la bani.
- **Rulare repetată sigură**: `on conflict do nothing` la încărcare și constrângerea
  `unique (customer_id, period_start, currency)` la facturi.
- **Totalul facturilor se calculează în SQL** (`sum ... group by`), apoi se verifică automat față de suma
  tranzacțiilor din perioadă.

## Presupuneri (enunțul nu le precizează)

- **Perioada facturată:** zilele 1-15 ale lunii (tranzacțiile de până la finalul zilei 15).
- **Data emiterii:** ziua 16, imediat după închiderea perioadei. **Scadența:** emiterea + 15 zile.
- **Se facturează doar tranzacțiile `APPROVED`**; cele `DECLINED` nu au fost efectuate efectiv.
- **Număr factură:** `INV-AAAALL-<cod client>`, de exemplu `INV-202609-C001`.
- Dacă un client are tranzacții în mai multe monede, primește câte o factură per monedă.

## Structura fișierelor

| Fișier | Rol |
|---|---|
| `schema.sql` | structura tabelelor |
| `db.py` | conexiunea la baza de date |
| `create_tables.py` | creează tabelele |
| `load_data.py` | citește Excelul și încarcă datele |
| `generate_invoices.py` | generează facturile |
| `test_tehnic_exemplu.xlsx` | fișier de exemplu (inventat, pentru exersare) |
