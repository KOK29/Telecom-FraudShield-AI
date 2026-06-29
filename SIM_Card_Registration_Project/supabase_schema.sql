create table if not exists sim_customers (
    sim_id text primary key,
    full_name text not null,
    nrc text not null,
    location text not null,
    phone_number text default '',
    email text default '',
    status text default 'ACTIVE',
    registered_at text
);

create index if not exists idx_sim_customers_phone_number on sim_customers(phone_number);
create index if not exists idx_sim_customers_nrc on sim_customers(nrc);

alter table sim_customers disable row level security;
