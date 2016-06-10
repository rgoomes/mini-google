DROP database if EXISTS minigoogle0;
CREATE database minigoogle0;
use minigoogle0;

CREATE TABLE if NOT EXISTS image(
	keyword 	varchar(64),
	name		varchar(64)
);

CREATE INDEX keywordIndex ON image (keyword) USING BTREE;
