/**
 * Process Monitor Frontend Application
 * Handles data fetching, display, and user interactions
 */

class ProcessMonitor {
    constructor() {
        this.apiBase = '/api';
        this.refreshInterval = null;
        this.currentData = null;
        
        this.initializeEventListeners();
        this.loadData();
        this.startAutoRefresh();
    }

    /**
     * Initialize event listeners for buttons and interactions
     */
    initializeEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadData();
        });

        // Clear data button
        document.getElementById('clearDataBtn').addEventListener('click', () => {
            this.clearOldData();
        });
    }

    /**
     * Start automatic refresh every 30 seconds
     */
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadData();
        }, 30000); // 30 seconds
    }

    /**
     * Stop automatic refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Load process data from the API
     */
    async loadData() {
        try {
            this.showLoading();
            
            const response = await fetch(`${this.apiBase}/processes/get/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.data && result.data.length > 0) {
                this.currentData = result.data;
                this.displayData(result.data);
                this.updateStatusBar(result.data);
            } else {
                this.showNoData();
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load process data. Please check your connection.');
        }
    }

    /**
     * Display process data in the UI
     */
    displayData(data) {
        const container = document.getElementById('processData');
        container.innerHTML = '';
        
        data.forEach(hostData => {
            const hostSection = this.createHostSection(hostData);
            container.appendChild(hostSection);
        });
        
        this.hideLoading();
        container.style.display = 'block';
        document.getElementById('noData').style.display = 'none';
    }

    /**
     * Create a host section with process tree
     */
    createHostSection(hostData) {
        const hostSection = document.createElement('div');
        hostSection.className = 'host-section';
        
        // Host header
        const hostHeader = document.createElement('div');
        hostHeader.className = 'host-header';
        
        const hostInfo = document.createElement('div');
        hostInfo.className = 'host-info';
        
        const hostName = document.createElement('div');
        hostName.className = 'host-name';
        hostName.innerHTML = `<i class="fas fa-desktop"></i> ${hostData.hostname}`;
        
        const hostStats = document.createElement('div');
        hostStats.className = 'host-stats';
        
        const processCount = document.createElement('div');
        processCount.className = 'stat-item';
        processCount.innerHTML = `
            <div class="stat-value">${hostData.total_processes}</div>
            <div class="stat-label">Processes</div>
        `;
        
        const cpuUsage = document.createElement('div');
        cpuUsage.className = 'stat-item';
        cpuUsage.innerHTML = `
            <div class="stat-value">${hostData.total_cpu_percent.toFixed(1)}%</div>
            <div class="stat-label">CPU</div>
        `;
        
        const memoryUsage = document.createElement('div');
        memoryUsage.className = 'stat-item';
        memoryUsage.innerHTML = `
            <div class="stat-value">${hostData.total_memory_mb.toFixed(1)} MB</div>
            <div class="stat-label">Memory</div>
        `;
        
        hostStats.appendChild(processCount);
        hostStats.appendChild(cpuUsage);
        hostStats.appendChild(memoryUsage);
        
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.innerHTML = `<i class="fas fa-clock"></i> Last updated: ${this.formatTimestamp(hostData.timestamp)}`;
        
        hostInfo.appendChild(hostName);
        hostInfo.appendChild(hostStats);
        hostHeader.appendChild(hostInfo);
        hostHeader.appendChild(timestamp);
        
        // Process tree
        const processTree = document.createElement('div');
        processTree.className = 'process-tree';
        
        if (hostData.processes && hostData.processes.length > 0) {
            hostData.processes.forEach(process => {
                const processItem = this.createProcessItem(process);
                processTree.appendChild(processItem);
            });
        } else {
            const noProcesses = document.createElement('div');
            noProcesses.className = 'no-data';
            noProcesses.innerHTML = '<p>No processes found</p>';
            processTree.appendChild(noProcesses);
        }
        
        hostSection.appendChild(hostHeader);
        hostSection.appendChild(processTree);
        
        return hostSection;
    }

    /**
     * Create a process item with expandable children
     */
    createProcessItem(process) {
        const processItem = document.createElement('div');
        processItem.className = 'process-item';
        
        const processHeader = document.createElement('div');
        processHeader.className = 'process-header';
        
        // Toggle button for expandable children
        let toggleButton = null;
        if (process.has_children) {
            toggleButton = document.createElement('div');
            toggleButton.className = 'process-toggle';
            toggleButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
            toggleButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleProcessChildren(processItem, toggleButton, process);
            });
        }
        
        const processInfo = document.createElement('div');
        processInfo.className = 'process-info';
        
        const processName = document.createElement('div');
        processName.className = 'process-name';
        processName.textContent = process.name;
        
        const processPid = document.createElement('div');
        processPid.className = 'process-pid';
        processPid.textContent = `PID: ${process.pid}`;
        
        const processMetrics = document.createElement('div');
        processMetrics.className = 'process-metrics';
        
        const cpuMetric = document.createElement('div');
        cpuMetric.className = 'metric cpu-metric';
        cpuMetric.innerHTML = `<i class="fas fa-microchip"></i> ${process.cpu_percent.toFixed(1)}%`;
        
        const memoryMetric = document.createElement('div');
        memoryMetric.className = 'metric memory-metric';
        memoryMetric.innerHTML = `<i class="fas fa-memory"></i> ${process.memory_mb.toFixed(1)} MB`;
        
        processMetrics.appendChild(cpuMetric);
        processMetrics.appendChild(memoryMetric);
        
        processInfo.appendChild(processName);
        processInfo.appendChild(processPid);
        processInfo.appendChild(processMetrics);
        
        if (toggleButton) {
            processHeader.appendChild(toggleButton);
        }
        processHeader.appendChild(processInfo);
        
        // Children container
        let childrenContainer = null;
        if (process.has_children) {
            childrenContainer = document.createElement('div');
            childrenContainer.className = 'process-children';
            childrenContainer.id = `children-${process.pid}`;
        }
        
        processItem.appendChild(processHeader);
        if (childrenContainer) {
            processItem.appendChild(childrenContainer);
        }
        
        return processItem;
    }

    /**
     * Toggle process children visibility
     */
    async toggleProcessChildren(processItem, toggleButton, process) {
        const childrenContainer = processItem.querySelector('.process-children');
        
        if (childrenContainer.classList.contains('expanded')) {
            // Collapse
            childrenContainer.classList.remove('expanded');
            toggleButton.classList.remove('expanded');
            toggleButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        } else {
            // Expand
            childrenContainer.classList.add('expanded');
            toggleButton.classList.add('expanded');
            toggleButton.innerHTML = '<i class="fas fa-chevron-down"></i>';
            
            // Load children if not already loaded
            if (childrenContainer.children.length === 0) {
                await this.loadProcessChildren(childrenContainer, process);
            }
        }
    }

    /**
     * Load and display process children
     */
    async loadProcessChildren(container, parentProcess) {
        try {
            // For now, we'll use the children data from the parent process
            // In a real implementation, you might want to fetch children separately
            if (parentProcess.children && parentProcess.children.length > 0) {
                parentProcess.children.forEach(childProcess => {
                    const childItem = this.createProcessItem(childProcess);
                    container.appendChild(childItem);
                });
            }
        } catch (error) {
            console.error('Error loading process children:', error);
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error';
            errorMsg.textContent = 'Failed to load child processes';
            container.appendChild(errorMsg);
        }
    }

    /**
     * Update the status bar with current data
     */
    updateStatusBar(data) {
        const totalProcesses = data.reduce((sum, host) => sum + host.total_processes, 0);
        const totalCpu = data.reduce((sum, host) => sum + host.total_cpu_percent, 0);
        const totalMemory = data.reduce((sum, host) => sum + host.total_memory_mb, 0);
        
        document.getElementById('hostCount').textContent = data.length;
        document.getElementById('totalProcesses').textContent = totalProcesses;
        document.getElementById('lastUpdated').textContent = this.formatTimestamp(new Date());
    }

    /**
     * Clear old data from the backend
     */
    async clearOldData() {
        try {
            const response = await fetch(`${this.apiBase}/clear-old-data/`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            this.showNotification(`Cleared ${result.deleted_count} old snapshots`, 'success');
            
            // Reload data after clearing
            this.loadData();
            
        } catch (error) {
            console.error('Error clearing old data:', error);
            this.showNotification('Failed to clear old data', 'error');
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('processData').style.display = 'none';
        document.getElementById('noData').style.display = 'none';
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    /**
     * Show no data state
     */
    showNoData() {
        this.hideLoading();
        document.getElementById('noData').style.display = 'block';
        document.getElementById('processData').style.display = 'none';
    }

    /**
     * Show error message
     */
    showError(message) {
        this.hideLoading();
        this.showNotification(message, 'error');
    }

    /**
     * Show notification message
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#f56565' : type === 'success' ? '#48bb78' : '#4299e1'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Add close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        document.body.appendChild(notification);
    }

    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProcessMonitor();
});

// Add CSS for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        margin-left: 15px;
        opacity: 0.8;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(notificationStyles); 