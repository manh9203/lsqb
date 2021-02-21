SELECT count(*)
FROM
  Person,
  Forum,
  Comment,
  Post,
  Comment_hasTag_Tag
WHERE Forum.hasModerator_Person = Person.id
  AND Post.Forum_containerOf = Forum.id
  AND Post.id = Comment.replyOf_Post
  AND Comment.id = Comment_hasTag_Tag.id;
