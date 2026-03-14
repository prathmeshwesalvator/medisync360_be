from rest_framework import serializers
from .models import SOSAlert, SOSStatusLog


class SOSStatusLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = SOSStatusLog
        fields = ['id', 'from_status', 'to_status', 'changed_by_name', 'note', 'changed_at']

    def get_changed_by_name(self, obj):
        return obj.changed_by.full_name if obj.changed_by else None


class SOSAlertSerializer(serializers.ModelSerializer):
    patient_name            = serializers.CharField(source='patient.full_name', read_only=True)
    patient_phone           = serializers.CharField(source='patient.phone', read_only=True)
    responding_hospital_name = serializers.SerializerMethodField()
    status_logs             = SOSStatusLogSerializer(many=True, read_only=True)

    class Meta:
        model  = SOSAlert
        fields = [
            'id', 'patient_name', 'patient_phone',
            'latitude', 'longitude', 'address',
            'severity', 'description',
            'blood_group', 'allergies', 'medications',
            'emergency_contact_name', 'emergency_contact_phone',
            'status',
            'responding_hospital_name',
            'accepted_at', 'enroute_at', 'arrived_at', 'resolved_at',
            'eta_minutes',
            'ambulance_latitude', 'ambulance_longitude', 'ambulance_number',
            'created_at', 'updated_at',
            'status_logs',
        ]

    def get_responding_hospital_name(self, obj):
        return obj.responding_hospital.name if obj.responding_hospital else None


class SOSCreateSerializer(serializers.Serializer):
    latitude    = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude   = serializers.DecimalField(max_digits=10, decimal_places=7)
    address     = serializers.CharField(required=False, allow_blank=True, default='')
    severity    = serializers.ChoiceField(
        choices=SOSAlert.Severity.choices,
        default=SOSAlert.Severity.HIGH,
    )
    description              = serializers.CharField(required=False, allow_blank=True, default='')
    blood_group              = serializers.CharField(required=False, allow_blank=True, default='')
    allergies                = serializers.CharField(required=False, allow_blank=True, default='')
    medications              = serializers.CharField(required=False, allow_blank=True, default='')
    emergency_contact_name   = serializers.CharField(required=False, allow_blank=True, default='')
    emergency_contact_phone  = serializers.CharField(required=False, allow_blank=True, default='')


class SOSRespondSerializer(serializers.Serializer):
    """Hospital uses this to accept an SOS and provide ETA + ambulance info."""
    eta_minutes      = serializers.IntegerField(min_value=1, max_value=120)
    ambulance_number = serializers.CharField(required=False, allow_blank=True, default='')


class SOSAmbulanceUpdateSerializer(serializers.Serializer):
    """Hospital pushes live ambulance GPS coordinates."""
    ambulance_latitude  = serializers.DecimalField(max_digits=10, decimal_places=7)
    ambulance_longitude = serializers.DecimalField(max_digits=10, decimal_places=7)