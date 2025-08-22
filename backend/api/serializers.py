"""
Serializers for the Process Monitoring API.
"""
from rest_framework import serializers
from .models import Host, ProcessSnapshot, Process


class ProcessSerializer(serializers.ModelSerializer):
    """Serializer for Process model."""
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = [
            'id', 'pid', 'name', 'cpu_percent', 'memory_mb',
            'parent_pid', 'command_line', 'status', 'create_time',
            'children', 'has_children'
        ]

    def get_children(self, obj):
        """Get serialized children processes."""
        children = obj.children
        if children.exists():
            return ProcessSerializer(children, many=True).data
        return []

    def get_has_children(self, obj):
        """Check if process has children."""
        return obj.children.exists()


class ProcessSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for ProcessSnapshot model."""
    processes = serializers.SerializerMethodField()
    hostname = serializers.CharField(source='host.hostname', read_only=True)

    class Meta:
        model = ProcessSnapshot
        fields = [
            'id', 'timestamp', 'total_processes', 'total_cpu_percent',
            'total_memory_mb', 'hostname', 'processes'
        ]

    def get_processes(self, obj):
        """Get all processes in the snapshot."""
        all_processes = obj.processes.all()
        return ProcessSerializer(all_processes, many=True).data


class HostSerializer(serializers.ModelSerializer):
    """Serializer for Host model."""
    latest_snapshot = serializers.SerializerMethodField()
    process_count = serializers.SerializerMethodField()

    class Meta:
        model = Host
        fields = [
            'id', 'hostname', 'ip_address', 'first_seen', 'last_seen',
            'is_active', 'latest_snapshot', 'process_count'
        ]

    def get_latest_snapshot(self, obj):
        """Get the latest snapshot for this host."""
        latest = obj.snapshots.first()
        if latest:
            return ProcessSnapshotSerializer(latest).data
        return None

    def get_process_count(self, obj):
        """Get the total number of processes in the latest snapshot."""
        latest = obj.snapshots.first()
        if latest:
            return latest.total_processes
        return 0


class ProcessDataSerializer(serializers.Serializer):
    """Serializer for incoming process data from agent."""
    hostname = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField()
    processes = serializers.ListField(
        child=serializers.DictField()
    )
    api_key = serializers.CharField(max_length=255)

    def validate_processes(self, value):
        """Validate process data structure."""
        for process in value:
            required_fields = ['pid', 'name']
            for field in required_fields:
                if field not in process:
                    raise serializers.ValidationError(
                        f"Process missing required field: {field}"
                    )
        return value 