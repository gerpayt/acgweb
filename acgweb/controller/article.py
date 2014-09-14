# coding: utf-8
from flask import render_template, json, abort, flash, make_response
from acgweb import app, db
from acgweb.model.article import Article
#from acgweb.model.category import Category
from acgweb.form.article import ArticleForm
import acgweb.const as CONST
from decorated_function import *

@app.route('/articlelist-cate<int:cateid>-p<int:pagenum>')
@app.route('/articlelist-cate<int:cateid>')
@app.route('/articlelist-p<int:pagenum>')
@app.route('/articlelist')
@login_required
def articlelist(pagenum=1,cateid=0):
    """Page: all articles"""
    category_list = CONST.article_category
    if cateid :
        article_count = Article.query.filter(Article.cate_id==cateid).count()
        article_list = Article.query.filter(Article.cate_id==cateid).order_by('posttime DESC').limit(CONST.article_per_page).offset(CONST.article_per_page*(pagenum-1)).all()
    else:
        article_count = Article.query.count()
        article_list = Article.query.order_by('posttime DESC').limit(CONST.article_per_page).offset(CONST.article_per_page*(pagenum-1)).all()
    if viewtype()==1:
        return render_template('article/articlelist_mobile.html',
            article_list=article_list,
            page_count=(article_count-1)/CONST.article_per_page+1,page_current=pagenum,cateid=cateid,category_list=category_list)
    else:
        return render_template('article/articlelist.html',
            article_list=article_list,
            page_count=(article_count-1)/CONST.article_per_page+1,page_current=pagenum,cateid=cateid,category_list=category_list)


@app.route('/api/articlelist')
#@login_required
def articlelistapi():
    article_list = Article.query.order_by('posttime DESC').all()
    res = []
    for article in article_list:
        d = {}
        d['id'] = article.id
        d['title'] = article.title
        d['cate_id'] = article.cate_id
        res.append(d)
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/articlemanage-p<int:pagenum>')
@app.route('/articlemanage')
@login_required
def articlemanage(pagenum=1):
    """Page: all articles"""
    if not session.get('is_arra_monitor'):
        abort(403)
    category_list = CONST.article_category
    article_count = Article.query.count()
    article_list = Article.query.order_by('posttime DESC').limit(CONST.article_per_page).offset(CONST.article_per_page*(pagenum-1))
    return render_template('article/articlemanage.html',
        article_list=article_list,
        page_count=(article_count-1)/CONST.article_per_page+1,page_current=pagenum,category_list=category_list)


@app.route('/article-<article_title>', methods=['GET', 'POST'])
@login_required
def articledetail(article_title):
    """Page: article detail"""
    category_list = CONST.article_category
    try:
        article_detail = Article.query.filter(Article.title == article_title).one()
    except:
        abort(404)
    #print Article.query.filter(Article.title==article_title).statement
    if viewtype()==1:
        return render_template('article/articledetail_mobile.html', article_detail=article_detail,category_list=category_list)
    else:
        return render_template('article/articledetail.html', article_detail=article_detail,category_list=category_list)


@app.route('/api/articledetail-<article_title>')
#@login_required
def articledetailapi(article_title):
    article = Article.query.filter(Article.title == article_title).one()
    d = {}
    d['id'] = article.id
    d['title'] = article.title
    d['cate_id'] = article.cate_id
    d['posttime'] = article.posttime
    d['content'] = article.content
    res = d
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/articleedit', methods=['GET', 'POST'])
@app.route('/articleedit-<int:article_id>', methods=['GET', 'POST'])
@login_required
def articleedit(article_id=0):
    if not session.get('is_arra_monitor'):
        abort(403)
    category_list = CONST.article_category
    if request.method == 'POST':
        form = ArticleForm(request.form)
        if form.validate_on_submit():
            if Article.query.filter(Article.title==form.title.data,Article.id!=form.id.data).count():
                form.title.errors.append('标题已存在')

        if not form.errors:
            article = Article.query.get(form.id.data)
            if not article: article = Article()
            article.title=form.title.data
            article.cate_id=form.cate_id.data
            article.content=form.content.data
            db.session.add(article)
            db.session.commit()

            flash({'type':'success', 'content':'保存成功！'})
            return redirect('/articlemanage')
        return render_template('article/articleedit.html', form=form,category_list=category_list)
    else:
        article = Article.query.get(article_id)
        form = ArticleForm(obj=article)

        return render_template('article/articleedit.html', form=form,category_list=category_list)



@app.route('/articledelete-<int:article_id>')
@login_required
def articledelete(article_id):
    """Page: activity detail"""
    if not session.get('is_arra_monitor'):
        abort(403)
    article = Article.query.get(article_id)
    flash({'type':'success', 'content':'文章已删除。'})
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('articlemanage'))


