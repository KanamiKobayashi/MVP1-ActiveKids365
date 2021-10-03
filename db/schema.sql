drop table if exists results;
create table results (
  `id` integer primary key autoincrement,
  `place` text not null,
  `indoor` text not null,
  `category` text not null,
  `age` text not null,
  `address` text not null,
  `photo` text,
  `web` text,
  `latitude` integer,
  `longitude` integer,
  `locations` text not null,
  `created` datetime default CURRENT_TIMESTAMP
);