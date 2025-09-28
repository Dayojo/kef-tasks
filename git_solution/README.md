# DevOps Solution: Self-Hosted Git Repository and Monitoring Setup

## Summary

This guide provides a comprehensive solution for Motley Crew plugins to migrate from GitHub to a self-hosted Git repository solution with enterprise-grade monitoring. The recommended solution uses GitLab as the primary platform with Prometheus and Grafana for comprehensive monitoring.

## Self-Hosted Git Repository Analysis

### Comparison of Solutions

| Feature | GitLab | Gitea | Gerrit |
|---------|--------|-------|--------|
| **Code Review** | Advanced (MRs, inline comments, approval rules) | Basic pull requests | Advanced change-based review |
| **Issue Tracking** | Full-featured (boards, milestones, epics) | Basic (issues, labels) | Limited (requires integrations) |
| **CI/CD Integration** | Native GitLab CI/CD | Third-party integrations | Verification system, CI integrations |
| **Scalability** | Enterprise-grade | Medium-scale | Enterprise-grade (Google scale) |
| **Primary Language** | Ruby/Go | Go | Java |
| **Resource Requirements** | High (4GB+ RAM) | Low (512MB RAM) | Medium-High (2GB+ RAM) |
| **Enterprise Features** | Advanced (compliance, audit, LDAP) | Limited | Advanced (fine-grained ACLs) |
| **Learning Curve** | Moderate | Easy | Steep |
| **Key Strengths** | All-in-one DevOps platform | Lightweight, fast setup | Rigorous code review, compliance |

### Recommendation: GitLab

GitLab is the optimal choice for Motley Crew plugins because:
- **Feature Parity**: Matches GitHub's functionality while adding self-hosting capabilities
- **Scalability**: Enterprise-grade architecture supports rapid growth
- **Integration**: All-in-one DevOps platform reduces tool complexity
- **Future-Proofing**: Comprehensive feature set eliminates need for future migrations

## GitLab Installation Guide

### Prerequisites

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable --now docker

# Install Docker Compose
sudo apt-get install -y docker-compose

# Create GitLab directory structure
mkdir -p ~/gitlab/{config,logs,data}
cd ~/gitlab
```

### GitLab Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  gitlab:
    image: 'gitlab/gitlab-ce:latest'
    restart: always
    hostname: 'gitlab.motleycrew.local'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'https://gitlab.motleycrew.local'
        gitlab_rails['gitlab_shell_ssh_port'] = 2222
        
        # Enable Prometheus metrics
        prometheus_monitoring['enable'] = true
        gitlab_rails['monitoring_whitelist'] = ['127.0.0.0/8', '172.0.0.0/8']
        
        # Performance tuning
        postgresql['shared_buffers'] = "256MB"
        postgresql['max_worker_processes'] = 8
        sidekiq['max_concurrency'] = 25
        
        # Security settings
        gitlab_rails['gitlab_shell_ssh_port'] = 2222
        nginx['ssl_certificate'] = "/etc/gitlab/ssl/gitlab.crt"
        nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/gitlab.key"
        
        # Backup configuration
        gitlab_rails['backup_keep_time'] = 604800
        gitlab_rails['backup_path'] = "/var/opt/gitlab/backups"
    ports:
      - '80:80'
      - '443:443'
      - '2222:22'
    volumes:
      - './config:/etc/gitlab'
      - './logs:/var/log/gitlab'
      - './data:/var/opt/gitlab'
    shm_size: '256m'
    networks:
      - gitlab_network

networks:
  gitlab_network:
    driver: bridge
```

### Deployment Steps

```bash
# Deploy GitLab
sudo docker-compose up -d

# Monitor startup progress
sudo docker-compose logs -f gitlab

# Get initial root password (after startup completes)
sudo docker-compose exec gitlab grep 'Password:' /etc/gitlab/initial_root_password

# Optional: Create SSL certificates
sudo mkdir -p ~/gitlab/config/ssl
sudo openssl req -newkey rsa:4096 -nodes -sha256 -keyout ~/gitlab/config/ssl/gitlab.key -x509 -days 365 -out ~/gitlab/config/ssl/gitlab.crt
```

