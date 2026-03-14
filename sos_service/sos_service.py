from django.utils import timezone
from .models import SOSAlert, SOSStatusLog
from notifications_service.notification_service import create_notification
from notifications_service.models import Notification
from hospital_service.models import Hospital
import math


def _log(sos: SOSAlert, to_status: str, changed_by=None, note: str = '') -> None:
    SOSStatusLog.objects.create(
        sos=sos,
        from_status=sos.status,
        to_status=to_status,
        changed_by=changed_by,
        note=note,
    )


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(float(lat1))) *
         math.cos(math.radians(float(lat2))) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def create_sos(patient, data: dict) -> SOSAlert:
    """
    Create a new SOS alert and notify all nearby hospitals (within 30 km)
    that have emergency beds available.
    """
    sos = SOSAlert.objects.create(
        patient=patient,
        latitude=data['latitude'],
        longitude=data['longitude'],
        address=data.get('address', ''),
        severity=data.get('severity', SOSAlert.Severity.HIGH),
        description=data.get('description', ''),
        blood_group=data.get('blood_group', ''),
        allergies=data.get('allergies', ''),
        medications=data.get('medications', ''),
        emergency_contact_name=data.get('emergency_contact_name', ''),
        emergency_contact_phone=data.get('emergency_contact_phone', ''),
        status=SOSAlert.Status.ACTIVE,
    )
    _log(sos, SOSAlert.Status.ACTIVE, changed_by=patient, note='SOS triggered by patient')

    # Notify nearby hospitals
    nearby = Hospital.objects.filter(
        status=Hospital.Status.ACTIVE,
        latitude__isnull=False,
        longitude__isnull=False,
    )
    notified = 0
    for h in nearby:
        dist = _haversine_km(data['latitude'], data['longitude'], h.latitude, h.longitude)
        if dist <= 30:
            create_notification(
                recipient=h.user,
                title=f'🚨 SOS ALERT — {data.get("severity", "high").upper()}',
                body=(
                    f'Emergency from {patient.full_name} '
                    f'({dist:.1f} km away). '
                    f'{data.get("description", "Medical emergency.")} '
                    f'Tap to respond.'
                ),
                notif_type='sos_alert',
                data={
                    'sos_id': sos.id,
                    'patient_lat': str(data['latitude']),
                    'patient_lon': str(data['longitude']),
                    'severity': data.get('severity', 'high'),
                    'type': 'sos',
                },
            )
            notified += 1

    return sos


def hospital_accept_sos(sos: SOSAlert, hospital, eta_minutes: int,
                         ambulance_number: str, changed_by) -> SOSAlert:
    """Hospital confirms they are responding."""
    if sos.status != SOSAlert.Status.ACTIVE:
        raise ValueError('SOS is no longer active.')
    _log(sos, SOSAlert.Status.ACCEPTED, changed_by=changed_by,
         note=f'Hospital {hospital.name} accepted. ETA {eta_minutes} min.')
    sos.status = SOSAlert.Status.ACCEPTED
    sos.responding_hospital = hospital
    sos.eta_minutes = eta_minutes
    sos.ambulance_number = ambulance_number
    sos.accepted_at = timezone.now()
    sos.save(update_fields=[
        'status', 'responding_hospital', 'eta_minutes',
        'ambulance_number', 'accepted_at', 'updated_at',
    ])
    # Notify patient
    create_notification(
        recipient=sos.patient,
        title='🚑 Help is on the way!',
        body=(
            f'{hospital.name} has accepted your SOS. '
            f'Ambulance #{ambulance_number} is on the way. '
            f'ETA: {eta_minutes} minutes.'
        ),
        notif_type='sos_accepted',
        data={'sos_id': sos.id, 'hospital_name': hospital.name,
              'eta_minutes': eta_minutes, 'type': 'sos'},
    )
    return sos


def hospital_enroute_sos(sos: SOSAlert, changed_by) -> SOSAlert:
    """Hospital marks ambulance as dispatched / en route."""
    if sos.status != SOSAlert.Status.ACCEPTED:
        raise ValueError('SOS must be accepted before marking en route.')
    _log(sos, SOSAlert.Status.ENROUTE, changed_by=changed_by)
    sos.status = SOSAlert.Status.ENROUTE
    sos.enroute_at = timezone.now()
    sos.save(update_fields=['status', 'enroute_at', 'updated_at'])
    create_notification(
        recipient=sos.patient,
        title='🚑 Ambulance dispatched',
        body=f'Ambulance #{sos.ambulance_number} is now en route to you.',
        notif_type='sos_enroute',
        data={'sos_id': sos.id, 'type': 'sos'},
    )
    return sos


def update_ambulance_location(sos: SOSAlert, lat, lon) -> SOSAlert:
    """Hospital pushes live ambulance GPS for the patient's tracking map."""
    sos.ambulance_latitude = lat
    sos.ambulance_longitude = lon
    sos.save(update_fields=['ambulance_latitude', 'ambulance_longitude', 'updated_at'])
    return sos


def hospital_arrived_sos(sos: SOSAlert, changed_by) -> SOSAlert:
    _log(sos, SOSAlert.Status.ARRIVED, changed_by=changed_by)
    sos.status = SOSAlert.Status.ARRIVED
    sos.arrived_at = timezone.now()
    sos.save(update_fields=['status', 'arrived_at', 'updated_at'])
    create_notification(
        recipient=sos.patient,
        title='✅ Ambulance arrived',
        body='The ambulance has arrived at your location.',
        notif_type='sos_arrived',
        data={'sos_id': sos.id, 'type': 'sos'},
    )
    return sos


def resolve_sos(sos: SOSAlert, changed_by) -> SOSAlert:
    _log(sos, SOSAlert.Status.RESOLVED, changed_by=changed_by)
    sos.status = SOSAlert.Status.RESOLVED
    sos.resolved_at = timezone.now()
    sos.save(update_fields=['status', 'resolved_at', 'updated_at'])
    return sos


def cancel_sos(sos: SOSAlert, changed_by) -> SOSAlert:
    if sos.status in [SOSAlert.Status.RESOLVED, SOSAlert.Status.ARRIVED]:
        raise ValueError('Cannot cancel a resolved or arrived SOS.')
    _log(sos, SOSAlert.Status.CANCELLED, changed_by=changed_by, note='Cancelled by patient')
    sos.status = SOSAlert.Status.CANCELLED
    sos.save(update_fields=['status', 'updated_at'])
    if sos.responding_hospital:
        create_notification(
            recipient=sos.responding_hospital.user,
            title='SOS Cancelled',
            body=f'Patient {sos.patient.full_name} has cancelled the SOS alert.',
            notif_type='sos_cancelled',
            data={'sos_id': sos.id, 'type': 'sos'},
        )
    return sos


def get_active_sos_for_hospital(hospital) -> list:
    """All active SOS alerts within 30km of the hospital."""
    active = SOSAlert.objects.filter(status=SOSAlert.Status.ACTIVE)
    nearby = []
    for sos in active:
        dist = _haversine_km(hospital.latitude, hospital.longitude,
                             sos.latitude, sos.longitude)
        if dist <= 30:
            nearby.append((sos, round(dist, 2)))
    nearby.sort(key=lambda x: x[1])
    return nearby