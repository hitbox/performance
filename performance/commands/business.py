import datetime as dt

from flask.cli import AppGroup

from .. import business
from ..extensions import db
from ..models import Flight
from ..models import Report
from ..utils import quarter_of_date

business_cli = AppGroup('business')

def query_to_dict(query):
    result = db.session.execute(query)
    return result.mappings().first()

@business_cli.command('performance')
def performance():
    date = dt.date(2022,6,1)
    result = business.performance_details(date)
    from pprint import pprint
    pprint(result)

    import code
    code.interact(local=locals())
