# Card transactions → SQL → invoices (Python + Supabase)

## What the project does

1. **Loads** the `Transactions` tab of the Excel file into 3 PostgreSQL tables
   (`customer`, `cards`, `card_transactions`), following the structures given in the other tabs.
2. **Generates invoices** (`invoice_header`) for every customer, covering the first 15 days of a month.



## How it's built (and why)

- **Python + pandas** to read the Excel file. It's the most direct way to read a tab and drop duplicates.
- **Normalized tables.** A customer has several cards and a card has several transactions. The Excel file repeats
  the customer's name on every row, but in the database it appears only once (`customer`).
- **Database-generated keys** (`identity`) for customers, cards and invoices. The Excel rows are matched through
  `customer_code` and `card_number`, which are declared `unique`. `transaction_id` comes from the API, so I keep it as it is.
- **Load order** follows the foreign keys: customers, then cards, then transactions.
- **Amounts** are `numeric(12,2)` in the database and `Decimal` in Python, so there are no rounding errors with money.
- **Safe to re-run.** `on conflict do nothing` when loading, and a `unique (customer_id, period_start, currency)`
  constraint on the invoices.
- **Invoice totals are calculated in SQL** (`sum ... group by`) and then checked automatically against the sum of
  the transactions in the period.

## Assumptions (the exercise doesn't specify them)

- **Invoiced period:** days 1-15 of the month (transactions up to the end of day 15).
- **Issue date:** day 16, right after the period closes. **Due date:** issue date + 15 days.
- **Only `APPROVED` transactions are invoiced.** The `DECLINED` ones never actually went through.
- **Invoice number:** `INV-YYYYMM-<customer code>`, for example `INV-202609-C001`.
- If a customer has transactions in more than one currency, they get one invoice per currency.

## Files

| File | What it does |
|---|---|
| `schema.sql` | table structure |
| `db.py` | database connection |
| `create_tables.py` | creates the tables |
| `load_data.py` | reads the Excel file and loads the data |
| `generate_invoices.py` | generates the invoices |
| `Transactions-Example.xlsx` | sample file (made up, for practice) |
