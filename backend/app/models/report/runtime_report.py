from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class PipelineStageMetric(BaseModel):
    stage_name: str
    status: str
    duration_s: float
    objects_created: int = 0
    objects_destroyed: int = 0
    peak_memory_mb: float = 0.0
    cpu_utilization_pct: float = 0.0
    errors: int = 0
    warnings: int = 0


class RuntimeHealthReport(BaseModel):
    execution_id: str
    start_time: datetime
    end_time: datetime
    total_duration_s: float = 0.0

    # Global Metrics
    global_peak_memory_mb: float = 0.0
    global_avg_cpu_pct: float = 0.0

    # Granular Metrics
    stage_metrics: List[PipelineStageMetric] = Field(default_factory=list)

    # Summary
    total_objects_created: int = 0
    total_objects_destroyed: int = 0
    total_errors: int = 0
    total_warnings: int = 0

    status: str = "PASS"
