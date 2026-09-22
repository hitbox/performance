import sqlalchemy as sa

def first_working_url(url_list):
    """
    Return the first url that connects.
    """
    for url in url_list:
        try:
            engine = sa.create_engine(url)
            with engine.connect() as connection:
                return url
        except Exception as e:
            pass
