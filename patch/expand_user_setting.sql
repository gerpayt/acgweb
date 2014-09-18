ALTER TABLE  `member` ADD `setting` TEXT NOT NULL AFTER  `flag` ;
UPDATE `member` SET `setting` = '' ;
