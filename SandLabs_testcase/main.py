import urllib
import re
from json import loads

from sanic import Sanic
from sanic.response import json, text, html

from db.update_db import sessionmaker, engine, Valuta, update_valuta_course

app = Sanic(__name__)

@app.route("/")
async def index(request):
    return html(open('template/main.html', 'r').read())

@app.route('/api/course/<currency:string>', methods=['GET'])
async def get(request, currency):
    try:
        course = await get_course(currency)
    except ValueError as ve:
        return text(ve)
    return json({'currency': currency, 'rub_course': course})

@app.route('/api/convert', methods=['POST'])
async def post(request):
    data = loads(request.form.get('json'))

    try:
        from_course = await get_course(data['from_currency'])
        to_course = await get_course(data['to_currency'])
    except ValueError as ve:
        return text(ve)

    return json({
        'currency': data['to_currency'],
        'amount': round(to_course/from_course * data['amount'], 4)
        })

async def get_course(valuta_name):
    Session = sessionmaker(bind=engine)
    session = Session()
    if valuta_name == 'RUB':
        return 1
    else:
        valuta = session.query(Valuta).filter_by(name=valuta_name).first()
        if valuta is None:
            raise ValueError('Currency is not found: ' + valuta_name)
        return valuta.course

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4)

    update_valuta_course()
