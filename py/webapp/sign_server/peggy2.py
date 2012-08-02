'''
Created on Aug 1, 2012

@author: robert
'''
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils.datetime_safe import datetime as safe_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from sign_server import peggy_tasks
from sign_server.models import BoardLease
import json
import md5

MAX_LEASE_SECONDS = 600

def get_current_lease(lease_code):
    search = BoardLease.objects.filter(end_date__gte=safe_datetime.now())
    search.filter(board_lease_code=lease_code)
    try:
        return search.get()
    except BoardLease.DoesNotExist:
        return None

def add_lease_expiration(response_data, lease):
    seconds_remaining = datetime.now() - lease.start_date
    response_data["lease_seconds_remaining"] = int(seconds_remaining.total_seconds())

def get_lease(request, term=60, top_row=0, left_col=0, bottom_row=11, right_col=79):
    response_data = dict()

    term = int(term)
    if term > MAX_LEASE_SECONDS:
        term = MAX_LEASE_SECONDS

    search = BoardLease.objects.filter(end_date__gte=safe_datetime.now())

    if search.count() > 0:
        generate_error(response_data, "in_use")
    else:
        m = md5.new()
        m.update(unicode(datetime.now().microsecond.__str__))
        lease_code = m.hexdigest()

        lease_expiry = datetime.now() + timedelta(seconds=term)
        new_lease = BoardLease(board_lease_code=lease_code, is_active=True, start_date=datetime.now(), end_date=lease_expiry, creation_date=datetime.now())
        new_lease.save()

        response_data['result'] = 'success'
        response_data['lease_code'] = lease_code
        response_data['lease_expiry'] = str(lease_expiry)
        add_lease_expiration(response_data, new_lease)

    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def renew_release(request, lease_code, term=1):
    response_data = dict()
    board_lease = get_current_lease(lease_code)
    if board_lease == None:
        generate_error(response_data, "bad_lease_code")
    else:
        lease_expiry = datetime.now() + timedelta(seconds=term)
        board_lease.end_date = lease_expiry
        board_lease.save()

        response_data['result'] = 'success'
        response_data['lease_code'] = lease_code
        response_data['lease_expiry'] = str(lease_expiry)
        add_lease_expiration(response_data, new_lease)

    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def expire_lease(request, lease_code):
    response_data = dict()
    board_lease = get_current_lease(lease_code)
    if board_lease is None:
        response_data['result'] = 'failure'
        response_data['reason_code'] = 'bad_lease_code'
    else:
        board_lease.end_date = datetime.now()
        board_lease.save()
        response_data['result'] = 'success'

    return HttpResponse(json.dumps(response_data), mimetype='application/json')


def clear_board(request, lease_code, row=None):
    response_data = dict()
    board_lease = get_current_lease(lease_code)
    if board_lease == None:
        generate_error(response_data, "bad_lease_code")
    else:
        peggy_tasks.clear_board(row)
        response_data['result'] = "success"
        add_lease_expiration(response_data, board_lease)

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@require_http_methods(["GET", "POST"])
@csrf_exempt
def write_to_board(request, lease_code=1, row=0, col=0, msg=''):
    if request.method == 'POST':
        lease_code = request.POST['lease_code']
        row = request.POST['row']
        col = request.POST['col']
        msg = request.POST['msg']
    response_data = dict()
    board_lease = get_current_lease(lease_code)
    if board_lease == None:
        generate_error(response_data, "bad_lease_code")
    else:
        peggy_tasks.write_to_board(int(row), int(col), board_lease.current_color + msg)
        response_data['result'] = "success"
        add_lease_expiration(response_data, board_lease)

    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def set_color(request, lease_code=1, color='green'):
    response_data = dict()
    board_lease = get_current_lease(lease_code)
    if board_lease == None:
        generate_error(response_data, "bad_lease_code")
    else:
        new_color = None
        if color == 'green':
            new_color = chr(29)
        elif color == 'red':
            new_color = chr(30)
        elif color == 'orange':
            new_color = chr(31)
        else:
            generate_error(response_data, "unknown_color")

        if new_color != None:
            board_lease.current_color = new_color
            response_data['result'] = "success"
            add_lease_expiration(response_data, board_lease)
            board_lease.save()

    return HttpResponse(json.dumps(response_data), mimetype="application/json")

def generate_error(response_data, reason_code):
    response_data['result'] = "failure"
    response_data['reason_code'] = reason_code
