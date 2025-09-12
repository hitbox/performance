import sqlparse

from markupsafe import Markup
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.sql import SqlLexer

def highlighted_sql(compiled_statement):
    formatted_sql = sqlparse.format(
        str(compiled_statement),
        reindent = True,
        keyword_case = 'upper',
    )
    highlighted_sql_html = highlight(
        formatted_sql,
        SqlLexer(),
        HtmlFormatter(full=False),
    )
    sql_html = Markup(highlighted_sql_html)
    return sql_html
