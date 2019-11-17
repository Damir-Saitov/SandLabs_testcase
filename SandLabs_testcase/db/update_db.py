import datetime
from urllib import request
import re

from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///db/valuta_table')

Base = declarative_base()
class Valuta(Base):
    __tablename__ = 'valuta_table'
    name = Column(String(3), primary_key=True)
    course = Column(Float)
    fullname = Column(String(100))

    def __init__(self, name, course, fullname):
        self.name = name
        self.course = course
        self.fullname = fullname

    def __str__(self):
        return '{}({}) - {}'.format(self.fullname, self.name, self.course)

    def __repr__(self):
        return 'Valuta({}, {}, {})'.format(self.name, self.course, self.fullname)
Base.metadata.create_all(engine)

def get_valuta_data():
    with request.urlopen(
            'http://www.cbr.ru/currency_base/daily/?date_req=' +
            str(datetime.date.today()).replace('-', '.')
            ) as page:
        page = page.read().decode('utf-8')

        valuta = tuple(
            i[4:len(i) - 5]
            for i in re.findall(r'<td>.*</td>', page)
            )
    return valuta

def create_db():
    valuta = get_valuta_data()

    Session = sessionmaker(bind=engine)
    session = Session()
    for i in range(0, len(valuta), 5):
        session.add(
            Valuta(
                valuta[i + 1],
                round(float(valuta[i + 4].replace(',', '.')) / int(valuta[i + 2]), 4),
                valuta[i + 3]
            )
        )
            
    session.commit()

def update_valuta_course():
    valuta = get_valuta_data()
    valuta = tuple((valuta[i + 2], valuta[i + 4]) for i in range(0, len(valuta), 5))
        
    Session = sessionmaker(bind=engine)
    session = Session()
    for v, c in zip(session.query(Valuta).all(), valuta):
        v.course = round(float(c[1].replace(',', '.')) / int(c[0]), 4)
            
    session.commit()
        

if __name__ == '__main__':
    create_db()