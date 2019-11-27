from pyfcm import FCMNotification
from models.notifications import Notifications


def notify(title, body, method, signals):
    try:
        api_key = "AAAAfxesG-s:APA91bHvbIoNvNZyYD3iQkImdmfnnOtFWmk2i3CiIcuOCzid3AbAPMZFBxpo4lT5_nyS4su-WrJ_lY5UuC2PmMhzwYlaxaLBgygb0nD6yIhZEReGQOgZvMwymrQf9LLeEUdSsQwb-qNL"

        push_service = FCMNotification(api_key=api_key)
        users = method_selector(method)
        print(users)
        signal = {"signals": signals}
        registration_ids = list(set(users))

        # registration_ids = [
        #     "exBMphU67DY:APA91bGgytkweyDk1NTJAbRcfeG2M8xdMlWmwKvPLaj8IK8zRKONKKbbp07BQ5HvkqudFG106q-KoTLBtBz1IfEOt0-AMW_faBxgrII8SabQUCieySCezoLyq8AVd8BsvTdc_wYbMDn5",
        #     "eSW2NjDorXA:APA91bHHhCtTlMDsmk7y_X_wHfkQwZZs_-0YgYv-gM5m4GJLknzlZ1J8I-hbdHz4h7igl8RSrr8kkNgspvWIefVGZqu_JyDlZ6iLy79I-gpg3yVEDXuHw8Aj8MGSttWinVZeIlIwrwFQ"]

        message_title = title
        message_body = body
        extra_kwargs = {
            'priority': 'high',
            'signal'  : signal,
        }
        result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title,
                                                      message_body=message_body, extra_kwargs=extra_kwargs)

        print(result)
        return True
    except Exception as e:
        print(e)
        return False


def method_selector(method):
    if method == "cause_list":
        users = [row.device_id for row in Notifications.query.filter_by(cause_list=True)]
        return users
    elif method == "nominated_counsel":
        users = [row.device_id for row in Notifications.query.filter_by(nominated_counsel=True)]
        return users
    elif method == "judges_roster":
        users = [row.device_id for row in Notifications.query.filter_by(judges_roster=True)]
        return users
