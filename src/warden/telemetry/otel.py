from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from warden.config import GCP_PROJECT_ID
from typing import Any, Dict

def setup_tracer():
    provider = TracerProvider()
    try:
        if GCP_PROJECT_ID and GCP_PROJECT_ID != "local-test-project":
            exporter = CloudTraceSpanExporter(project_id=GCP_PROJECT_ID)
            provider.add_span_processor(BatchSpanProcessor(exporter))
    except Exception:
        pass
    trace.set_tracer_provider(provider)

setup_tracer()
tracer = trace.get_tracer("warden")

def get_trace_id() -> str:
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return "0" * 32

def span(name: str):
    """Helper to start a span"""
    return tracer.start_as_current_span(name)

def add_event(name: str, attributes: Dict[str, Any] = None):
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        current_span.add_event(name, attributes)
