from rest_framework import serializers

from releases.models import Release


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = (
            "id",
            "release_name",
            "start_at",
            "end_at",
            "created_by",
            "product",
            "goal",
            "description",
        )

    def verify_fields_releases(self, releases, date_start, date_end, release_name):
        if date_start > date_end:
            raise serializers.ValidationError({
                "message": "The start date must be less than the end date"
            })
        
        for release in releases:
            if date_start >= release.start_at and date_start <= release.end_at:
                raise serializers.ValidationError({
                    "message": "The start date must be greater than the start date of the previous release"
                })

            if release_name == release.release_name:
                raise serializers.ValidationError({
                    "message": "The release name must be unique"
                })

    def create(self, validated_data):
        release = Release.objects.all()
        self.verify_fields_releases(
            release, validated_data['start_at'], validated_data['end_at'], validated_data['release_name']
        )
        return Release.objects.create(**validated_data)

    def update(self, validated_data):
        release = Release.objects.all()
        self.verify_fields_releases(
            release, validated_data['start_at'], validated_data['end_at'], validated_data['release_name']
        )
        return Release.objects.update(**validated_data)
