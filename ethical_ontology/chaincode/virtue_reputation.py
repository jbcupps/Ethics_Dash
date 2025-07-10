"""
Virtue-Based Reputation Smart Contract

Implements virtue ethics-based reputation system tracking character virtues and vices.
Aligns with paper's virtue-based reputation requirements for ethical AI governance.
"""

import logging
import re
import time
from typing import Dict, Any, List, Optional
from .base_contract import BaseSmartContract

logger = logging.getLogger(__name__)

class VirtueReputationContract(BaseSmartContract):
    """
    Smart contract for evaluating virtue ethics and maintaining reputation scores.
    
    Based on Aristotelian virtue ethics - focuses on character traits that lead
    to human flourishing (eudaimonia) and the golden mean between extremes.
    """
    
    def __init__(self):
        super().__init__("VirtueReputationContract", "1.0.0")
        
        # Define core virtues and their opposing vices
        # Aligns with paper's virtue-based reputation system
        self.virtues = {
            "honesty": {
                "virtue_id": "virtue_001",
                "virtue_name": "Honesty",
                "description": "Truthfulness and sincerity in communication and action",
                "positive_keywords": ["honest", "truthful", "sincere", "transparent", "genuine"],
                "vice_keywords": ["dishonest", "lie", "deceive", "fake", "insincere"],
                "deficiency_vice": "deceitfulness",
                "excess_vice": "brutal_honesty",
                "weight": 1.0
            },
            "courage": {
                "virtue_id": "virtue_002", 
                "virtue_name": "Courage",
                "description": "Firmness in facing difficulty, danger, or pain",
                "positive_keywords": ["brave", "courageous", "bold", "fearless", "stand_up"],
                "vice_keywords": ["cowardly", "fearful", "timid", "reckless", "rash"],
                "deficiency_vice": "cowardice",
                "excess_vice": "rashness",
                "weight": 0.9
            },
            "compassion": {
                "virtue_id": "virtue_003",
                "virtue_name": "Compassion", 
                "description": "Sympathetic concern for the suffering of others",
                "positive_keywords": ["compassionate", "empathetic", "caring", "kind", "help"],
                "vice_keywords": ["callous", "cruel", "indifferent", "heartless", "mean"],
                "deficiency_vice": "callousness",
                "excess_vice": "excessive_empathy",
                "weight": 0.9
            },
            "justice": {
                "virtue_id": "virtue_004",
                "virtue_name": "Justice",
                "description": "Giving each person what they deserve; fairness and equity",
                "positive_keywords": ["fair", "just", "equitable", "impartial", "rights"],
                "vice_keywords": ["unfair", "biased", "discriminate", "prejudice", "unjust"],
                "deficiency_vice": "injustice",
                "excess_vice": "rigid_legalism",
                "weight": 1.0
            },
            "temperance": {
                "virtue_id": "virtue_005",
                "virtue_name": "Temperance",
                "description": "Moderation and self-restraint in desires and actions",
                "positive_keywords": ["moderate", "restrained", "balanced", "disciplined", "controlled"],
                "vice_keywords": ["excessive", "indulgent", "extreme", "immoderate", "reckless"],
                "deficiency_vice": "insensibility",
                "excess_vice": "overindulgence",
                "weight": 0.8
            },
            "wisdom": {
                "virtue_id": "virtue_006",
                "virtue_name": "Practical Wisdom (Phronesis)",
                "description": "Good judgment and the ability to act appropriately in context",
                "positive_keywords": ["wise", "prudent", "thoughtful", "judicious", "discerning"],
                "vice_keywords": ["foolish", "imprudent", "rash", "thoughtless", "naive"],
                "deficiency_vice": "foolishness",
                "excess_vice": "overthinking",
                "weight": 0.9
            }
        }
        
        # Initialize reputation tracking
        self.agent_reputations: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Loaded {len(self.virtues)} virtue definitions")
    
    def check_compliance(self, action_description: str, **kwargs) -> Dict[str, Any]:
        """
        Evaluate an action based on virtue ethics principles.
        
        Analyzes the action for virtue/vice indicators and assesses
        alignment with character excellence and human flourishing.
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
        
        # Agent ID for reputation tracking (optional)
        agent_id = kwargs.get("agent_id", "anonymous")
        
        # Analyze virtue/vice content
        virtue_analysis = self._analyze_virtues(action_lower)
        
        # Calculate overall virtue score
        total_virtue_score = sum(v["virtue_score"] * v["weight"] for v in virtue_analysis.values())
        total_vice_score = sum(v["vice_score"] * v["weight"] for v in virtue_analysis.values())
        total_weight = sum(v["weight"] for v in virtue_analysis.values() if v["virtue_score"] > 0 or v["vice_score"] > 0)
        
        if total_weight == 0:
            # No virtue/vice indicators found
            result = {
                "compliant": True,
                "confidence": 0.5,
                "reasoning": "No clear virtue or vice indicators detected. Action appears ethically neutral.",
                "rule_applied": "virtue_neutrality",
                "virtue_analysis": virtue_analysis,
                "virtue_score": 0.0,
                "vice_score": 0.0
            }
        else:
            net_virtue_score = (total_virtue_score - total_vice_score) / total_weight
            
            # Determine compliance based on net virtue score
            if net_virtue_score > 0.2:
                result = {
                    "compliant": True,
                    "confidence": min(0.9, 0.6 + abs(net_virtue_score) * 0.3),
                    "reasoning": f"Action demonstrates virtuous character traits and aligns with human flourishing. Net virtue score: {net_virtue_score:.2f}",
                    "rule_applied": "virtue_excellence",
                    "virtue_analysis": virtue_analysis,
                    "virtue_score": total_virtue_score / total_weight,
                    "vice_score": total_vice_score / total_weight
                }
            elif net_virtue_score < -0.2:
                result = {
                    "compliant": False,
                    "confidence": min(0.9, 0.6 + abs(net_virtue_score) * 0.3),
                    "reasoning": f"Action demonstrates vicious character traits that impede human flourishing. Net virtue score: {net_virtue_score:.2f}",
                    "rule_applied": "vice_detection",
                    "virtue_analysis": virtue_analysis,
                    "virtue_score": total_virtue_score / total_weight,
                    "vice_score": total_vice_score / total_weight
                }
            else:
                result = {
                    "compliant": True,
                    "confidence": 0.6,
                    "reasoning": f"Action shows mixed virtue/vice indicators. Ethical evaluation depends on context and practical wisdom (phronesis).",
                    "rule_applied": "virtue_mixed",
                    "virtue_analysis": virtue_analysis,
                    "virtue_score": total_virtue_score / total_weight,
                    "vice_score": total_vice_score / total_weight
                }
        
        # Update agent reputation if specified
        if agent_id != "anonymous":
            self._update_agent_reputation(agent_id, result)
        
        # Log the evaluation
        self._log_call("check_compliance", {"action": action_description, "agent": agent_id}, result)
        
        return result
    
    def _analyze_virtues(self, action_text: str) -> Dict[str, Dict[str, Any]]:
        """
        Analyze text for virtue and vice indicators.
        
        Returns analysis for each virtue with scores and evidence.
        """
        analysis = {}
        
        for virtue_key, virtue_data in self.virtues.items():
            virtue_score = 0.0
            vice_score = 0.0
            evidence = []
            
            # Check for positive virtue keywords
            for keyword in virtue_data["positive_keywords"]:
                if keyword in action_text:
                    virtue_score += 0.2
                    evidence.append(f"Positive: '{keyword}'")
            
            # Check for vice keywords
            for keyword in virtue_data["vice_keywords"]:
                if keyword in action_text:
                    vice_score += 0.2
                    evidence.append(f"Negative: '{keyword}'")
            
            # Apply virtue-specific contextual analysis
            virtue_context_score, vice_context_score = self._analyze_virtue_context(
                action_text, virtue_key, virtue_data
            )
            virtue_score += virtue_context_score
            vice_score += vice_context_score
            
            analysis[virtue_key] = {
                "virtue_name": virtue_data["virtue_name"],
                "virtue_score": min(1.0, virtue_score),
                "vice_score": min(1.0, vice_score),
                "weight": virtue_data["weight"],
                "evidence": evidence,
                "net_score": virtue_score - vice_score
            }
        
        return analysis
    
    def _analyze_virtue_context(self, text: str, virtue_key: str, virtue_data: Dict[str, Any]) -> tuple[float, float]:
        """Apply context-specific analysis for different virtues."""
        virtue_score = 0.0
        vice_score = 0.0
        
        if virtue_key == "honesty":
            # Look for honesty/dishonesty patterns
            honesty_patterns = [r"tell.*truth", r"being.*honest", r"admit.*mistake"]
            dishonesty_patterns = [r"hide.*truth", r"deliberately.*mislead", r"cover.*up"]
            
            for pattern in honesty_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    virtue_score += 0.3
            
            for pattern in dishonesty_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    vice_score += 0.3
        
        elif virtue_key == "courage":
            # Look for courage/cowardice patterns
            courage_patterns = [r"stand.*up.*for", r"face.*(?:danger|difficulty)", r"defend.*(?:weak|innocent)"]
            cowardice_patterns = [r"avoid.*responsibility", r"abandon.*(?:duty|commitment)", r"flee.*from"]
            
            for pattern in courage_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    virtue_score += 0.3
            
            for pattern in cowardice_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    vice_score += 0.3
        
        elif virtue_key == "justice":
            # Look for justice/injustice patterns
            justice_patterns = [r"treat.*equally", r"give.*(?:fair|equal)", r"protect.*rights"]
            injustice_patterns = [r"discriminate.*against", r"unfair.*advantage", r"deny.*rights"]
            
            for pattern in justice_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    virtue_score += 0.3
            
            for pattern in injustice_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    vice_score += 0.3
        
        return virtue_score, vice_score
    
    def _update_agent_reputation(self, agent_id: str, evaluation_result: Dict[str, Any]):
        """Update an agent's virtue-based reputation score."""
        if agent_id not in self.agent_reputations:
            self.agent_reputations[agent_id] = {
                "total_evaluations": 0,
                "virtue_scores": {virtue: 0.0 for virtue in self.virtues.keys()},
                "overall_reputation": 0.5,  # Start neutral
                "created_at": time.time(),
                "last_updated": time.time()
            }
        
        agent_rep = self.agent_reputations[agent_id]
        agent_rep["total_evaluations"] += 1
        agent_rep["last_updated"] = time.time()
        
        # Update virtue scores using exponential moving average
        alpha = 0.1  # Learning rate
        virtue_analysis = evaluation_result.get("virtue_analysis", {})
        
        for virtue_key, analysis in virtue_analysis.items():
            current_score = agent_rep["virtue_scores"][virtue_key]
            new_score = analysis["net_score"]
            agent_rep["virtue_scores"][virtue_key] = (1 - alpha) * current_score + alpha * new_score
        
        # Calculate overall reputation as weighted average of virtue scores
        total_weighted_score = sum(
            score * self.virtues[virtue]["weight"] 
            for virtue, score in agent_rep["virtue_scores"].items()
        )
        total_weight = sum(virtue_data["weight"] for virtue_data in self.virtues.values())
        agent_rep["overall_reputation"] = max(0.0, min(1.0, 0.5 + total_weighted_score / total_weight))
        
        # Store in contract state
        self.update_state(f"reputation_{agent_id}", agent_rep)
    
    def get_agent_reputation(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the reputation profile for a specific agent."""
        return self.agent_reputations.get(agent_id) or self.get_state(f"reputation_{agent_id}")
    
    def get_applicable_rules(self) -> List[Dict[str, Any]]:
        """Return all virtue rules this contract can evaluate."""
        return [
            {
                "rule_id": virtue_data["virtue_id"],
                "rule_name": virtue_data["virtue_name"],
                "description": virtue_data["description"],
                "parameters": ["action_description", "agent_id (optional)"],
                "deficiency_vice": virtue_data["deficiency_vice"],
                "excess_vice": virtue_data["excess_vice"]
            }
            for virtue_data in self.virtues.values()
        ]
    
    def assess_golden_mean(self, virtue_key: str, intensity: float) -> Dict[str, Any]:
        """
        Assess if an action intensity represents the virtuous mean between extremes.
        
        Implements Aristotle's doctrine of the golden mean.
        """
        if virtue_key not in self.virtues:
            return {"error": f"Unknown virtue: {virtue_key}"}
        
        virtue_data = self.virtues[virtue_key]
        
        # Golden mean is around 0.5-0.7 range (moderate virtue)
        if 0.4 <= intensity <= 0.7:
            assessment = "virtuous_mean"
            reasoning = f"Action demonstrates appropriate {virtue_data['virtue_name']} - the golden mean between extremes"
        elif intensity < 0.4:
            assessment = "deficiency_vice"
            reasoning = f"Action shows deficiency in {virtue_data['virtue_name']}, trending toward {virtue_data['deficiency_vice']}"
        else:  # intensity > 0.7
            assessment = "excess_vice"
            reasoning = f"Action shows excess in {virtue_data['virtue_name']}, trending toward {virtue_data['excess_vice']}"
        
        result = {
            "virtue": virtue_data["virtue_name"],
            "intensity": intensity,
            "assessment": assessment,
            "reasoning": reasoning,
            "deficiency_vice": virtue_data["deficiency_vice"],
            "excess_vice": virtue_data["excess_vice"]
        }
        
        self._log_call("assess_golden_mean", {"virtue": virtue_key, "intensity": intensity}, result)
        return result
    
    def get_reputation_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top-ranked agents by overall reputation."""
        all_reps = []
        
        # Collect from current session
        for agent_id, rep_data in self.agent_reputations.items():
            all_reps.append({
                "agent_id": agent_id,
                "overall_reputation": rep_data["overall_reputation"],
                "total_evaluations": rep_data["total_evaluations"]
            })
        
        # Sort by reputation score
        all_reps.sort(key=lambda x: x["overall_reputation"], reverse=True)
        
        return all_reps[:limit] 