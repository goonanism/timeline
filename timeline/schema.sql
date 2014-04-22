drop table if exists event;
create table event (
  id integer primary key autoincrement,
  name text not null,
  note text null,
  link text null,
  date_from date not null,
  date_to date null,
  milestone integer null
);

drop table if exists tag;
create table tag (
  id integer primary key autoincrement,
  name text not null,
  reference text not null
);

drop table if exists event_tag;
create table event_tag (
  id integer primary key autoincrement,
  event_id integer not null,
  tag_id integer not null
);