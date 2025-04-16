"""
Monitoring and Logging Configuration for Vertex AI Deployments

This module provides configuration and utilities for setting up monitoring,
logging, alerting, and dashboard creation for Medical Billing Denial Agent
deployments on Vertex AI.
"""

import base64
import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union, Any

try:
    from google.cloud import monitoring_v3
    from google.cloud import logging as cloud_logging
    from google.cloud.monitoring_dashboard import v1 as dashboard
except ImportError:
    print("Google Cloud Monitoring libraries not found.")
    print("Install them with: pip install google-cloud-monitoring google-cloud-logging google-cloud-monitoring-dashboards")

# Set up logger
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Severity levels for alerts."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class MetricDefinition:
    """Definition of a custom metric to be monitored."""
    name: str
    display_name: str
    description: str
    metric_kind: str  # GAUGE, DELTA, CUMULATIVE
    value_type: str   # BOOL, INT64, DOUBLE, STRING, DISTRIBUTION
    unit: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    

@dataclass
class AlertPolicy:
    """Definition of an alert policy."""
    name: str
    display_name: str
    description: str
    metric_name: str
    threshold_value: float
    duration_seconds: int = 300  # 5 minutes
    severity: AlertSeverity = AlertSeverity.WARNING
    notification_channels: List[str] = field(default_factory=list)
    

@dataclass
class LogMetric:
    """Definition of a log-based metric."""
    name: str
    display_name: str
    description: str
    filter_string: str
    value_extractor: Optional[str] = None


@dataclass
class DashboardPanel:
    """Definition of a dashboard panel."""
    title: str
    metric_name: str
    filter_string: Optional[str] = None
    panel_type: str = "LINE"  # LINE, STACKED_BAR, STACKED_AREA
    

@dataclass
class Dashboard:
    """Definition of a monitoring dashboard."""
    name: str
    display_name: str
    description: str
    panels: List[DashboardPanel] = field(default_factory=list)


def create_custom_metrics(project_id: str, metrics: List[MetricDefinition]) -> None:
    """
    Create custom metrics in Google Cloud Monitoring.
    
    Args:
        project_id: The Google Cloud project ID
        metrics: List of metric definitions to create
    """
    client = monitoring_v3.MetricServiceClient()
    project_path = f"projects/{project_id}"
    
    for metric in metrics:
        descriptor = monitoring_v3.MetricDescriptor()
        descriptor.type = f"custom.googleapis.com/{metric.name}"
        descriptor.display_name = metric.display_name
        descriptor.description = metric.description
        descriptor.metric_kind = getattr(monitoring_v3.MetricDescriptor.MetricKind, metric.metric_kind)
        descriptor.value_type = getattr(monitoring_v3.MetricDescriptor.ValueType, metric.value_type)
        descriptor.unit = metric.unit
        
        for label_key, label_description in metric.labels.items():
            label = monitoring_v3.LabelDescriptor()
            label.key = label_key
            label.description = label_description
            label.value_type = monitoring_v3.LabelDescriptor.ValueType.STRING
            descriptor.labels.append(label)
        
        try:
            client.create_metric_descriptor(name=project_path, metric_descriptor=descriptor)
            logger.info(f"Created custom metric: {metric.name}")
        except Exception as e:
            logger.error(f"Failed to create metric {metric.name}: {str(e)}")


