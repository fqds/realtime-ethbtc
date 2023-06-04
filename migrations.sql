CREATE TABLE stat (
    id bigserial not null primary key, 
    eth_value float not null,
    btc_value float not null,
    unix int not null
);