from .models import Notification, FCMToken


def create_notification(recipient, title: str, body: str, notif_type: str, data: dict = None) -> Notification:
    n = Notification.objects.create(
        recipient=recipient, title=title, body=body,
        notif_type=notif_type, data=data or {},
    )
    _send_fcm(recipient, title, body, data or {})
    return n


def _send_fcm(user, title: str, body: str, data: dict):
    """
    FCM dispatch stub. Replace with actual firebase-admin SDK call.
    e.g.:
        import firebase_admin.messaging as fm
        tokens = list(FCMToken.objects.filter(user=user).values_list('token', flat=True))
        if tokens:
            msg = fm.MulticastMessage(notification=fm.Notification(title=title, body=body), tokens=tokens, data=data)
            fm.send_multicast(msg)
    """
    tokens = FCMToken.objects.filter(user=user).values_list('token', flat=True)
    if tokens:
        # TODO: plug in firebase-admin here
        Notification.objects.filter(recipient=user, fcm_sent=False, title=title).update(fcm_sent=True)


def notify_appointment_booked(appointment):
    create_notification(
        recipient=appointment.patient,
        title='Appointment Confirmed',
        body=f'Your appointment with Dr. {appointment.doctor.user.full_name} on {appointment.date} at {appointment.start_time} is confirmed.',
        notif_type=Notification.Type.APPOINTMENT_BOOKED,
        data={'appointment_id': appointment.id},
    )
    create_notification(
        recipient=appointment.doctor.user,
        title='New Appointment',
        body=f'New appointment from {appointment.patient.full_name} on {appointment.date} at {appointment.start_time}.',
        notif_type=Notification.Type.APPOINTMENT_BOOKED,
        data={'appointment_id': appointment.id},
    )


def notify_appointment_cancelled(appointment):
    create_notification(
        recipient=appointment.patient,
        title='Appointment Cancelled',
        body=f'Your appointment with Dr. {appointment.doctor.user.full_name} on {appointment.date} has been cancelled.',
        notif_type=Notification.Type.APPOINTMENT_CANCELLED,
        data={'appointment_id': appointment.id},
    )


def notify_appointment_reminder(appointment):
    create_notification(
        recipient=appointment.patient,
        title='Appointment Reminder',
        body=f'Reminder: You have an appointment with Dr. {appointment.doctor.user.full_name} on {appointment.date} at {appointment.start_time}.',
        notif_type=Notification.Type.APPOINTMENT_REMINDER,
        data={'appointment_id': appointment.id},
    )