from app.models.trustrepo_context import TrustRepoContext
from app.models.report.runtime_report import RuntimeHealthReport, PipelineStageMetric
from datetime import datetime


class RuntimeHealthEngine:
    """
    Analyzes execution traces to produce a RuntimeHealthReport.
    Supports Execution Replay by persisting traces.
    """

    def generate_report(
            self, context: TrustRepoContext) -> RuntimeHealthReport:
        report = RuntimeHealthReport(
            execution_id=context.execution_id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )

        for trace in context.execution_trace:
            stage = PipelineStageMetric(
                stage_name=trace.get("layer", "Unknown"),
                status=trace.get("status", "UNKNOWN"),
                duration_s=trace.get("time_s", 0.0),
                objects_created=trace.get("objects_created", 0),
                objects_destroyed=0,
                peak_memory_mb=trace.get("memory_mb", 0.0),
                cpu_utilization_pct=trace.get("cpu_pct", 0.0),
                errors=len(trace.get("errors", [])),
                warnings=len(trace.get("warnings", []))
            )
            report.stage_metrics.append(stage)
            report.total_objects_created += stage.objects_created
            report.total_errors += stage.errors
            report.total_warnings += stage.warnings
            report.total_duration_s += stage.duration_s

            if stage.status == "FAILED":
                report.status = "FAIL"

        return report

    def save_execution_trace(
            self, context: TrustRepoContext, output_path: str):
        """Saves the context trace for Execution Replay."""
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(context.model_dump(mode='json'), f, indent=2)

    def load_execution_trace(self, input_path: str) -> TrustRepoContext:
        """Loads a persisted context trace for Execution Replay."""
        import json
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return TrustRepoContext.model_validate(data)
