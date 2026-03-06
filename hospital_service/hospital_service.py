import math
from .models import Hospital, CapacityLog


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi    = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_nearby_hospitals(lat: float, lon: float, radius_km: float = 20.0) -> list:
    """Return active hospitals within radius_km, sorted by distance. No PostGIS needed."""
    qs = Hospital.objects.filter(
        status=Hospital.Status.ACTIVE,
        latitude__isnull=False,
        longitude__isnull=False,
    )
    results = []
    for h in qs:
        dist = haversine_km(lat, lon, float(h.latitude), float(h.longitude))
        if dist <= radius_km:
            h.distance_km = round(dist, 2)
            results.append(h)
    results.sort(key=lambda h: h.distance_km)
    return results


def search_hospitals(query='', city='', department='', has_icu=False):
    qs = Hospital.objects.filter(status=Hospital.Status.ACTIVE)
    if query:
        qs = qs.filter(name__icontains=query)
    if city:
        qs = qs.filter(city__icontains=city)
    if department:
        qs = qs.filter(departments__name__icontains=department, departments__is_active=True)
    if has_icu:
        qs = qs.filter(icu_available__gt=0)
    return qs.distinct()


def update_capacity(hospital, available_beds: int, icu_available: int, emergency_available: int):
    hospital.available_beds      = available_beds
    hospital.icu_available       = icu_available
    hospital.emergency_available = emergency_available
    hospital.save(update_fields=['available_beds', 'icu_available', 'emergency_available', 'updated_at'])
    CapacityLog.objects.create(
        hospital=hospital,
        total_beds=hospital.total_beds,
        available_beds=available_beds,
        icu_total=hospital.icu_total,
        icu_available=icu_available,
    )
    return hospital