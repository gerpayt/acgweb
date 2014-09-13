ALTER TABLE  `activity` ADD  `work_start_time` INT NOT NULL AFTER  `venue` ;
UPDATE `activity` SET  `work_start_time` = `start_time` - 3600 ;
