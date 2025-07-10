"""
Deontological Smart Contract

Implements deontological (duty-based) ethical rules like "Do not lie", "Keep promises", etc.
Aligns with paper's Command: Deontological Smart Contracts for encoding moral duties.
"""

import logging
import re
from typing import Dict, Any, List
from .base_contract import BaseSmartContract

logger = logging.getLogger(__name__)

class DeonticRuleContract(BaseSmartContract):
    """
    Smart contract for evaluating deontological ethical rules.
    
    Based on Kantian ethics - actions are right or wrong based on adherence to duty,
    not consequences. Rules must be universalizable and respect rational autonomy.
    """
    
    def __init__(self):
        super().__init__("DeonticRuleContract", "1.0.0")
        
        # Define the core deontological rules
        # Aligns with paper's emphasis on encoding fundamental moral duties
        self.rules = {
            "do_not_lie": {
                "rule_id": "deontic_001",
                "rule_name": "Do Not Lie",
                "description": "The duty to communicate truthfully and not deceive others",
                "keywords": ["lie", "deceive", "false", "mislead", "dishonest", "untrue", "fabricate"],
                "universalizability_test": "If everyone lied, communication would become meaningless",
                "weight": 1.0
            },
            "keep_promises": {
                "rule_id": "deontic_002", 
                "rule_name": "Keep Promises",
                "description": "The duty to fulfill commitments and honor agreements",
                "keywords": ["promise", "commitment", "agreement", "pledge", "vow", "contract", "break"],
                "universalizability_test": "If everyone broke promises, trust would be impossible",
                "weight": 0.9
            },
            "respect_autonomy": {
                "rule_id": "deontic_003",
                "rule_name": "Respect Personal Autonomy", 
                "description": "The duty to treat rational beings as ends in themselves, not mere means",
                "keywords": ["manipulate", "exploit", "coerce", "force", "consent", "autonomy", "dignity"],
                "universalizability_test": "Treating people as mere tools violates their rational nature",
                "weight": 1.0
            },
            "do_not_steal": {
                "rule_id": "deontic_004",
                "rule_name": "Do Not Steal",
                "description": "The duty to respect others' property rights",
                "keywords": ["steal", "theft", "rob", "take", "property", "belong", "owner"],
                "universalizability_test": "If everyone stole, property rights would be meaningless",
                "weight": 0.8
            },
            "do_not_harm": {
                "rule_id": "deontic_005",
                "rule_name": "Do Not Cause Unnecessary Harm",
                "description": "The duty to avoid causing suffering or damage without justification",
                "keywords": ["harm", "hurt", "damage", "injure", "violence", "pain", "suffer"],
                "universalizability_test": "Causing unnecessary harm violates the dignity of rational beings",
                "weight": 0.9
            }
        }
        
        logger.info(f"Loaded {len(self.rules)} deontological rules")
    
    def check_compliance(self, action_description: str, **kwargs) -> Dict[str, Any]:
        """
        Check if an action complies with deontological duties.
        
        Analyzes the action description against fundamental moral duties
        using keyword matching and rule-based reasoning.
        """
        # Validate input
        if not isinstance(action_description, str) or not action_description.strip():
            return {
                "compliant": False,
                "confidence": 0.0,
                "reasoning": "Invalid or empty action description",
                "rule_applied": "input_validation"
            }
        
        action_description = self._sanitize_text_input(action_description, max_length=2000)
        action_lower = action_description.lower()
        
        # Track all rule violations found
        violations = []
        max_violation_weight = 0.0
        
        # Check each deontological rule
        for rule_key, rule_data in self.rules.items():
            violation_score = self._check_rule_violation(action_lower, rule_data)
            
            if violation_score > 0.3:  # Threshold for considering it a violation
                violations.append({
                    "rule": rule_data["rule_name"],
                    "rule_id": rule_data["rule_id"],
                    "violation_score": violation_score,
                    "weight": rule_data["weight"],
                    "weighted_score": violation_score * rule_data["weight"]
                })
                max_violation_weight = max(max_violation_weight, violation_score * rule_data["weight"])
        
        # Determine compliance based on violations
        if not violations:
            result = {
                "compliant": True,
                "confidence": 0.8,
                "reasoning": "No deontological duty violations detected in the action description",
                "rule_applied": "comprehensive_duty_check",
                "violations": []
            }
        else:
            # Sort violations by weighted score
            violations.sort(key=lambda x: x["weighted_score"], reverse=True)
            primary_violation = violations[0]
            
            result = {
                "compliant": False,
                "confidence": min(0.9, max_violation_weight),
                "reasoning": f"Action appears to violate the duty: {primary_violation['rule']}. " +
                           f"Deontological ethics requires adherence to moral duties regardless of consequences.",
                "rule_applied": primary_violation["rule_id"],
                "violations": violations
            }
        
        # Log the evaluation
        self._log_call("check_compliance", {"action": action_description}, result)
        
        # Update contract state with recent evaluations
        self._track_evaluation(action_description, result)
        
        return result
    
    def _check_rule_violation(self, action_text: str, rule_data: Dict[str, Any]) -> float:
        """
        Check how strongly an action violates a specific deontological rule.
        
        Returns a score from 0.0 (no violation) to 1.0 (clear violation).
        """
        keywords = rule_data["keywords"]
        violation_score = 0.0
        
        # Count keyword matches
        keyword_matches = 0
        for keyword in keywords:
            if keyword in action_text:
                keyword_matches += 1
                
                # Some keywords are stronger indicators
                if keyword in ["lie", "deceive", "steal", "manipulate", "coerce"]:
                    violation_score += 0.3
                else:
                    violation_score += 0.1
        
        # Boost score if multiple keywords match
        if keyword_matches > 1:
            violation_score += 0.2
        
        # Apply contextual analysis for specific rules
        if rule_data["rule_id"] == "deontic_001":  # Do not lie
            violation_score += self._analyze_deception_context(action_text)
        elif rule_data["rule_id"] == "deontic_003":  # Respect autonomy  
            violation_score += self._analyze_autonomy_violation(action_text)
        
        return min(1.0, violation_score)
    
    def _analyze_deception_context(self, text: str) -> float:
        """Analyze text for deception-related patterns."""
        deception_patterns = [
            r"tell.*(?:false|untrue|lie)",
            r"make.*(?:false|misleading).*claim",
            r"hide.*truth",
            r"deliberately.*mislead",
            r"provide.*false.*information"
        ]
        
        score = 0.0
        for pattern in deception_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.3
        
        return min(0.6, score)
    
    def _analyze_autonomy_violation(self, text: str) -> float:
        """Analyze text for autonomy violation patterns."""
        autonomy_patterns = [
            r"(?:force|coerce).*(?:into|to)",
            r"manipulate.*(?:into|to)",
            r"without.*consent",
            r"against.*will",
            r"exploit.*(?:weakness|vulnerability)"
        ]
        
        score = 0.0
        for pattern in autonomy_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.4
        
        return min(0.7, score)
    
    def _track_evaluation(self, action: str, result: Dict[str, Any]):
        """Track evaluation history for analysis and improvement."""
        evaluations = self.get_state("recent_evaluations") or []
        
        # Keep only last 100 evaluations
        if len(evaluations) >= 100:
            evaluations = evaluations[-99:]
        
        evaluations.append({
            "action": action[:200],  # Truncate for storage
            "compliant": result["compliant"],
            "confidence": result["confidence"],
            "rule_applied": result["rule_applied"],
            "timestamp": self.deployed_at
        })
        
        self.update_state("recent_evaluations", evaluations)
    
    def get_applicable_rules(self) -> List[Dict[str, Any]]:
        """Return all deontological rules this contract can evaluate."""
        return [
            {
                "rule_id": rule_data["rule_id"],
                "rule_name": rule_data["rule_name"],
                "description": rule_data["description"],
                "parameters": ["action_description"],
                "universalizability_test": rule_data["universalizability_test"]
            }
            for rule_data in self.rules.values()
        ]
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get statistics about rule evaluations."""
        evaluations = self.get_state("recent_evaluations") or []
        
        if not evaluations:
            return {"total_evaluations": 0, "compliance_rate": 0.0}
        
        total = len(evaluations)
        compliant = sum(1 for e in evaluations if e["compliant"])
        
        # Count violations by rule
        rule_violations = {}
        for evaluation in evaluations:
            if not evaluation["compliant"]:
                rule = evaluation["rule_applied"]
                rule_violations[rule] = rule_violations.get(rule, 0) + 1
        
        return {
            "total_evaluations": total,
            "compliance_rate": compliant / total,
            "violation_count": total - compliant,
            "rule_violations": rule_violations,
            "average_confidence": sum(e["confidence"] for e in evaluations) / total
        }
    
    def check_universalizability(self, maxim: str) -> Dict[str, Any]:
        """
        Test if a maxim (personal rule) can be universalized without contradiction.
        
        This implements Kant's Categorical Imperative test.
        """
        maxim = self._sanitize_text_input(maxim, max_length=500)
        
        # Simple heuristic-based universalizability test
        contradictory_patterns = [
            r"only.*(?:i|me|myself)",
            r"nobody.*else",
            r"except.*(?:me|myself)",
            r"when.*(?:convenient|beneficial).*to.*me"
        ]
        
        contradiction_score = 0.0
        for pattern in contradictory_patterns:
            if re.search(pattern, maxim.lower(), re.IGNORECASE):
                contradiction_score += 0.3
        
        universalizable = contradiction_score < 0.4
        
        result = {
            "universalizable": universalizable,
            "confidence": 0.7 if universalizable else min(0.9, contradiction_score + 0.5),
            "reasoning": "Maxim passes universalizability test" if universalizable else 
                        "Maxim contains self-exception or contradiction when universalized",
            "contradiction_score": contradiction_score
        }
        
        self._log_call("check_universalizability", {"maxim": maxim}, result)
        return result 