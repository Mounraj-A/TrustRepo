from app.models.trustrepo_context import TrustRepoContext
from app.services.reporting.report_generator import ReportGenerator


class ReportingPipeline:
    def __init__(self):
        self.generator = ReportGenerator()

    def run(self, context: TrustRepoContext) -> TrustRepoContext:
        print("--- Layer 7: Report Generation ---")
        report = self.generator.generate_report(context)
        context.report_context.report = report

        print("Final TrustReport generated.")
        return context
