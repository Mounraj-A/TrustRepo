"""
Regression Test Suite for TrustRepo Enterprise Reasoning Pipeline

Measures precision/recall of the Expected vs Observed feature extraction
and verdict resolution.
"""
from app.services.verification.decision_matrix import DecisionMatrix, DecisionVerdictState

def test_decision_matrix_verified():
    engine = DecisionMatrix()
    expected = ["spring boot", "jwt", "jpa"]
    observed = ["spring boot", "jwt", "jpa"]
    
    result = engine.evaluate(expected, observed, "")
    assert result.final_verdict == DecisionVerdictState.VERIFIED
    assert result.coverage_score == 1.0
    assert result.consistency_score == 1.0

def test_decision_matrix_contradiction():
    engine = DecisionMatrix()
    expected = ["jwt"]
    observed = ["oauth2"]
    
    result = engine.evaluate(expected, observed, "")
    assert result.final_verdict == DecisionVerdictState.CONTRADICTION
    assert len(result.contradicted_features) == 1

def test_decision_matrix_missing_documentation():
    engine = DecisionMatrix()
    expected = ["jwt"]
    observed = []
    
    result = engine.evaluate(expected, observed, "")
    assert result.final_verdict == DecisionVerdictState.MISSING_DOCUMENTATION
    assert result.coverage_score == 0.0

def test_decision_matrix_unsupported_documentation():
    engine = DecisionMatrix()
    expected = ["spring boot"]
    observed = ["spring boot", "redis"]
    
    result = engine.evaluate(expected, observed, "")
    assert result.final_verdict == DecisionVerdictState.UNSUPPORTED_DOCUMENTATION
    assert result.coverage_score == 1.0
    assert "redis" in result.unsupported_features

def test_decision_matrix_partial_documentation():
    engine = DecisionMatrix()
    expected = ["spring boot", "jwt", "jpa"]
    observed = ["spring boot", "jpa"]
    
    result = engine.evaluate(expected, observed, "")
    assert result.final_verdict == DecisionVerdictState.PARTIAL_DOCUMENTATION
    assert result.coverage_score == 0.6667
    assert "jwt" in result.missing_features
