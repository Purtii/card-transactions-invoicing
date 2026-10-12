-- Structura bazei de date (după tab-urile din Excel).
-- Scriptul șterge tabelele existente și le recreează, deci poate fi rulat oricând de la zero.

drop table if exists invoice_header cascade;
drop table if exists card_transactions cascade;
drop table if exists cards cascade;
drop table if exists customer cascade;

create table customer (
  customer_id   int generated always as identity primary key,
  customer_code varchar(10)  not null unique,   -- codul din API (ex. C001)
  full_name     varchar(100) not null,
  email         varchar(150),
  city          varchar(60)
);

create table cards (
  card_id       int generated always as identity primary key,
  customer_id   int not null references customer(customer_id),
  card_number   varchar(20) not null unique,    -- număr mascat, ex. 4539********2810
  card_type     varchar(20),
  card_expiry   varchar(5)
);

create table card_transactions (
  transaction_id   int primary key,             -- vine din API, se păstrează ca atare
  card_id          int not null references cards(card_id),
  transaction_date timestamp not null,
  merchant         varchar(100),
  amount           numeric(12,2) not null,
  currency         varchar(3) not null,
  status           varchar(20) not null
);

create table invoice_header (
  invoice_id     int generated always as identity primary key,
  customer_id    int not null references customer(customer_id),
  invoice_number varchar(20) not null,
  period_start   date not null,
  period_end     date not null,
  issue_date     date not null,
  due_date       date not null,
  total_amount   numeric(12,2) not null,
  currency       varchar(3) not null,
  -- o singură factură per client, perioadă și monedă (permite rularea repetată fără dubluri)
  unique (customer_id, period_start, currency)
);
