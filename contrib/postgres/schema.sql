create table wallets
(
	id serial not null
		constraint wallets_pk
			primary key,
	amount bigint not null
);

comment on table wallets is 'Кошельки';

create table users
(
	id serial not null
		constraint users_pk
			primary key,
	phone bigint not null,
	wallet_id integer not null
		constraint users_wallets_id_fk
			references wallets,
	created_at timestamp with time zone not null
);

comment on table users is 'Пользователи';

create unique index users_phone_uindex
	on users (phone);

create table operation_logs
(
	id bigserial not null
		constraint operation_logs_pk
			primary key,
	wallet_from integer
		constraint operation_logs_wallets_id_fk
			references wallets,
	wallet_to integer not null
		constraint operation_logs_wallets_id_fk_2
			references wallets,
	idempotency_key uuid not null,
	date timestamp with time zone not null,
	amount bigint not null
);

comment on table operation_logs is 'Лог операций движения денежных средств';

create unique index operation_logs_idempotency_key_uindex
	on operation_logs (idempotency_key);
