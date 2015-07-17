#
# Database access functions for the web forum.
# 

import psycopg2


# Get posts from database.
def get_all_posts():  # Database connection
    """
    Retrieves all posts from the SQL DB
    :return posts:
    """

    DB = psycopg2.connect("dbname=forum")
    c = DB.cursor()
    c.execute("SELECT * FROM posts")
    posts = ({'content': str(row[1]), 'time': str(row[0])}
             for row in c.fetchall())
    return posts

# Add a post to the database.
def add_post(content):
    """
    Adds a post to the SQL DB and returns no value
    :param content:
    :return none:
    """
    DB = psycopg2.connect("dbname=forum")
    c = DB.cursor()
    c.execute("INSERT INTO posts (content) VALUES (%s)", (content,))
    c.execute("DELETE FROM posts WHERE content LIKE '%cheese%'")
    DB.commit()
    DB.close()


def truncate_posts():
    """
    Removes all entries from posts table
    :return:
    """
    DB = psycopg2.connect("dbname=forum")
    c = DB.cursor()
    c.execute("TRUNCATE posts")
    DB.commit()
    DB.close()


