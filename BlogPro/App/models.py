from App.exts import db


# 文章分类
class ArticleClass(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    articles = db.relationship('Article', backref='my_article', lazy=True)


# 文章
class Article(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(20), unique=True)
    date = db.Column(db.DateTime)
    content = db.Column(db.String(2000))
    picture = db.Column(db.String(100))
    # 与文章分类进行关联
    article_class = db.Column(db.Integer, db.ForeignKey(ArticleClass.id))

# 用户
class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(50))
    sex = db.Column(db.String(20))




