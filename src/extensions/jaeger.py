from flask import Flask              
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider        
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


def configure_tracer(app: Flask) -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=app.config.get('JAEGER_HOST', 'localhost'),
                agent_port=app.config.get('JAEGER_PORT', 6831),
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


def init_jaeger(app: Flask):
    configure_tracer(app)
    FlaskInstrumentor().instrument_app(app)
