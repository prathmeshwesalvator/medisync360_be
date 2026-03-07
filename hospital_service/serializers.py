from rest_framework import serializers
from .models import Hospital, Department, Amenity, CapacityLog


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = ['id', 'name', 'head_doctor_name', 'phone_extension', 'floor', 'is_active']


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Amenity
        fields = ['id', 'name', 'is_available']



class HospitalListSerializer(serializers.ModelSerializer):
    bed_occupancy_percent = serializers.ReadOnlyField()
    icu_occupancy_percent = serializers.ReadOnlyField()

    class Meta:
        model  = Hospital
        fields = [
            'id', 'name', 'address', 'city', 'state', 'pincode',
            'phone', 'email', 'website',
            'logo_url', 'image_url', 'description', 'status',
            'total_beds', 'available_beds',
            'icu_total', 'icu_available',
            'emergency_beds', 'emergency_available',
            'bed_occupancy_percent', 'icu_occupancy_percent',
            'latitude', 'longitude',   # ← MAKE SURE THESE ARE HERE
            'is_verified', 'established_year',
        ]



class HospitalDetailSerializer(serializers.ModelSerializer):
    departments           = DepartmentSerializer(many=True, read_only=True)
    amenities             = AmenitySerializer(many=True, read_only=True)
    bed_occupancy_percent = serializers.ReadOnlyField()
    icu_occupancy_percent = serializers.ReadOnlyField()

    class Meta:
        model  = Hospital
        fields = '__all__'


class HospitalWriteSerializer(serializers.ModelSerializer):
    """Create / update — hospital user fills in their details."""
    departments = DepartmentSerializer(many=True, required=False)
    amenities   = AmenitySerializer(many=True, required=False)

    class Meta:
        model   = Hospital
        exclude = ['user', 'is_verified', 'created_at', 'updated_at']

    def create(self, validated_data):
        departments_data = validated_data.pop('departments', [])
        amenities_data   = validated_data.pop('amenities', [])
        hospital = Hospital.objects.create(**validated_data)
        for d in departments_data:
            Department.objects.create(hospital=hospital, **d)
        for a in amenities_data:
            Amenity.objects.create(hospital=hospital, **a)
        return hospital

    def update(self, instance, validated_data):
        validated_data.pop('departments', None)
        validated_data.pop('amenities', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CapacityUpdateSerializer(serializers.Serializer):
    available_beds      = serializers.IntegerField(min_value=0)
    icu_available       = serializers.IntegerField(min_value=0)
    emergency_available = serializers.IntegerField(min_value=0)

    def validate(self, attrs):
        hospital = self.context.get('hospital')
        if hospital:
            if attrs['available_beds'] > hospital.total_beds:
                raise serializers.ValidationError({'available_beds': 'Cannot exceed total beds.'})
            if attrs['icu_available'] > hospital.icu_total:
                raise serializers.ValidationError({'icu_available': 'Cannot exceed total ICU beds.'})
            if attrs['emergency_available'] > hospital.emergency_beds:
                raise serializers.ValidationError({'emergency_available': 'Cannot exceed total emergency beds.'})
        return attrs


class CapacityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CapacityLog
        fields = '__all__'




