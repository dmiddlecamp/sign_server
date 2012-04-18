'''
Created on Apr 17, 2012

@author: robert
'''
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils.datetime_safe import datetime as safe_datetime
from sign_server import peggy_tasks
from sign_server.models import BoardLease
import json
import md5


def has_current_lease(lease_code):
    search = BoardLease.objects.filter(end_date__gte=safe_datetime.now())
    search.filter(board_lease_code=lease_code)
    return search.count() > 0


def get_lease(request, term):
    response_data = dict()

    term = int(term)
    if term > 10:
        term = 10

    search = BoardLease.objects.filter(end_date__gte=safe_datetime.now())

    if search.count() > 0:
        response_data['result'] = 'failure'
    else:
        m = md5.new()
        m.update(unicode(datetime.now().microsecond.__str__))
        lease_code = m.hexdigest()

        lease_expiry = datetime.now() + timedelta(seconds=term * 60)
        new_lease = BoardLease(board_lease_code=lease_code, is_active=True, start_date=datetime.now(), end_date=lease_expiry, creation_date=datetime.now())
        new_lease.save()

        response_data['result'] = 'success'
        response_data['lease_code'] = lease_code
        response_data['lease_expiry'] = str(lease_expiry)

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def clear_board(request, lease_code, row):
    response_data = dict()
    if has_current_lease(lease_code) == False:
        response_data['result'] = "failure"
    else:
        peggy_tasks.clear_board(row)
        response_data['result'] = "success"

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def write_to_board(request, lease_code, row, col, msg):
    response_data = dict()
    if has_current_lease(lease_code) == False:
        response_data['result'] = "failure"
    else:
        peggy_tasks.write_to_board(int(row), int(col), msg)
        response_data['result'] = "success"

    return HttpResponse(json.dumps(response_data), mimetype="application/json")

