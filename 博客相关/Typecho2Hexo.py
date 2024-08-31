# -*- coding: utf-8 -*-

import os
import sqlite3
import arrow
from box import Box

def create_data(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn.row_factory = dict_factory

    cursor = conn.cursor()

    # 创建分类和标签
    cursor.execute("SELECT type, slug, name FROM typecho_metas")
    categories = cursor.fetchall()
    for cate in categories:
        cate = Box(cate)
        path = f'data/{cate.slug}'
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f'{path}/index.md', 'w', encoding="utf-8") as f:
            f.write(f"title: {cate.slug}\n")
            f.write(f"date: {arrow.now().format('YYYY-MM-DD HH:mm:ss')}\n")
            if cate.type == 'category':
                f.write('type: "categories"\n')
            elif cate.type == 'tag':
                f.write('type: "tags"\n')
            f.write("comments: true\n")
            f.write("---\n")

    # 创建文章
    cursor.execute("SELECT cid, title, slug, text, created FROM typecho_contents WHERE type='post'")
    entries = cursor.fetchall()
    for e in Box(entries):
        title = e.title.strip()
        urlname = f'/archives/{e.slug}/'
        print(title)
        content = str(e.text).replace('<!--markdown-->', '')

        # 找出文章的tag及category
        cursor.execute("SELECT type, name, slug FROM typecho_relationships ts JOIN typecho_metas tm ON tm.mid = ts.mid WHERE ts.cid = ?", (e.cid,))
        metas = cursor.fetchall()

        tags = []
        category = ""
        for m in Box(metas):
            if m.type == 'tag':
                tags.append(m.name)
            if m.type == 'category':
                category = m.slug

        # 创建文章目录和文件
        created_date = arrow.get(e.created)
        path = f'data/_posts/{created_date.format("YYYY")}/{created_date.format("MMDD")} {title.replace("/", "-")}'
        os.makedirs(path, exist_ok=True)
        
        with open(f"{path}/index.md", 'w', encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"title: {title}\n")
            f.write(f"date: {created_date.format('YYYY-MM-DD HH:mm:ss')}\n")
            f.write(f"category: {category}\n")
            f.write(f"tags: [{','.join(tags)}]\n")
            f.write(f"permalink: {urlname}\n")
            f.write("---\n")
            f.write(content)

    conn.close()

def main():
    db_path = '/root/应用/typecho/65dafd493903e.db'
    create_data(db_path)

if __name__ == "__main__":
    main()
