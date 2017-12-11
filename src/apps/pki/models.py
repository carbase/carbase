from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session


def do_stuff(sender, user, request, **kwargs):
    sessions = Session.objects.all()
    for session in sessions:
        not_this_session = session.pk != request.session._get_session_key()
        this_user_session = session.get_decoded().get('_auth_user_id') == str(user.id)
        print(not_this_session, this_user_session)
        if (not_this_session and this_user_session):
            session.delete()


user_logged_in.connect(do_stuff)


class RevokedCertificate(models.Model):
    ''' Сертификаты отозванные НУЦ РК '''
    serial_number = models.CharField(max_length=64)
    revocation_date = models.DateTimeField()
