create table if not exists public.admin_users (
    id bigserial primary key,
    username text unique not null,
    email text unique not null,
    full_name text,
    role text default 'Administrator',
    password_hash text not null,
    salt text not null,
    is_active boolean default true,
    created_at text,
    last_login_at text
);

alter table public.admin_users disable row level security;
