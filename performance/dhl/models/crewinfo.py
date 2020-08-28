import enum

from sqlalchemy_utils import ChoiceType

from performance.extensions import db

class CrewInfo(enum.Enum):
    FULL_CREW = 0
    CAPTAIN_ONLY = 1
    FIRST_OFFICER_ONLY = 2
    NONE = 3

    def __str__(self):
        return self.label


CrewInfo.FULL_CREW.label = 'Full Crew'
CrewInfo.CAPTAIN_ONLY.label = 'Captain Only'
CrewInfo.FIRST_OFFICER_ONLY.label = 'First Officer Only'
CrewInfo.NONE.label = '(None)'

def make_crew_info_column(label):
    return db.Column(
        ChoiceType(
            CrewInfo,
            impl = db.Integer()),
        default = CrewInfo.NONE,
        info = dict(
            label = label,
        )
    )
