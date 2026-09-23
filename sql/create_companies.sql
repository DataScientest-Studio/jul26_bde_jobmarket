CREATE TABLE companies (
    id serial PRIMARY KEY,

    name VARCHAR(255) NOT NULL,
    name_normalized VARCHAR(255),

    siren VARCHAR(9) UNIQUE,
    headquarters_address TEXT,
    creation_date DATE,

    employee_count VARCHAR(100),
    logo_url TEXT,

    offer_count INTEGER
);