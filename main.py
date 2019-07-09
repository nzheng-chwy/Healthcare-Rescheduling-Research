# 1. Create tensor structure to store appointment data for given range of days.
# 2. Use SQLite to create dummy data to build distributions from for patient
# demand for appointments (by day/time).
# 3. Use Python to connect to SQLite database to convert data into distribution
# for sampling purposes.
# 4. Create parameter for "rate of flexibility" to indicate how willing patients
# are to reschedule.
# 5. implement cancellations
# 6. keep track of no shows
# 7. simulate rescheduling

# generates patient "arrival rates" Poisson distribution regarding making
# appointments by day.

import os.path
import sqlite3 as sql
from sqlite3 import Error
import numpy as np
import scipy as sp
from datetime import datetime

# The current directory of program files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# The address of the database containing appointment data in SQLite.
APPOINTMENT_DATABASE = os.path.join(BASE_DIR, "data\\Appointment_Data.db")
# number of appointment slots per day.
NUM_SLOTS = 10
# number of days out you want to keep track of for appointment scheduling.
NUM_DAYS = 14
# number of iterations of the simulations (days).
NUM_ITERS = 100
# expected proportion of people who will accept a reschedule by clinic.
FLEX_RATE = 0.2


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sql.connect(db_file)
        # Setting row_factory allows for data access in rows using row names.
        conn.row_factory = sql.Row
        return conn
    except Error as e:
        print(e)

    return None


def executeQuery(conn, query):
    """
    Execute query string [query] on database that is connected to in [conn]
    :param conn: the Connection object
    :param query: the query string to execute
    :return: the Cursor object containing result from query execution
    """
    cur = conn.cursor()
    cur.execute(query)
    return cur


# creates initial empty schedule
def createSchedule():
    # initiate all values in matrix to -1, indicating no lead-time exists yet
    schedule = np.full((NUM_SLOTS, NUM_DAYS), -1)
    return schedule


# retrieves data from database and creates distribution for appointment
def arrivalRates(conn):
    """
    Creates dictionary containing all appointments mades grouped by 
    tuple (lead days, time of appointment). Used as a distribution to 
    sample from to determine what patients will book. 
    :param cursor: the Cursor object containing appointment query results
    :return: the dictionary containing all appointment counts
    """

    cursor = executeQuery(conn, """SELECT ScheduleDate, COUNT(ScheduleDate) AS 
                                   NumApptMade FROM AggregateAppointmentData
                                   GROUP BY ScheduleDate""")
    num_days = np.zeros(7)
    num_arrivals = np.zeros(7)

    for row in cursor:

    mean_arrivals = np.array(7)
    for i in len(num_days):
        mean_arrivals[i] = num_arrivals[i]/num_days[i] if num_days != 0 else 0
    return mean_arrivals


# retrieves data from database and creates distribution for appointment rates based
# on number of days out and slot position. There should be a mean number of
# people who arrive
def appointmentRates(conn):
    """
    Creates dictionary containing all appointments mades grouped by 
    tuple (lead days, time of appointment). Used as a distribution to 
    sample from to determine what patients will book. 
    :param cursor: the Cursor object containing appointment query results
    :return: the dictionary containing all appointment counts
    """

    cursor = executeQuery(conn, "SELECT * FROM AggregateAppointmentData")
    appointmentDict = {}

    for row in cursor:
        # The date on which an appointment was made, not the appointment itself.
        schedule_date_str = row["ScheduleDate"]
        # The date and time of the actual scheduled appointment.
        appointment_date_str = row["ActualApptDate"]
        appointment_time_str = row["ActualApptTime"]
        # Converts Date/Time strings extracted from table into DateTime type.
        schedule_date = datetime.strptime(schedule_date_str, '%Y-%m-%d')
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d')
        appointment_time = datetime.strptime(appointment_time_str, '%H:%M')
        # Calculate lead time (days) between day of scheduling and appointment.
        lead_days = (appointment_date - schedule_date).days
        # Converts appointment time into 24-hour (hour:minute) notation for
        # readability.
        appointment_hour_min = str(appointment_time.hour) + ":" + \
            str('{:>02d}'.format(appointment_time.minute))
        # Creates a tuple (lead-days, appointment-time) to insert into
        # frequency distribution "appointmentDict".
        days_time_tuple = (lead_days, appointment_hour_min)
        if(days_time_tuple in appointmentDict):
            appointmentDict[days_time_tuple] += 1
        else:
            appointmentDict[days_time_tuple] = 1

    return appointmentDict


# retrives data from database and creates distribution for cancellation rates
# based on number of days out, slot position, and lead time of appointment.
def cancelRates():
    return


# retrives data from database and creates distribution for rebooking rates
# based on number of days out, slot position, and lead time of appointment.
def rebookRates():
    return


# based on day, use poisson distribution to find number of people that arrive,
# then given that number, sample from distribution for appointment preference
# for each person (can sample for multiple preferences as proxy for order of
# preference)
def arrivals(schedule, queue):
    return


def simulate(schedule, queue, iterations):
    empty_slots = 0
    first_choice = 0
    second_choice = 0
    arrival_dist = appointmentRates()
    cancel_dist = cancelRates()
    rebook_dist = rebookRates()
    for iter in range(iterations):
        sch_postarrival, patient_queue = arrivals(schedule, queue)
    return


# Main function call. Operates as follows:
# 1. Create matrix representation of empty appointment schedule.
if __name__ == "__main__":

    database_conn = create_connection(APPOINTMENT_DATABASE)
    arrival_distribution = arrivalRates(database_conn)
    appointment_distribution = appointmentRates(database_conn)

  #  print(appointment_distribution)
  #  schedule = createSchedule()
  #  simulate(schedule, NUM_ITERS)

  # CONCEPT: Use neural nets to create fitted model for predicting number of
  # requested appts for a given slot.
  # CONCEPT #2: Use Holt-Winters seasonal/trend data to capture seasonal appt
  # changes and mean changes (for example, if more/less people get sick over time
  # due to pandemics or better preventative care)
