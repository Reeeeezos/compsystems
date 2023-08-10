CREATE USER postgres SUPERUSER;

CREATE TABLE features (
    id integer not null,
    name varchar(40),
    geometry geometry(geometry, 4326)
);