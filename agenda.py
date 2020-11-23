import mysql.connector
from datetime import timedelta
from mysql.connector import pooling

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


class Agenda:
    def __init__(self, __people, __dispo, __indispo, __periode):
        self._dispo = []
        self._indispo = []
        self._start = __periode[0][0]
        self._end = __periode[0][1]
        self._vacation = __periode[0][2]
        self._people = []
        if self._vacation:
            self._vacation_start = __periode[0][3]
            self._vacation_end = __periode[0][4]
        for i in __dispo:
            self._dispo.append(Date(i))

        for i in __indispo:
            self._indispo.append(Date(i))

        for i in __people:
            self._people.append(User(i))

        self._agenda = []
        self.calc()

    def calc(self):
        delta = self._end - self._start
        vacation = []
        if self._vacation:
            v_delta = self._vacation_end - self._vacation_start
            v_delta = v_delta.days
            for i in range(v_delta + 1):
                vacation.append(self._vacation_start + timedelta(days=i))

        for i in range(delta.days + 1):
            date = self._start + timedelta(days=i)
            weekday = date.weekday()
            if date not in vacation and weekday != 5 and weekday != 6:
                self._agenda.append(Calendar(date))

        user = []

        for i in self._agenda:
            for j in self._dispo:
                if i.date == j.date and i.attribution is None and j.p_id not in user and i.date:
                    i.attribution = j.p_id
                    i.etape = 1
                    user.append(j.p_id)

        for i in range(delta.days + 1):
            date = self._start + timedelta(days=i)
            weekday = date.weekday()
            for people in self._people:
                if weekday == people.dis_day - 1:
                    self._dispo.append(Date((people.id, date)))
        for i in self._agenda:
            for j in self._dispo:
                if i.date == j.date and i.attribution is None and j.p_id not in user:
                    i.attribution = j.p_id
                    i.etape = 2
                    user.append(j.p_id)

        for i in self._agenda:
            for j in self._people:
                if i.attribution == j.id:
                    i.people = j

        print(self._agenda)


class Date:
    def __init__(self, data):
        self._date = data[1]
        self._p_id = data[0]

    def __repr__(self):
        to_print = f'Id : {self.p_id}\n'
        to_print += f'Date : {self._date.isoformat()}\n'
        to_print += f'Jour de la semaine : {WEEKDAYS[self._date.weekday()]}\n'
        return to_print

    @property
    def date(self):
        return self._date

    @property
    def p_id(self):
        return self._p_id


class Calendar:
    def __init__(self, date):
        self._attribution = None
        self._date = date
        self._people = None
        self._etape = 0

    @property
    def date(self):
        return self._date

    @property
    def attribution(self):
        return self._attribution

    @attribution.setter
    def attribution(self, user):
        self._attribution = user

    @property
    def people(self):
        return self._people

    @people.setter
    def people(self, user):
        self._people = user

    @property
    def etape(self):
        return self._etape

    @etape.setter
    def etape(self, etape):
        self._etape = etape

    def __repr__(self):
        return f'{self._date.isoformat()} : {self._people} (attribué à l\'étape {self._etape})\n'


class User:
    def __init__(self, __people):
        self._id = __people[0]
        self._name = f'{__people[1]} {__people[2]}'
        self._indis_day = __people[3]
        self._dis_day = __people[4]
        self._special = __people[5]
        self._p_indis = __people[6]
        self._n_day = __people[8]

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def indis_day(self):
        return self._indis_day

    @property
    def dis_day(self):
        return self._dis_day

    @property
    def special(self):
        return self._special

    @property
    def p_indis(self):
        return self._p_indis

    def __repr__(self):
        return f'id: {self._id} nom : {self._name}, jour dispo : {self._n_day}'


connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="poooll",
                                                              pool_size=1,
                                                              pool_reset_session=True,
                                                              host='localhost',
                                                              database='permanence',
                                                              user='root',
                                                              password='7aXqVk.83')

# Get connection object from a pool
connection_object = connection_pool.get_connection()

if connection_object.is_connected():
    cursor = connection_object.cursor(buffered=True)
    results = cursor.execute('CALL fetchPeople(1, 1)', multi=True)
    people = []
    dispo = []
    indispo = []
    periode = []
    try:
        for (i, cur) in enumerate(results):
            if cur.with_rows:
                if i == 0:
                    people = cursor.fetchall()
                if i == 1:
                    dispo = cursor.fetchall()
                elif i == 2:
                    indispo = cursor.fetchall()
                elif i == 3:
                    periode = cursor.fetchall()
    except Exception as e:
        pass
    Agenda(people, dispo, indispo, periode)
