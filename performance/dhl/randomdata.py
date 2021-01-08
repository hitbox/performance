import random
import string

from .models import Report
from .models.crewinfo import CrewInfo

crew_info_list = list(CrewInfo)

def _word(min=3, max=9):
    length = random.randint(min, max)
    return ''.join(random.sample(string.ascii_lowercase, length))

def _sentence():
    nwords = random.randint(3, 12)
    words = ' '.join(_word() for _ in range(nwords))
    words += random.choice(string.punctuation)
    return words

def _paragraph():
    n = random.randint(1, 4)
    return ' '.join(_sentence() for _ in range(n))

def random_report(date):
    report = Report(
        date = date,
        system_detail = _paragraph(),
        charter_detail = _paragraph(),
        extra_section_detail = _paragraph(),
        ferry_flight_detail = _paragraph(),

        aircraft_spares_1200 = random.randint(1,10),
        aircraft_spares_1800 = random.randint(1,10),
        aircraft_spares_2000 = random.randint(1,10),
        aircraft_spares_0300 = random.randint(1,10),

        crew_info_1200 = random.choice(crew_info_list),
        crew_info_1800 = random.choice(crew_info_list),
        crew_info_2000 = random.choice(crew_info_list),
        crew_info_0300 = random.choice(crew_info_list),

        abx_amazon_previous_days_performance_percent = 10 / random.randint(1, 10),
        abx_amazon_previous_days_performance_lanes = random.randint(1, 10),
        abx_amazon_previous_days_performance_late = random.randint(1, 10),
        abx_amazon_arrival_performance_mtd_percent = 10 / random.randint(1, 10),
        abx_amazon_arrival_performance_mtd_lanes = random.randint(1, 10),
        abx_amazon_arrival_performance_mtd_late = random.randint(1, 10),
        abx_amazon_days_at_100_percent = random.randint(1, 10),
        abx_amazon_qtd_performance_percent = 10 / random.randint(1, 10),
        abx_amazon_qtd_performance_lanes = random.randint(1, 10),
        abx_amazon_qtd_performance_late = random.randint(1, 10),

    )
    return report