### Initial Configuration

1. **Access GitLab**: Navigate to `http://your-server-ip`
2. **Login**: Use `root` with the generated password
3. **Security Setup**:
   - Change root password
   - Configure two-factor authentication
   - Set up user accounts and permissions
4. **Project Migration**:
   - Create organization structure
   - Import existing repositories
   - Configure CI/CD pipelines

## Comprehensive Monitoring Setup

### Monitoring Architecture

Create monitoring stack in `monitoring/docker-compose.yml`:

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--storage.tsdb.retention.size=10GB'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SECURITY_DISABLE_GRAVATAR=true
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
    restart: unless-stopped
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    restart: unless-stopped
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points="^/(sys|proc|dev|host|etc)($$|/)"'
    restart: unless-stopped
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  monitoring:
    driver: bridge
```

### Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'motleycrew-monitor'

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'gitlab'
    scheme: https
    metrics_path: '/-/metrics'
    static_configs:
      - targets: ['gitlab.motleycrew.local']
    basic_auth:
      username: 'prometheus_user'
      password: 'prometheus_token'
    scrape_interval: 30s

  - job_name: 'gitlab-workhorse'
    static_configs:
      - targets: ['gitlab.motleycrew.local:9229']
    scrape_interval: 15s

  - job_name: 'gitlab-sidekiq'
    static_configs:
      - targets: ['gitlab.motleycrew.local:8082']
    scrape_interval: 15s

  - job_name: 'gitlab-gitaly'
    static_configs:
      - targets: ['gitlab.motleycrew.local:9236']
    scrape_interval: 15s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 15s

  - job_name: 'docker-daemon'
    static_configs:
      - targets: ['172.17.0.1:9323']
    scrape_interval: 15s
```

### Alert Rules Configuration

Create `monitoring/alert_rules.yml`:

```yaml
groups:
  - name: system_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 85% for more than 5 minutes."

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for more than 5 minutes."

      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 10% on {{ $labels.device }}."

      - alert: GitLabDown
        expr: up{job="gitlab"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "GitLab instance is down"
          description: "GitLab has been down for more than 1 minute."

      - alert: HighContainerRestarts
        expr: rate(container_restarts_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Container restart rate is high"
          description: "Container {{ $labels.name }} has a high restart rate."

  - name: gitlab_alerts
    rules:
      - alert: GitLabHighResponseTime
        expr: gitlab_http_request_duration_seconds{quantile="0.95"} > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GitLab high response time"
          description: "95th percentile response time is above 2 seconds."

      - alert: GitLabHighErrorRate
        expr: rate(gitlab_http_requests_total{code=~"5.."}[5m]) > 0.1
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "GitLab high error rate"
          description: "Error rate is above 10% for more than 3 minutes."

      - alert: GitLabJobQueueHigh
        expr: gitlab_sidekiq_jobs_waiting_count > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "GitLab job queue is high"
          description: "Sidekiq job queue has more than 1000 waiting jobs."
```

### Alertmanager Configuration

