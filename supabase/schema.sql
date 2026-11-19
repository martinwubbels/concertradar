-- Run once in the SQL editor of your own Supabase project.
-- Only authenticated owners may read or modify their state.
create table if not exists public.concertradar_user_state (
  user_id uuid primary key references auth.users(id) on delete cascade,
  payload jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.concertradar_user_state enable row level security;
revoke all on public.concertradar_user_state from anon;
grant select, insert, update, delete on public.concertradar_user_state to authenticated;
drop policy if exists "read own state" on public.concertradar_user_state;
drop policy if exists "insert own state" on public.concertradar_user_state;
drop policy if exists "update own state" on public.concertradar_user_state;
create policy "read own state" on public.concertradar_user_state
  for select to authenticated using (auth.uid() = user_id);
create policy "insert own state" on public.concertradar_user_state
  for insert to authenticated with check (auth.uid() = user_id);
create policy "update own state" on public.concertradar_user_state
  for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
