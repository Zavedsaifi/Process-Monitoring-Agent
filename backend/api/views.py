"""
Views for the Process Monitoring API.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timezone
import json

from .models import Host, ProcessSnapshot, Process
from .serializers import (
    ProcessSerializer, ProcessSnapshotSerializer, HostSerializer,
    ProcessDataSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class ProcessDataView(View):
    """View for receiving process data from agent."""
    
    def post(self, request):
        """Handle POST request with process data."""
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")
            
            serializer = ProcessDataSerializer(data=data)
            if not serializer.is_valid():
                print(f"Serializer validation failed: {serializer.errors}")
                return JsonResponse(
                    {'error': 'Invalid data', 'details': serializer.errors},
                    status=400
                )
            
            print(f"Data validation passed: {data}")
            
            # Validate API key (commented out for now)
            # if data.get('api_key') != getattr(settings, 'API_KEY', 'default-key'):
            #     return JsonResponse(
            #         {'error': 'Invalid API key'},
            #         status=401
            #     )
            
            # Get or create host
            host, created = Host.objects.get_or_create(
                hostname=data['hostname']
            )
            host.update_last_seen()
            print(f"Host {'created' if created else 'retrieved'}: {host.hostname}")
            print(f"Received data for host: {data['hostname']} with {len(data['processes'])} processes")
            
            # Parse timestamp
            try:
                if isinstance(data['timestamp'], str):
                    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                else:
                    timestamp = datetime.now(timezone.utc)
                print(f"Timestamp parsed: {timestamp}")
            except (ValueError, TypeError) as e:
                print(f"Timestamp parsing error: {e}, using current time")
                timestamp = datetime.now(timezone.utc)
            
            # Create snapshot
            snapshot = ProcessSnapshot.objects.create(
                host=host,
                timestamp=timestamp,
                total_processes=len(data['processes'])
            )
            print(f"Snapshot created: {snapshot.id} with {len(data['processes'])} processes")
            
            # Calculate totals
            total_cpu = 0.0
            total_memory = 0.0
            
            # Create processes
            for i, proc_data in enumerate(data['processes']):
                cpu_percent = proc_data.get('cpu_percent', 0.0)
                memory_mb = proc_data.get('memory_mb', 0.0)
                
                total_cpu += cpu_percent
                total_memory += memory_mb
                
                # Handle create_time field properly
                create_time = proc_data.get('create_time')
                if create_time is not None:
                    try:
                        # Convert to string if it's not already
                        if not isinstance(create_time, str):
                            create_time = str(create_time)
                        # Try to parse and format as ISO string
                        parsed_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                        create_time = parsed_time.isoformat()
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid create_time format for process {i}: {create_time}")
                        create_time = None
                
                Process.objects.create(
                    snapshot=snapshot,
                    pid=proc_data['pid'],
                    name=proc_data['name'],
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    parent_pid=proc_data.get('parent_pid'),
                    command_line=proc_data.get('command_line', ''),
                    status=proc_data.get('status', 'running'),
                    create_time=create_time
                )
                
                # Log every 50th process for debugging
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1}/{len(data['processes'])} processes...")
            
            print(f"All {len(data['processes'])} processes created successfully")
            
            # Update snapshot totals
            snapshot.total_cpu_percent = total_cpu
            snapshot.total_memory_mb = total_memory
            snapshot.save()
            print(f"Snapshot updated with totals")
            
            return JsonResponse({
                'status': 'success',
                'message': f'Processed {len(data["processes"])} processes',
                'snapshot_id': snapshot.id
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse(
                {'error': 'Invalid JSON', 'details': str(e)},
                status=400
            )
        except Exception as e:
            print(f"Unexpected error in ProcessDataView.post: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse(
                {'error': 'Unexpected error', 'details': str(e)},
                status=500
            )


@api_view(['GET'])
def get_processes(request):
    """Get latest process data for frontend."""
    try:
        # Get the latest snapshot for each host
        hosts = Host.objects.filter(is_active=True)
        
        if not hosts.exists():
            return Response({
                'message': 'No hosts found',
                'data': []
            })
        
        # Get latest snapshot for each host
        latest_snapshots = []
        for host in hosts:
            latest = host.snapshots.first()
            if latest:
                latest_snapshots.append(latest)
        
        if not latest_snapshots:
            return Response({
                'message': 'No snapshots found',
                'data': []
            })
        
        # Sort by timestamp (most recent first)
        latest_snapshots.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Serialize data
        data = []
        for snapshot in latest_snapshots:
            snapshot_data = ProcessSnapshotSerializer(snapshot).data
            data.append(snapshot_data)
        
        return Response({
            'message': 'Success',
            'data': data,
            'total_hosts': len(data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_hosts(request):
    """Get list of monitored hosts."""
    try:
        hosts = Host.objects.filter(is_active=True)
        serializer = HostSerializer(hosts, many=True)
        
        return Response({
            'message': 'Success',
            'data': serializer.data,
            'total_hosts': len(serializer.data)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_host_processes(request, hostname):
    """Get process data for a specific host."""
    try:
        host = Host.objects.get(hostname=hostname, is_active=True)
        latest_snapshot = host.snapshots.first()
        
        if not latest_snapshot:
            return Response({
                'message': f'No snapshots found for host {hostname}',
                'data': None
            })
        
        snapshot_data = ProcessSnapshotSerializer(latest_snapshot).data
        
        return Response({
            'message': 'Success',
            'data': snapshot_data
        })
        
    except Host.DoesNotExist:
        return Response(
            {'error': f'Host {hostname} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def clear_old_data(request):
    """Clear old process data (keep last 24 hours)."""
    try:
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Delete old snapshots and related processes
        old_snapshots = ProcessSnapshot.objects.filter(timestamp__lt=cutoff_time)
        count = old_snapshots.count()
        
        old_snapshots.delete()
        
        return Response({
            'message': f'Cleared {count} old snapshots',
            'deleted_count': count
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 