def create_alert_policies(project_id: str, policies: List[AlertPolicy]) -> None:
    """
    Create alert policies in Google Cloud Monitoring.
    
    Args:
        project_id: The Google Cloud project ID
        policies: List of alert policies to create
    """
    client = monitoring_v3.AlertPolicyServiceClient()
    project_path = f"projects/{project_id}"
    
    for policy in policies:
        alert_policy = monitoring_v3.AlertPolicy()
        alert_policy.display_name = policy.display_name
        alert_policy.documentation = monitoring_v3.AlertPolicy.Documentation()
        alert_policy.documentation.content = policy.description
        
        # Create condition
        condition = monitoring_v3.AlertPolicy.Condition()
        condition.display_name = f"Threshold Condition - {policy.display_name}"
        
        # Set up the threshold condition
        threshold = monitoring_v3.AlertPolicy.Condition.MetricThreshold()
        threshold.filter = f'metric.type="custom.googleapis.com/{policy.metric_name}" AND resource.type="vertex_ai_agent"'
        threshold.comparison = monitoring_v3.AlertPolicy.Condition.ComparisonType.COMPARISON_GT
        threshold.threshold_value = policy.threshold_value
        
        # Set up aggregation
        aggregation = monitoring_v3.Aggregation()
        aggregation.alignment_period.seconds = 60
        aggregation.per_series_aligner = monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
        aggregation.cross_series_reducer = monitoring_v3.Aggregation.Reducer.REDUCE_SUM
        threshold.aggregations = [aggregation]
        
        # Set up duration
        threshold.duration.seconds = policy.duration_seconds
        
        # Apply threshold to condition
        condition.condition_threshold = threshold
        
        # Add condition to policy
        alert_policy.conditions = [condition]
        
        # Set notification channels
        if policy.notification_channels:
            alert_policy.notification_channels = [
                f"projects/{project_id}/notificationChannels/{channel_id}"
                for channel_id in policy.notification_channels
            ]
            
        # Set severity via user labels
        alert_policy.user_labels = {"severity": policy.severity.value}
        
        # Create the policy
        try:
            created_policy = client.create_alert_policy(
                name=project_path,
                alert_policy=alert_policy
            )
            logger.info(f"Created alert policy: {policy.name}")
        except Exception as e:
            logger.error(f"Failed to create alert policy {policy.name}: {str(e)}")


def create_log_metrics(project_id: str, metrics: List[LogMetric]) -> None:
    """
    Create log-based metrics in Google Cloud Logging.
    
    Args:
        project_id: The Google Cloud project ID
        metrics: List of log metrics to create
    """
    client = cloud_logging.Client(project=project_id)
    
    for metric in metrics:
        try:
            log_metric = client.metric(metric.name)
            log_metric.description = metric.description
            log_metric.filter_ = metric.filter_string
            
            if metric.value_extractor:
                log_metric.value_extractor = metric.value_extractor
                
            log_metric.create_or_update()
            logger.info(f"Created log-based metric: {metric.name}")
        except Exception as e:
            logger.error(f"Failed to create log-based metric {metric.name}: {str(e)}")


def create_dashboard(project_id: str, dashboard_config: Dashboard) -> None:
    """
    Create a monitoring dashboard in Google Cloud Monitoring.
    
    Args:
        project_id: The Google Cloud project ID
        dashboard_config: Dashboard configuration
    """
    client = dashboard.DashboardsServiceClient()
    project_path = f"projects/{project_id}"
    
    # Create dashboard configuration
    dashboard_json = {
        "displayName": dashboard_config.display_name,
        "etag": "",
        "mosaicLayout": {
            "columns": 12,
            "tiles": []
        }
    }
    
    # Add panels
    row_height = 4
    current_row = 0
    
    for i, panel in enumerate(dashboard_config.panels):
        # Calculate position (2 panels per row)
        column = 0 if i % 2 == 0 else 6
        if i % 2 == 0 and i > 0:
            current_row += row_height
        
        # Create widget
        widget = {
            "title": panel.title,
            "xyChart": {
                "dataSets": [
                    {
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": f'metric.type="custom.googleapis.com/{panel.metric_name}" AND resource.type="vertex_ai_agent"',
                                "aggregation": {
                                    "alignmentPeriod": "60s",
                                    "perSeriesAligner": "ALIGN_MEAN",
                                    "crossSeriesReducer": "REDUCE_SUM"
                                }
                            }
                        },
                        "plotType": panel.panel_type,
                        "minAlignmentPeriod": "60s"
                    }
                ],
                "yAxis": {
                    "scale": "LINEAR",
                    "label": ""
                }
            }
        }
        
        # Add panel filter if provided
        if panel.filter_string:
            widget["xyChart"]["dataSets"][0]["timeSeriesQuery"]["timeSeriesFilter"]["filter"] += f" AND {panel.filter_string}"
        
        # Add tile to dashboard
        dashboard_json["mosaicLayout"]["tiles"].append({
            "widget": widget,
            "xPos": column,
            "yPos": current_row,
            "width": 6,
            "height": row_height
        })
    
    # Create dashboard
    try:
        dashboard_object = dashboard.Dashboard(
            display_name=dashboard_config.display_name,
            etag="",
            mosaic_layout=dashboard_json["mosaicLayout"]
        )
        
        created_dashboard = client.create_dashboard(
            parent=project_path,
            dashboard=dashboard_object
        )
        logger.info(f"Created dashboard: {dashboard_config.name}")
    except Exception as e:
        logger.error(f"Failed to create dashboard {dashboard_config.name}: {str(e)}")


