"""
Models for the Process Monitoring API.
"""
from django.db import models
from django.utils import timezone


class Host(models.Model):
    """Model for storing host information."""
    hostname = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['hostname']

    def __str__(self):
        return self.hostname

    def update_last_seen(self):
        """Update the last_seen timestamp."""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])


class ProcessSnapshot(models.Model):
    """Model for storing a snapshot of process information."""
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='snapshots')
    timestamp = models.DateTimeField(default=timezone.now)
    total_processes = models.IntegerField(default=0)
    total_cpu_percent = models.FloatField(default=0.0)
    total_memory_mb = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['host', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.host.hostname} - {self.timestamp}"


class Process(models.Model):
    """Model for storing individual process information."""
    snapshot = models.ForeignKey(ProcessSnapshot, on_delete=models.CASCADE, related_name='processes')
    pid = models.IntegerField()
    name = models.CharField(max_length=255)
    cpu_percent = models.FloatField(default=0.0)
    memory_mb = models.FloatField(default=0.0)
    parent_pid = models.IntegerField(null=True, blank=True)
    command_line = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='running')
    create_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['pid']
        indexes = [
            models.Index(fields=['snapshot', 'pid']),
            models.Index(fields=['snapshot', 'parent_pid']),
        ]
        unique_together = ['snapshot', 'pid']

    def __str__(self):
        return f"{self.name} (PID: {self.pid})"

    @property
    def children(self):
        """Get all child processes of this process."""
        return Process.objects.filter(
            snapshot=self.snapshot,
            parent_pid=self.pid
        )

    @property
    def parent(self):
        """Get the parent process of this process."""
        if self.parent_pid:
            return Process.objects.filter(
                snapshot=self.snapshot,
                pid=self.parent_pid
            ).first()
        return None 