Create `monitoring/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@example.com'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'your_email_password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'default'
    email_configs:
      - to: 'devops@motleycrew.com'
        subject: 'Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

  - name: 'critical-alerts'
    email_configs:
      - to: 'devops@motleycrew.com,cto@motleycrew.com'
        subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
        body: |
          CRITICAL ALERT TRIGGERED
          
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          Instance: {{ .Labels.instance }}
          {{ end }}

  - name: 'warning-alerts'
    email_configs:
      - to: 'devops@motleycrew.com'
        subject: 'WARNING: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

## Comprehensive Monitoring Metrics

### System-Level Metrics

#### CPU Monitoring
- **CPU utilization percentage** by core
- **CPU load average** (1, 5, 15 minutes)
- **Context switches** per second
- **CPU wait time** for I/O operations
- **CPU steal time** (virtualized environments)

#### Memory Monitoring
- **Total memory usage** percentage
- **Available memory** and buffers/cache
- **Swap usage** and page faults
- **Memory leaks** detection
- **OOM (Out of Memory)** events

#### Disk I/O Monitoring
- **Disk read/write IOPS** and throughput
- **Disk utilization** percentage and queue length
- **Free disk space** monitoring with alerts
- **Storage growth** trends
- **I/O wait time** and latency

#### Network Monitoring
- **Network bandwidth** utilization (inbound/outbound)
- **Network latency** and packet loss
- **Connection count** and network errors
- **Unusual traffic pattern** detection
- **Network interface** errors and collisions

### GitLab Application Metrics

#### Web Performance
- **HTTP request response times** (avg, 95th percentile)
- **Requests per second** and concurrent users
- **HTTP error rates** (4xx, 5xx responses)
- **Transaction duration** for different operations
- **Active user sessions** and authentication events

#### CI/CD Pipeline Metrics
- **Pipeline success/failure** rates
- **Build and deployment** durations
- **Job queue lengths** and runner utilization
- **Artifact storage** growth and cleanup
- **Pipeline concurrency** and resource usage

#### Git Operations
- **Git push/pull** operation performance
- **Repository size** growth tracking
- **Clone and fetch** operation durations
- **Git LFS storage** usage and transfer rates
- **Branch and merge** request metrics

### Database and Storage Metrics

#### PostgreSQL Monitoring
- **Database query performance** and slow queries
- **Connection pool** utilization and wait times
- **Database size** and growth trends
- **Lock contention** and deadlocks
- **Replication lag** (if applicable)

#### Redis Monitoring
- **Memory usage** and key count
- **Cache hit rates** and evicted keys
- **Redis connection** count and command latency
- **Persistence** and backup status
- **Slow log** analysis

### Container and Infrastructure Metrics

#### Docker Container Monitoring
- **Container CPU** and memory usage per container
- **Container restart counts** and health status
- **Image pull times** and registry performance
- **Container filesystem** usage and I/O
- **Network traffic** per container

## Grafana Dashboard Configuration

### Dashboard Provisioning

Create `monitoring/grafana/provisioning/dashboards/dashboard.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### Data Source Provisioning

Create `monitoring/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

## Deployment and Operation

### Complete Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash

echo "Deploying GitLab and Monitoring Stack..."

# Deploy GitLab
cd ~/gitlab
sudo docker-compose up -d

# Wait for GitLab to start
echo "Waiting for GitLab to start..."
sleep 60

# Deploy Monitoring Stack
cd ~/monitoring
sudo docker-compose up -d

# Display access information
echo "Deployment complete!"
echo "GitLab: http://your-server-ip"
echo "Grafana: http://your-server-ip:3000 (admin/admin123)"
echo "Prometheus: http://your-server-ip:9090"
echo "cAdvisor: http://your-server-ip:8080"

# Get GitLab root password
echo "GitLab root password:"
sudo docker-compose -f ~/gitlab/docker-compose.yml exec gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

### Backup Strategy

Create `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup GitLab
sudo docker-compose -f ~/gitlab/docker-compose.yml exec gitlab gitlab-backup create
sudo cp ~/gitlab/data/backups/* $BACKUP_DIR/

# Backup Grafana dashboards
sudo cp -r ~/monitoring/grafana/ $BACKUP_DIR/

# Backup configuration files
sudo cp ~/gitlab/docker-compose.yml $BACKUP_DIR/
sudo cp ~/monitoring/docker-compose.yml $BACKUP_DIR/
sudo cp ~/monitoring/prometheus.yml $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

## Security Considerations

### GitLab Security
- Enable two-factor authentication for all users
- Configure SSL/TLS certificates
- Regular security updates and patches
- Implement backup encryption
- Configure firewall rules

### Monitoring Security
- Secure Grafana with strong passwords
- Implement HTTPS for all monitoring interfaces
- Regular security scanning
- Access control and user management
- Audit log monitoring

## Conclusion

This comprehensive guide provides Motley Crew plugins with a production-ready, self-hosted GitLab environment with enterprise-grade monitoring capabilities. The solution scales from current needs while providing the foundation for future growth, eliminating the need for another platform migration as the company expands.

The monitoring solution provides complete visibility into system performance, application health, and security metrics, enabling proactive issue detection and resolution. With proper implementation and maintenance, this solution will support the company's DevOps needs well into the future.