def setup_default_monitoring(project_id: str, agent_name: str = "medical-billing-denial-agent") -> None:
    """
    Set up default monitoring, logging, and alerting for the deployment.
    
    Args:
        project_id: The Google Cloud project ID
        agent_name: The name of the deployed agent
    """
    # Define custom metrics
    metrics = [
        MetricDefinition(
            name="agent/request_count",
            display_name="Agent Request Count",
            description="Number of requests to the agent",
            metric_kind="CUMULATIVE",
            value_type="INT64",
            unit="1",
            labels={"environment": "Deployment environment"}
        ),
        MetricDefinition(
            name="agent/response_time",
            display_name="Agent Response Time",
            description="Time taken to generate a response",
            metric_kind="GAUGE",
            value_type="DOUBLE",
            unit="s",
            labels={"environment": "Deployment environment"}
        ),
        MetricDefinition(
            name="agent/error_count",
            display_name="Agent Error Count",
            description="Number of errors encountered by the agent",
            metric_kind="CUMULATIVE",
            value_type="INT64",
            unit="1",
            labels={"severity": "Error severity", "type": "Error type"}
        ),
        MetricDefinition(
            name="agent/document_processing_time",
            display_name="Document Processing Time",
            description="Time taken to process documents",
            metric_kind="GAUGE",
            value_type="DOUBLE",
            unit="s",
            labels={"document_type": "Type of document processed"}
        ),
        MetricDefinition(
            name="agent/knowledge_retrieval_time",
            display_name="Knowledge Retrieval Time",
            description="Time taken to retrieve information from knowledge bases",
            metric_kind="GAUGE",
            value_type="DOUBLE",
            unit="s",
            labels={"knowledge_base": "Type of knowledge base queried"}
        )
    ]
    
    # Define alert policies
    policies = [
        AlertPolicy(
            name="high_error_rate",
            display_name="High Error Rate",
            description="Alert when the agent error rate exceeds threshold",
            metric_name="agent/error_count",
            threshold_value=5.0,
            duration_seconds=300,
            severity=AlertSeverity.ERROR
        ),
        AlertPolicy(
            name="slow_response_time",
            display_name="Slow Response Time",
            description="Alert when the agent response time exceeds threshold",
            metric_name="agent/response_time",
            threshold_value=10.0,
            duration_seconds=300,
            severity=AlertSeverity.WARNING
        ),
        AlertPolicy(
            name="document_processing_failure",
            display_name="Document Processing Failure",
            description="Alert when document processing failures occur",
            metric_name="agent/error_count",
            threshold_value=2.0,
            duration_seconds=300,
            severity=AlertSeverity.ERROR
        )
    ]
    
    # Define log-based metrics
    log_metrics = [
        LogMetric(
            name="phi_detection_events",
            display_name="PHI Detection Events",
            description="Count of events where PHI was detected and handled",
            filter_string='resource.type="vertex_ai_agent" AND jsonPayload.event_type="phi_detection"'
        ),
        LogMetric(
            name="denial_code_lookup",
            display_name="Denial Code Lookup Events",
            description="Count of denial code lookup operations",
            filter_string='resource.type="vertex_ai_agent" AND jsonPayload.event_type="denial_code_lookup"'
        ),
        LogMetric(
            name="document_upload_events",
            display_name="Document Upload Events",
            description="Count of document upload events",
            filter_string='resource.type="vertex_ai_agent" AND jsonPayload.event_type="document_upload"'
        )
    ]
    
    # Define dashboard
    dashboard_config = Dashboard(
        name="agent_performance",
        display_name="Medical Billing Denial Agent Performance",
        description="Performance metrics for the Medical Billing Denial Agent",
        panels=[
            DashboardPanel(
                title="Request Count",
                metric_name="agent/request_count",
                panel_type="LINE"
            ),
            DashboardPanel(
                title="Response Time",
                metric_name="agent/response_time",
                panel_type="LINE"
            ),
            DashboardPanel(
                title="Error Count",
                metric_name="agent/error_count",
                panel_type="STACKED_BAR"
            ),
            DashboardPanel(
                title="Document Processing Time",
                metric_name="agent/document_processing_time",
                panel_type="LINE"
            ),
            DashboardPanel(
                title="Knowledge Retrieval Time",
                metric_name="agent/knowledge_retrieval_time",
                panel_type="LINE"
            ),
            DashboardPanel(
                title="PHI Detection Events",
                metric_name="logging.googleapis.com/user/phi_detection_events",
                panel_type="STACKED_BAR"
            )
        ]
    )
    
    # Create metrics, alerts, and dashboard
    create_custom_metrics(project_id, metrics)
    create_alert_policies(project_id, policies)
    create_log_metrics(project_id, log_metrics)
    create_dashboard(project_id, dashboard_config)
    
    logger.info(f"Default monitoring setup completed for project: {project_id}")


