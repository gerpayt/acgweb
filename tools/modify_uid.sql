-- change uid sql script --
-- replace @old and @new --
set @old = 'M201371888';
set @new = 'M201371888';

-- update member table --
update `member` set `uid` = @new WHERE `uid` = @old;

-- update duty table --
update `duty` set `uid` = @new WHERE `uid` = @old;

-- update message table --
update `message` set `fromuid` = @new WHERE `fromuid` = @old;
update `message` set `touid` = @new WHERE `touid` = @old;

-- update schedule table --
update `schedule` set `uid` = @new WHERE `uid` = @old;

