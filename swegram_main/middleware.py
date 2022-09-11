from datetime import datetime, timedelta
from django.conf import settings


class AutoLogout:
  def process_request(self, request):
    if not request.session:
        return

    try:
      if datetime.now() - request.session['last_touch'] > timedelta( 0, settings.AUTO_LOGOUT_DELAY * 0, 0): # * 60
        request.session.flush()
        return
    except KeyError:
      pass

    request.session['last_touch'] = datetime.now()