def setup_logging_export(project_id: str, destination: str) -> None:
    """
    Set up log export for compliance and archival purposes.
    
    Args:
        project_id: The Google Cloud project ID
        destination: Destination for logs (e.g., Cloud Storage bucket, BigQuery dataset)
    """
    client = cloud_logging.Client(project=project_id)
    
    # Create a sink to export logs
    sink_name = "medical-billing-agent-logs"
    sink = client.sink(sink_name)
    
    # Configure the sink
    sink.filter_ = 'resource.type="vertex_ai_agent"'
    sink.destination = destination
    
    # Create or update the sink
    try:
        sink.create_or_update()
        logger.info(f"Created log export sink to {destination}")
    except Exception as e:
        logger.error(f"Failed to create log export sink: {str(e)}")


def emit_custom_metric(
    project_id: str,
    metric_name: str,
    value: Union[int, float],
    labels: Dict[str, str] = None
) -> bool:
    """
    Emit a custom metric to Cloud Monitoring.
    
    Args:
        project_id: The Google Cloud project ID
        metric_name: The name of the metric (without custom.googleapis.com/ prefix)
        value: The metric value to record
        labels: Optional labels to attach to the metric
        
    Returns:
        bool: True if successful, False otherwise
    """
    client = monitoring_v3.MetricServiceClient()
    project_path = f"projects/{project_id}"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_name}"
    
    # Add labels if provided
    if labels:
        for key, value in labels.items():
            series.metric.labels[key] = value
    
    # Set the resource (Vertex AI Agent)
    series.resource.type = "vertex_ai_agent"
    series.resource.labels["project_id"] = project_id
    
    # Create the data point
    point = series.points.add()
    point.value.double_value = float(value) if isinstance(value, (int, float)) else 0.0
    
    # Set the time
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)
    point.interval.end_time.seconds = seconds
    point.interval.end_time.nanos = nanos
    
    # Write the time series
    try:
        client.create_time_series(
            name=project_path,
            time_series=[series]
        )
        return True
    except Exception as e:
        logger.error(f"Failed to emit metric {metric_name}: {str(e)}")
        return False


def main():
    """Command-line interface for setting up monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up monitoring for Medical Billing Denial Agent")
    parser.add_argument("--project-id", required=True, help="Google Cloud project ID")
    parser.add_argument("--agent-name", default="medical-billing-denial-agent", help="Deployed agent name")
    parser.add_argument("--log-destination", help="Destination for log export (optional)")
    
    args = parser.parse_args()
    
    # Set up monitoring
    setup_default_monitoring(args.project_id, args.agent_name)
    
    # Set up log export if destination provided
    if args.log_destination:
        setup_logging_export(args.project_id, args.log_destination)


if __name__ == "__main__":
    main()
