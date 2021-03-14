DROP VIEW IF EXISTS Message;
DROP VIEW IF EXISTS Comment_replyOf_Message;
DROP VIEW IF EXISTS Message_hasCreator_Person;
DROP VIEW IF EXISTS Message_hasTag_Tag;
DROP VIEW IF EXISTS Message_isLocatedIn_Country;
DROP VIEW IF EXISTS Person_likes_Message;

DROP TABLE IF exists Company;
DROP TABLE IF exists University;
DROP TABLE IF exists Continent;
DROP TABLE IF exists Country;
DROP TABLE IF exists City;
DROP TABLE IF exists Forum;
DROP TABLE IF exists Comment;
DROP TABLE IF exists Post;
DROP TABLE IF exists Person;
DROP TABLE IF exists Comment_hasTag_Tag;
DROP TABLE IF exists Post_hasTag_Tag;
DROP TABLE IF exists Forum_hasMember_Person;
DROP TABLE IF exists Forum_hasTag_Tag;
DROP TABLE IF exists Person_hasInterest_Tag;
DROP TABLE IF exists Person_likes_Comment;
DROP TABLE IF exists Person_likes_Post;
DROP TABLE IF exists Person_studyAt_University;
DROP TABLE IF exists Person_workAt_Company;
DROP TABLE IF exists Person_knows_Person;
