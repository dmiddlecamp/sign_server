# Create your views here.
from django.shortcuts import render_to_response
from django.utils.datetime_safe import strftime
from robertsTest.models import FooMessage
import datetime

def all_messages(request):
    thisMessage = FooMessage(message_text='Test Message created on ' + strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
    thisMessage.save()
    messages = FooMessage.objects.all()
    return render_to_response('robertsTest/messages.html', {'messages': messages})

