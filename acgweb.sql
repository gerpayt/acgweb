-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2014-06-26 13:40:54
-- 服务器版本: 5.5.37-0ubuntu0.14.04.1
-- PHP 版本: 5.5.13-2+deb.sury.org~trusty+1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `acgweb`
--

-- --------------------------------------------------------

--
-- 表的结构 `activity`
--

CREATE TABLE IF NOT EXISTS `activity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `oid` int(11) NOT NULL,
  `title` varchar(32) NOT NULL,
  `remark` text NOT NULL,
  `venue` tinyint(4) NOT NULL,
  `start_time` int(11) NOT NULL,
  `end_time` int(11) NOT NULL,
  `type` tinyint(4) NOT NULL,
  `status` tinyint(4) NOT NULL,
  `hostname` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oid` (`oid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `article`
--

CREATE TABLE IF NOT EXISTS `article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(32) NOT NULL,
  `cate_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `posttime` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  KEY `title_2` (`title`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `duty`
--

CREATE TABLE IF NOT EXISTS `duty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `aid` int(11) NOT NULL,
  `uid` varchar(12) NOT NULL,
  `status` tinyint(4) NOT NULL,
  `process` text NOT NULL,
  `log` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aid` (`aid`),
  KEY `uid` (`uid`),
  KEY `aid_2` (`aid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `member`
--

CREATE TABLE IF NOT EXISTS `member` (
  `uid` varchar(12) NOT NULL,
  `name` varchar(12) NOT NULL,
  `password` varchar(32) NOT NULL,
  `type` tinyint(4) NOT NULL,
  `sex` tinyint(4) NOT NULL,
  `school` varchar(12) NOT NULL,
  `mobile_num` varchar(12) NOT NULL,
  `mobile_type` tinyint(4) NOT NULL,
  `mobile_short` varchar(8) NOT NULL,
  `email` varchar(32) NOT NULL,
  `qqnum` varchar(32) NOT NULL,
  `address` varchar(16) NOT NULL,
  `credit_card` varchar(20) NOT NULL,
  `photo` text NOT NULL,
  `introduce` text NOT NULL,
  `register_time` int(11) NOT NULL,
  `lastlogin_time` int(11) NOT NULL,
  `flag` int(11) NOT NULL,
  PRIMARY KEY (`uid`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

--
-- 转存表中的数据 `member`
--

INSERT INTO `member` (`uid`, `name`, `password`, `type`, `sex`, `school`, `mobile_num`, `mobile_type`, `mobile_short`, `email`, `qqnum`, `address`, `credit_card`, `photo`, `introduce`, `register_time`, `lastlogin_time`, `flag`) VALUES
('M201371888', '陈丰', '21232f297a57a5a743894a0e4a801fc3', 1, 1, '光电', '15271810369', 1, '61369', 'gerpayt@qq.com', '378874086', '', '', 'data/member/IMG_2587.JPG\ndata/member/IMG_1713.JPG\n', '', 1401159028, 1403593727, 0);
-- --------------------------------------------------------

--
-- 表的结构 `message`
--

CREATE TABLE IF NOT EXISTS `message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fromuid` varchar(12) NOT NULL,
  `touid` varchar(12) NOT NULL,
  `subject` varchar(32) NOT NULL,
  `content` text NOT NULL,
  `sendtime` int(11) NOT NULL,
  `readtime` int(11) NOT NULL,
  `type` tinyint(4) NOT NULL,
  `status` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `from` (`fromuid`),
  KEY `to` (`touid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `schedule`
--

CREATE TABLE IF NOT EXISTS `schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(12) NOT NULL,
  `semester` varchar(8) NOT NULL,
  `week` varchar(16) NOT NULL,
  `weekday` varchar(8) NOT NULL,
  `section` varchar(8) NOT NULL,
  `classname` varchar(32) NOT NULL,
  `classtype` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `uid` (`uid`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
