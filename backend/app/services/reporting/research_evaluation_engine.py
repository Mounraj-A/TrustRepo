from pydantic import BaseModel
from typing import Dict


class ResearchEvaluationReport(BaseModel):
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    accuracy: float = 0.0
    coverage: float = 0.0
    latency_ms: float = 0.0
    scalability_score: float = 0.0
    false_discovery_rate: float = 0.0
    mcc: float = 0.0  # Matthews Correlation Coefficient
    false_positives: int = 0
    false_negatives: int = 0


class ResearchEvaluationEngine:
    """
    Evaluates TrustRepo against ground truth datasets to compute
    dissertation-grade research metrics including MCC and FDR.
    """

    def evaluate(self, predictions: Dict[str, bool],
                 ground_truth: Dict[str, bool]) -> ResearchEvaluationReport:
        tp = 0
        fp = 0
        fn = 0
        tn = 0

        for key, expected in ground_truth.items():
            predicted = predictions.get(key, False)
            if expected and predicted:
                tp += 1
            elif expected and not predicted:
                fn += 1
            elif not expected and predicted:
                fp += 1
            elif not expected and not predicted:
                tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision +
                                         recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / (tp + tn + fp +
                                fn) if (tp + tn + fp + fn) > 0 else 0.0

        fdr = fp / (fp + tp) if (fp + tp) > 0 else 0.0

        # Matthews Correlation Coefficient
        import math
        mcc_denominator = math.sqrt(
            (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = ((tp * tn) - (fp * fn)) / \
            mcc_denominator if mcc_denominator > 0 else 0.0

        return ResearchEvaluationReport(
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            accuracy=round(accuracy, 4),
            false_discovery_rate=round(fdr, 4),
            mcc=round(mcc, 4),
            false_positives=fp,
            false_negatives=fn,
            coverage=1.0,  # Placeholder
            latency_ms=0.0,  # Placeholder
            scalability_score=1.0  # Placeholder
        )
