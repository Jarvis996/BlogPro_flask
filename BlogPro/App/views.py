import datetime
import hashlib

from flask import Blueprint, render_template, session, request, redirect, url_for
from App.models import *

blue = Blueprint('blog', __name__)


# 首页
@blue.route('/')
def index():
    uname = session.get('uname', '')
    articles = Article.query.all()  # 文章内容对象集
    article_classs = ArticleClass.query.all()  # 文章分类对象集
    return render_template('home/index.html', articles=articles, article_classs=article_classs, uname=uname)


# 登陆
@blue.route('/login/', methods=['get', 'post'])
def login():
    uname = session.get('uname')
    if uname:
        return redirect(url_for('blog.add_category'))
    else:
        if request.method == 'POST':
            uname = request.form.get('uname')
            pwd = request.form.get('pwd')
            # 登陆验证用户名和密码
            users = User.query.filter_by(name=uname, password=pwd)
            print(users)
            if users.count() > 0:
                # 登陆成功后，保存登陆状态
                session['uname'] = uname
                return redirect(url_for('blog.add_category'))
            return render_template('admin/login.html')
    return render_template('admin/login.html')

# 注册
@blue.route('/register/', methods=['get', 'post'])
def register():
    if request.method == 'POST':
        uname = request.form.get('uname')
        pwd = request.form.get('pwd')
        sex = request.form.get('sex')
        users = User.query.filter_by(name=uname)
        if users.count() > 0:
            nameerro = ('用户:%s已存在，请重新输入！' % uname)
            return render_template('admin/register.html', nameerro=nameerro)
        elif sex not in ('男', '女'):
            sexerro = '性别输入有误!请重新输入'
            return render_template('admin/register.html', sexerro=sexerro)
        else:
            user = User()
            user.name = uname
            user.password = pwd
            user.sex = sex
            try:
                db.session.add(user)
                db.session.commit()
            except:
                db.session.rollback()
                db.session.flush()
                return "注册失败"
            # 如果注册成功，跳转到登陆页面
            good = '恭喜你，注册成功!'
            return render_template('admin/login.html', good=good)
    return render_template('admin/register.html')

# 退出
@blue.route('/logout/')
def logout():
    session.pop('uname')
    return redirect(url_for('blog.index'))


# 增加栏目
@blue.route('/add_category/', methods=['get', 'post'])
def add_category():
    uname = session.get('uname')
    if not uname:
        return redirect(url_for('blog.login'))
    if request.method == 'POST':
        class_name = request.form.get('category_name')
        article_class = ArticleClass.query.filter_by(name=class_name)
        if article_class.count()> 0:
            return "分类已存在，添加失败！"
        article_class = ArticleClass()
        article_class.name = class_name
        try:
            db.session.add(article_class)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return "栏目添加失败"

        # 如果添加成功，重定向到登陆页面

        return redirect(url_for('blog.add_category'))
    else:
        article_classs = ArticleClass.query.all()
        # for i in article_classs:
        #     art = Article.query.filter_by(article_class=i.id).count()
        #     i.num = art  # 将文章分类统计输入到数据库中
        return render_template('/admin/category.html', article_classs=article_classs)


# 删除栏目
@blue.route('/del_category/<article_class_id>/')
def del_category(article_class_id):
    classid = ArticleClass.query.get(article_class_id)
    articles = Article.query.filter_by(article_class=article_class_id)
    for article in articles: # 删除指定分类下的文章的对象
        db.session.delete(article)
        db.session.commit()
    try: # 删除这个分类
        db.session.delete(classid)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        return '删除失败1'

    return redirect(url_for('blog.add_category'))


# 修改栏目
@blue.route('/modify_category/<int:article_class_id>/',methods=['get', 'post'])
def modify_category(article_class_id):
    article_class = ArticleClass.query.get(article_class_id) # 获取该id名的文章栏目，传到页面
    if request.method == 'POST':
        article_class = ArticleClass.query.get(article_class_id) # 获得这个id的栏目对象
        print(article_class.name)
        article_class.name = request.form.get('category_name')
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
        return redirect(url_for('blog.add_category'))
    return render_template('/admin/update_category.html', article_class=article_class)


# 查看对应栏目
@blue.route('/article_class/<classid>/')
def article_class(classid):
    if not classid:
        classid = 1
    articles = Article.query.filter_by(article_class=classid)
    article = ArticleClass.query.get(classid)
    article_classs = ArticleClass.query.all()  # 文章分类对象集
    return render_template("home/list.html", articles=articles, article=article,article_classs=article_classs)

# 管理文章
@blue.route('/notice/')
def notice():
    articles = Article.query.all()
    return render_template('/admin/notice.html', articles=articles)

# 添加文章
@blue.route('/add_article/', methods=['get', 'post'])
def add_article():
    article_classs = ArticleClass.query.all()
    if request.method == 'POST':
        article = Article()
        article.title = request.form.get('art_title')
        article.content = request.form.get('art_content')
        article.date = datetime.datetime.now()
        # article.Introduction = article.content[0:20]
        article.picture = request.form.get('art_picture')
        article.article_class = request.form.get('article_class')
        try:
            db.session.add(article)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
            return '添加文章失败'
    return render_template('admin/add_article.html', article_classs=article_classs)

# 删除文章
@blue.route('/del_article/<article_id>/')
def del_article(article_id):
    print(article_id)
    article = Article.query.get(article_id)
    try:
        db.session.delete(article)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        return "删除失败"

    return redirect(url_for('blog.notice'))

# 修改文章
@blue.route('/modify_article/<int:article_id>/', methods=['get', 'post'])
def modify_article(article_id):
    articles = ArticleClass.query.all() # 获取所有的文章分类，显示在页面上
    old_article = Article.query.get(article_id) # 获取当前id文章的内容集
    if request.method == 'POST':
        article = Article.query.get(article_id)
        article.title = request.form.get('article_title')
        article.content = request.form.get('article_content')
        article.picture = request.form.get('article_picture')
        article.article_class = int(request.form.get('article_article_class'))
        print(article.article_class,type(article.article_class))
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.flush()
        return redirect(url_for('blog.notice'))
    return render_template('admin/update_article.html', old_article=old_article, articles=articles)


# 我的相册
@blue.route('/my_picture/')
def my_picture():
    articles = Article.query.all()
    return render_template('/home/share.html', articles=articles)

# # 可替换的功能界面
# @blue.route('/non_url/')
# def non_url():
#     return render_template('/home/non_url.html')


# ==================密码加密函数(暂时未用)=================
def my_md5(string):
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()



