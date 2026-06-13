-- Seed the Online Shop demo database with a tiny schema and some rows so that
-- database-monitoring checks (Module 22) have real objects and data to read.
CREATE TABLE IF NOT EXISTS customers (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    created TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    amount      NUMERIC(10,2) NOT NULL,
    status      TEXT NOT NULL DEFAULT 'paid',
    created     TIMESTAMPTZ DEFAULT now()
);

INSERT INTO customers (name) VALUES ('Alice'), ('Bob'), ('Carol');

INSERT INTO orders (customer_id, amount, status) VALUES
    (1, 49.90, 'paid'),
    (1, 12.00, 'paid'),
    (2, 99.99, 'pending'),
    (3, 5.50,  'paid');
