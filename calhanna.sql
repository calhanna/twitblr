/*
 Navicat Premium Data Transfer

 Source Server         : asfdasdf
 Source Server Type    : MySQL
 Source Server Version : 80023
 Source Host           : 10.0.0.17:3306
 Source Schema         : calhanna

 Target Server Type    : MySQL
 Target Server Version : 80023
 File Encoding         : 65001

 Date: 06/06/2023 14:41:02
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tblactions
-- ----------------------------
DROP TABLE IF EXISTS `tblactions`;
CREATE TABLE `tblactions`  (
  `action_id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NULL DEFAULT NULL,
  `user_id` int NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`action_id`) USING BTREE,
  INDEX `action_user_id`(`user_id` ASC) USING BTREE,
  INDEX `post_id`(`post_id` ASC) USING BTREE,
  CONSTRAINT `action_user_id` FOREIGN KEY (`user_id`) REFERENCES `tblusers` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `post_id` FOREIGN KEY (`post_id`) REFERENCES `tblpost` (`post_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 196 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tblactions
-- ----------------------------
INSERT INTO `tblactions` VALUES (185, 32, 2, 'Like');
INSERT INTO `tblactions` VALUES (186, 27, 2, 'Like');
INSERT INTO `tblactions` VALUES (187, 26, 2, 'Like');
INSERT INTO `tblactions` VALUES (188, 22, 2, 'Like');
INSERT INTO `tblactions` VALUES (189, 11, 2, 'Like');
INSERT INTO `tblactions` VALUES (190, 9, 2, 'Like');
INSERT INTO `tblactions` VALUES (191, 7, 2, 'Like');
INSERT INTO `tblactions` VALUES (192, 6, 2, 'Like');
INSERT INTO `tblactions` VALUES (193, 12, 1, 'Like');
INSERT INTO `tblactions` VALUES (194, 10, 1, 'Like');
INSERT INTO `tblactions` VALUES (195, 22, 1, 'Like');

-- ----------------------------
-- Table structure for tblpost
-- ----------------------------
DROP TABLE IF EXISTS `tblpost`;
CREATE TABLE `tblpost`  (
  `post_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT 'Need to link this but I can\'t remember how',
  `date` date NULL DEFAULT NULL,
  `time` time NULL DEFAULT NULL,
  `content` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '255 character limit appears to be standard',
  `reply_id` int NULL DEFAULT 0,
  PRIMARY KEY (`post_id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `tblusers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 42 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tblpost
-- ----------------------------
INSERT INTO `tblpost` VALUES (1, 1, '2023-02-28', '15:04:11', 'this is a test post please ignore', 0);
INSERT INTO `tblpost` VALUES (4, 2, '2023-03-03', '12:43:52', 'this is a test post that wont be put in the database', 0);
INSERT INTO `tblpost` VALUES (6, 3, '2023-03-06', '12:53:59', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 0);
INSERT INTO `tblpost` VALUES (7, 1, '2023-03-21', '14:46:24', 'OR 1=1', 0);
INSERT INTO `tblpost` VALUES (9, 1, '2023-03-27', '12:52:27', '<img src=\"https://previews.123rf.com/images/ratoca/ratoca1505/ratoca150500621/39986628-funny-goblin.jpg\"/>', 0);
INSERT INTO `tblpost` VALUES (10, 2, '2023-03-27', '13:19:47', '<b>my post is so cool</b> <h1 style=\"color:pink\">AAAA</h1>', 0);
INSERT INTO `tblpost` VALUES (11, 1, '2023-03-27', '13:21:31', '<img src=\"https://previews.123rf.com/images/ratoca/ratoca1505/ratoca150500621/39986628-funny-goblin.jpg\"/>', 0);
INSERT INTO `tblpost` VALUES (12, 2, '2023-03-28', '14:33:52', '<h2 style=\"color:pink\">HEY', 0);
INSERT INTO `tblpost` VALUES (13, 2, '2023-04-03', '13:13:20', 'this is a reply', 11);
INSERT INTO `tblpost` VALUES (14, 2, '2023-04-03', '13:35:26', 'this is a reply to a reply', 13);
INSERT INTO `tblpost` VALUES (15, 3, '2023-04-03', '13:59:00', 'this is a reply to a reply to a reply', 14);
INSERT INTO `tblpost` VALUES (16, 3, '2023-04-03', '14:00:09', 'this is the 4th reply', 15);
INSERT INTO `tblpost` VALUES (18, 2, '2023-04-03', '14:04:25', 'BASED goblinposter', 17);
INSERT INTO `tblpost` VALUES (19, 2, '2023-04-03', '14:05:37', 'this is so sad post goblin <img src=\"https://previews.123rf.com/images/ratoca/ratoca1505/ratoca150500621/39986628-funny-goblin.jpg\">', 2);
INSERT INTO `tblpost` VALUES (20, 2, '2023-04-03', '14:06:46', 'goblinless behaviour', 1);
INSERT INTO `tblpost` VALUES (21, 4, '2023-04-04', '12:08:15', 'Lorem ipsum dolor sit amet, nonummy ligula volutpat hac integer nonummy. Suspendisse ultricies, congue etiam tellus, erat libero, nulla eleifend, mauris pellentesque. Suspendisse integer praesent vel, integer gravida mauris, fringilla vehicula lacinia non', 17);
INSERT INTO `tblpost` VALUES (22, 4, '2023-04-04', '12:09:45', '<a href=\"../../requirements.txt\">click me :)</a>', 0);
INSERT INTO `tblpost` VALUES (24, 1, '2023-04-04', '12:26:08', 'gobobobobobbolin', 21);
INSERT INTO `tblpost` VALUES (25, 1, '2023-04-04', '12:26:23', 'goboobalin', 24);
INSERT INTO `tblpost` VALUES (26, 1, '2023-04-04', '12:27:05', 'owo what is this post', 0);
INSERT INTO `tblpost` VALUES (27, 1, '2023-04-04', '12:27:21', '<h1>moshi moshi</h1>', 0);
INSERT INTO `tblpost` VALUES (31, 1, '2023-04-05', '12:38:02', 'god u people are boring', 14);
INSERT INTO `tblpost` VALUES (32, 1, '2023-04-05', '13:21:10', '<btn onclick=\"console.log(\'hello\')\">Hello!</btn>', 0);
INSERT INTO `tblpost` VALUES (38, 1, '2023-04-06', '09:11:40', 'god im so excited', 30);
INSERT INTO `tblpost` VALUES (39, 3, '2023-04-06', '09:31:39', 'me too', 38);
INSERT INTO `tblpost` VALUES (40, 2, '2023-05-29', '14:33:29', 'asdfasfdsfs', 32);
INSERT INTO `tblpost` VALUES (41, 4, '2023-05-30', '14:38:02', 'ikr', 20);

-- ----------------------------
-- Table structure for tblusers
-- ----------------------------
DROP TABLE IF EXISTS `tblusers`;
CREATE TABLE `tblusers`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `password` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `profile_picture` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'default_pfp.png',
  `admin` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of tblusers
-- ----------------------------
INSERT INTO `tblusers` VALUES (1, 'testuser', '30c952fab122c3f9759f02a6d95c3758b246b4fee239957b2d4fee46e26170c4', 'test@test.com', './userUploads/1.jpg', '1');
INSERT INTO `tblusers` VALUES (2, 'testuser2', '8e064b83fb2eeb241de2b432860997581e4149fc4d1ce186881314d8892bc7d4', 'test@gmail.com', 'default_pfp.png', '1');
INSERT INTO `tblusers` VALUES (3, 'testuser3', '30c952fab122c3f9759f02a6d95c3758b246b4fee239957b2d4fee46e26170c4', 'test3@test.com', 'default_pfp.png', '0');
INSERT INTO `tblusers` VALUES (4, 'flatearther2005', 'a20a2b7bb0842d5cf8a0c06c626421fd51ec103925c1819a51271f2779afa730', 'kylkeys@student.pakuranga.school.nz', 'default_pfp.png', '0');
INSERT INTO `tblusers` VALUES (7, 'xX_BASED_goblinPoster_Xx', 'f59ddf918f384a1b7e1d1011c49c3f3fd38421fc3ed3d90dfaa9bb1633325478', 'goblin@posts.com', './userUploads/7.webp', '0');
INSERT INTO `tblusers` VALUES (8, 'MrDanS_21', '796e43a5a8cdb73b92b5f59eb50610cea3efa8ce229cd7f0557983091b2b4552', 'ur.mom@mail.com', './userUploads/8.png', '0');
INSERT INTO `tblusers` VALUES (9, 'johnnywho', '358100c210df061db1f9a7a8945fa3140e169ddf67f7005c57c007647753e100', 'johvu@student.pakuranga.school.nz', 'default_pfp.png', '0');

-- ----------------------------
-- Table structure for testtbl
-- ----------------------------
DROP TABLE IF EXISTS `testtbl`;
CREATE TABLE `testtbl`  (
  `a` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of testtbl
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
