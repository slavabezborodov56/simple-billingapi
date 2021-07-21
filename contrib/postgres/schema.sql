create database billing;

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
			references wallets
);

comment on table users is 'Пользователи';

create unique index users_phone_uindex
	on users (phone);
