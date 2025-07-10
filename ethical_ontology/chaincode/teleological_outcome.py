"""
Teleological Outcome Tracking Smart Contract

Implements consequentialist/utilitarian ethics by evaluating actions based on their outcomes.
Aligns with paper's teleological outcome tracking requirements for ethical AI governance.
"""

import logging
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from .base_contract import BaseSmartContract

logger = logging.getLogger(__name__)

class TeleologicalOutcomeContract(BaseSmartContract):
    """
    Smart contract for evaluating actions based on their consequences and outcomes.
    
    Based on utilitarian and consequentialist ethics - actions are right insofar as
    they promote the greatest good for the greatest number (utility maximization).
    """
    
    def __init__(self):
        super().__init__("TeleologicalOutcomeContract", "1.0.0")
        
        # Define outcome categories and their weights
        # Aligns with paper's teleological outcome tracking
        self.outcome_categories = {
            "wellbeing": {
                "category_id": "outcome_001",
                "category_name": "Human Wellbeing",
                "description": "Physical and mental health, happiness, life satisfaction",
                "positive_keywords": ["improve", "enhance", "benefit", "wellbeing", "health", "happiness", "flourish"],
                "negative_keywords": ["harm", "damage", "hurt", "suffering", "pain", "deteriorate", "worsen"],
                "weight": 1.0,
                "aggregation_type": "utilitarian"  # Sum across all affected parties
            },
            "autonomy": {
                "category_id": "outcome_002",
                "category_name": "Personal Autonomy",
                "description": "Freedom of choice, self-determination, empowerment",
                "positive_keywords": ["empower", "freedom", "choice", "control", "independence", "self-determination"],
                "negative_keywords": ["restrict", "limit", "control", "coerce", "dependent", "constrain"],
                "weight": 0.9,
                "aggregation_type": "priority"  # Protect individual rights
            },
            "justice": {
                "category_id": "outcome_003",
                "category_name": "Social Justice",
                "description": "Fairness, equality, distribution of benefits and burdens",
                "positive_keywords": ["fair", "equal", "just", "equitable", "inclusive", "distribute"],
                "negative_keywords": ["unfair", "unequal", "biased", "discriminate", "exclude", "privilege"],
                "weight": 0.9,
                "aggregation_type": "maximin"  # Help the worst-off
            },
            "knowledge": {
                "category_id": "outcome_004",
                "category_name": "Knowledge and Truth",
                "description": "Understanding, education, scientific progress, information accuracy",
                "positive_keywords": ["learn", "educate", "understand", "truth", "knowledge", "discover", "research"],
                "negative_keywords": ["ignorance", "misinform", "deceive", "hide", "suppress", "false"],
                "weight": 0.7,
                "aggregation_type": "utilitarian"
            },
            "environment": {
                "category_id": "outcome_005",
                "category_name": "Environmental Impact",
                "description": "Sustainability, ecological health, resource conservation",
                "positive_keywords": ["sustainable", "green", "conservation", "renewable", "eco-friendly", "preserve"],
                "negative_keywords": ["pollute", "waste", "destroy", "unsustainable", "deplete", "contaminate"],
                "weight": 0.8,
                "aggregation_type": "intergenerational"  # Consider future generations
            },
            "social_cohesion": {
                "category_id": "outcome_006",
                "category_name": "Social Cohesion",
                "description": "Community bonds, trust, cooperation, social stability",
                "positive_keywords": ["unite", "cooperate", "trust", "community", "solidarity", "together"],
                "negative_keywords": ["divide", "conflict", "mistrust", "isolate", "fragment", "discord"],
                "weight": 0.6,
                "aggregation_type": "utilitarian"
            }
        }
        
        # Track outcome predictions and actual results over time
        self.outcome_history: List[Dict[str, Any]] = []
        
        logger.info(f"Loaded {len(self.outcome_categories)} outcome categories")
    
    def check_compliance(self, action_description: str, **kwargs) -> Dict[str, Any]:
        """
        Evaluate an action based on its predicted consequences and outcomes.
        
        Analyzes the likely outcomes across multiple dimensions and calculates
        an overall utility score based on consequentialist principles.
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
        
        # Extract additional parameters
        affected_parties = kwargs.get("affected_parties", 1)  # Number of people affected
        time_horizon = kwargs.get("time_horizon", "short_term")  # short_term, medium_term, long_term
        certainty_level = kwargs.get("certainty_level", 0.7)  # Confidence in outcome prediction
        pvb_data_hash = kwargs.get('pvb_data_hash')
        is_pvb_verified = True
        if pvb_data_hash:
            try:
                import requests
                oracle_url = f'http://oracle_bridge:3000/verify_pvb_data?data_hash={pvb_data_hash}'
                response = requests.get(oracle_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    is_pvb_verified = data.get('is_verified', False)
                    logger.info(f'PVB verification for {pvb_data_hash}: {is_pvb_verified}')
                else:
                    logger.warning(f'Oracle request failed: {response.status_code}')
                    is_pvb_verified = False
            except Exception as e:
                logger.error(f'Error querying oracle: {e}')
                is_pvb_verified = False
        
        # Analyze outcomes
        outcome_analysis = self._analyze_outcomes(action_description.lower())
        
        if not is_pvb_verified:
            for analysis in outcome_analysis.values():
                analysis['net_outcome_score'] = -1.0
                analysis['evidence'].append('PVB verification failed - negative outcome assumed')
        
        # Calculate weighted utility score
        total_utility = 0.0
        total_weight = 0.0
        
        for category_key, analysis in outcome_analysis.items():
            category_data = self.outcome_categories[category_key]
            
            # Apply aggregation method specific to each category
            aggregated_score = self._apply_aggregation_method(
                analysis["net_outcome_score"],
                category_data["aggregation_type"],
                affected_parties
            )
            
            # Apply time horizon adjustment
            time_adjusted_score = self._apply_time_horizon_adjustment(
                aggregated_score, time_horizon
            )
            
            # Weight by category importance and certainty
            weighted_score = time_adjusted_score * category_data["weight"] * certainty_level
            total_utility += weighted_score
            total_weight += category_data["weight"]
        
        # Normalize utility score
        if total_weight > 0:
            normalized_utility = total_utility / total_weight
        else:
            normalized_utility = 0.0
        
        # Determine compliance based on utility threshold
        utility_threshold = 0.1  # Minimum positive utility required
        
        if normalized_utility > utility_threshold:
            result = {
                "compliant": True,
                "confidence": min(0.9, 0.6 + abs(normalized_utility) * 0.3 * certainty_level),
                "reasoning": f"Action is predicted to produce net positive outcomes with utility score: {normalized_utility:.3f}. " +
                           f"Expected to benefit {affected_parties} parties over {time_horizon} timeframe.",
                "rule_applied": "utility_maximization",
                "utility_score": normalized_utility,
                "outcome_analysis": outcome_analysis,
                "affected_parties": affected_parties,
                "time_horizon": time_horizon
            }
        elif normalized_utility < -utility_threshold:
            result = {
                "compliant": False,
                "confidence": min(0.9, 0.6 + abs(normalized_utility) * 0.3 * certainty_level),
                "reasoning": f"Action is predicted to produce net negative outcomes with utility score: {normalized_utility:.3f}. " +
                           f"Expected to harm {affected_parties} parties over {time_horizon} timeframe.",
                "rule_applied": "harm_prevention",
                "utility_score": normalized_utility,
                "outcome_analysis": outcome_analysis,
                "affected_parties": affected_parties,
                "time_horizon": time_horizon
            }
        else:
            result = {
                "compliant": True,
                "confidence": 0.5,
                "reasoning": f"Action appears outcome-neutral with utility score: {normalized_utility:.3f}. " +
                           f"Minimal predicted impact on {affected_parties} parties over {time_horizon} timeframe.",
                "rule_applied": "outcome_neutrality",
                "utility_score": normalized_utility,
                "outcome_analysis": outcome_analysis,
                "affected_parties": affected_parties,
                "time_horizon": time_horizon
            }
        
        # Track prediction for later validation
        self._track_outcome_prediction(action_description, result)
        
        # Log the evaluation
        self._log_call("check_compliance", {
            "action": action_description,
            "affected_parties": affected_parties,
            "time_horizon": time_horizon,
            "certainty": certainty_level
        }, result)
        
        return result
    
    def _analyze_outcomes(self, action_text: str) -> Dict[str, Dict[str, Any]]:
        """
        Analyze text for outcome indicators across all categories.
        
        Returns analysis for each outcome category with predicted impacts.
        """
        analysis = {}
        
        for category_key, category_data in self.outcome_categories.items():
            positive_score = 0.0
            negative_score = 0.0
            evidence = []
            
            # Check for positive outcome keywords
            for keyword in category_data["positive_keywords"]:
                if keyword in action_text:
                    positive_score += 0.2
                    evidence.append(f"Positive: '{keyword}'")
            
            # Check for negative outcome keywords
            for keyword in category_data["negative_keywords"]:
                if keyword in action_text:
                    negative_score += 0.2
                    evidence.append(f"Negative: '{keyword}'")
            
            # Apply category-specific contextual analysis
            context_positive, context_negative = self._analyze_outcome_context(
                action_text, category_key, category_data
            )
            positive_score += context_positive
            negative_score += context_negative
            
            analysis[category_key] = {
                "category_name": category_data["category_name"],
                "positive_score": min(1.0, positive_score),
                "negative_score": min(1.0, negative_score),
                "net_outcome_score": positive_score - negative_score,
                "weight": category_data["weight"],
                "evidence": evidence,
                "aggregation_type": category_data["aggregation_type"]
            }
        
        return analysis
    
    def _analyze_outcome_context(self, text: str, category_key: str, category_data: Dict[str, Any]) -> Tuple[float, float]:
        """Apply context-specific analysis for different outcome categories."""
        positive_score = 0.0
        negative_score = 0.0
        
        if category_key == "wellbeing":
            # Look for wellbeing-specific patterns
            wellbeing_positive = [r"improve.*(?:health|wellbeing)", r"reduce.*(?:suffering|pain)", r"increase.*happiness"]
            wellbeing_negative = [r"cause.*(?:harm|suffering)", r"reduce.*(?:health|wellbeing)", r"increase.*pain"]
            
            for pattern in wellbeing_positive:
                if re.search(pattern, text, re.IGNORECASE):
                    positive_score += 0.3
            
            for pattern in wellbeing_negative:
                if re.search(pattern, text, re.IGNORECASE):
                    negative_score += 0.3
        
        elif category_key == "justice":
            # Look for justice/equity patterns
            justice_positive = [r"increase.*(?:equality|fairness)", r"reduce.*(?:inequality|discrimination)", r"ensure.*(?:fair|equal)"]
            justice_negative = [r"increase.*(?:inequality|discrimination)", r"unfair.*(?:advantage|treatment)", r"exclude.*from"]
            
            for pattern in justice_positive:
                if re.search(pattern, text, re.IGNORECASE):
                    positive_score += 0.3
            
            for pattern in justice_negative:
                if re.search(pattern, text, re.IGNORECASE):
                    negative_score += 0.3
        
        elif category_key == "environment":
            # Look for environmental impact patterns
            env_positive = [r"reduce.*(?:pollution|waste)", r"sustainable.*(?:practice|development)", r"conserve.*(?:energy|resources)"]
            env_negative = [r"increase.*(?:pollution|waste)", r"damage.*environment", r"deplete.*(?:resources|energy)"]
            
            for pattern in env_positive:
                if re.search(pattern, text, re.IGNORECASE):
                    positive_score += 0.3
            
            for pattern in env_negative:
                if re.search(pattern, text, re.IGNORECASE):
                    negative_score += 0.3
        
        return positive_score, negative_score
    
    def _apply_aggregation_method(self, base_score: float, aggregation_type: str, affected_parties: int) -> float:
        """Apply different aggregation methods based on ethical theory."""
        if aggregation_type == "utilitarian":
            # Simple sum - more affected parties = higher impact
            return base_score * affected_parties
        
        elif aggregation_type == "priority":
            # Prioritarian - diminishing marginal utility
            if affected_parties <= 1:
                return base_score
            else:
                # Square root to model diminishing returns
                return base_score * (affected_parties ** 0.5)
        
        elif aggregation_type == "maximin":
            # Rawlsian maximin - focus on worst-off
            if base_score < 0:
                return base_score * 2.0  # Amplify negative impacts
            else:
                return base_score * 0.8  # Moderate positive impacts
        
        elif aggregation_type == "intergenerational":
            # Consider future generations (simplified)
            future_multiplier = 1.5 if base_score < 0 else 1.2
            return base_score * future_multiplier
        
        else:
            return base_score
    
    def _apply_time_horizon_adjustment(self, score: float, time_horizon: str) -> float:
        """Adjust scores based on time horizon of effects."""
        if time_horizon == "short_term":
            return score * 0.8  # Short-term effects weighted less
        elif time_horizon == "medium_term":
            return score * 1.0  # Medium-term effects weighted normally
        elif time_horizon == "long_term":
            return score * 1.3  # Long-term effects weighted more
        else:
            return score
    
    def _track_outcome_prediction(self, action: str, prediction_result: Dict[str, Any]):
        """Track outcome predictions for later validation and learning."""
        prediction_record = {
            "action": action[:200],  # Truncate for storage
            "predicted_utility": prediction_result["utility_score"],
            "predicted_outcomes": prediction_result["outcome_analysis"],
            "timestamp": time.time(),
            "prediction_id": f"pred_{int(time.time() * 1000)}"
        }
        
        self.outcome_history.append(prediction_record)
        
        # Keep only last 500 predictions
        if len(self.outcome_history) > 500:
            self.outcome_history = self.outcome_history[-500:]
        
        # Store in contract state
        self.update_state("outcome_predictions", self.outcome_history)
    
    def update_actual_outcome(self, prediction_id: str, actual_outcomes: Dict[str, float], 
                            actual_utility: float) -> Dict[str, Any]:
        """
        Update a prediction with actual observed outcomes.
        
        This enables learning and calibration of the outcome prediction model.
        """
        # Find the prediction
        prediction = None
        for pred in self.outcome_history:
            if pred["prediction_id"] == prediction_id:
                prediction = pred
                break
        
        if not prediction:
            return {"error": f"Prediction {prediction_id} not found"}
        
        # Calculate prediction accuracy
        predicted_utility = prediction["predicted_utility"]
        utility_error = abs(predicted_utility - actual_utility)
        accuracy = max(0.0, 1.0 - utility_error)
        
        # Update prediction record
        prediction["actual_utility"] = actual_utility
        prediction["actual_outcomes"] = actual_outcomes
        prediction["utility_error"] = utility_error
        prediction["accuracy"] = accuracy
        prediction["updated_at"] = time.time()
        
        # Store updated history
        self.update_state("outcome_predictions", self.outcome_history)
        
        result = {
            "prediction_id": prediction_id,
            "predicted_utility": predicted_utility,
            "actual_utility": actual_utility,
            "utility_error": utility_error,
            "accuracy": accuracy,
            "learning_signal": "positive" if accuracy > 0.7 else "negative"
        }
        
        self._log_call("update_actual_outcome", {"prediction_id": prediction_id}, result)
        return result
    
    def get_applicable_rules(self) -> List[Dict[str, Any]]:
        """Return all outcome-based rules this contract can evaluate."""
        return [
            {
                "rule_id": category_data["category_id"],
                "rule_name": category_data["category_name"],
                "description": category_data["description"],
                "parameters": ["action_description", "affected_parties", "time_horizon", "certainty_level"],
                "aggregation_type": category_data["aggregation_type"]
            }
            for category_data in self.outcome_categories.values()
        ]
    
    def get_prediction_accuracy_metrics(self) -> Dict[str, Any]:
        """Get metrics on the accuracy of outcome predictions."""
        predictions_with_outcomes = [
            p for p in self.outcome_history 
            if "actual_utility" in p
        ]
        
        if not predictions_with_outcomes:
            return {
                "total_predictions": len(self.outcome_history),
                "validated_predictions": 0,
                "average_accuracy": 0.0,
                "validation_rate": 0.0
            }
        
        total_predictions = len(self.outcome_history)
        validated_count = len(predictions_with_outcomes)
        average_accuracy = sum(p["accuracy"] for p in predictions_with_outcomes) / validated_count
        average_error = sum(p["utility_error"] for p in predictions_with_outcomes) / validated_count
        
        return {
            "total_predictions": total_predictions,
            "validated_predictions": validated_count,
            "validation_rate": validated_count / total_predictions,
            "average_accuracy": average_accuracy,
            "average_utility_error": average_error,
            "high_accuracy_rate": sum(1 for p in predictions_with_outcomes if p["accuracy"] > 0.8) / validated_count
        }
    
    def simulate_outcome_scenario(self, base_action: str, scenario_modifications: List[str]) -> Dict[str, Any]:
        """
        Simulate different outcome scenarios for comparative analysis.
        
        Useful for exploring alternative actions and their predicted consequences.
        """
        scenarios = {}
        
        # Analyze base action
        base_result = self.check_compliance(base_action)
        scenarios["base"] = {
            "action": base_action,
            "utility_score": base_result["utility_score"],
            "outcome_analysis": base_result["outcome_analysis"]
        }
        
        # Analyze modified scenarios
        for i, modification in enumerate(scenario_modifications):
            modified_action = f"{base_action} {modification}"
            modified_result = self.check_compliance(modified_action)
            scenarios[f"scenario_{i+1}"] = {
                "action": modified_action,
                "modification": modification,
                "utility_score": modified_result["utility_score"],
                "outcome_analysis": modified_result["outcome_analysis"],
                "utility_change": modified_result["utility_score"] - base_result["utility_score"]
            }
        
        # Find best scenario
        best_scenario = max(scenarios.keys(), key=lambda k: scenarios[k]["utility_score"])
        
        result = {
            "scenarios": scenarios,
            "best_scenario": best_scenario,
            "best_utility": scenarios[best_scenario]["utility_score"],
            "recommendation": scenarios[best_scenario]["action"] if best_scenario != "base" else "No modification improves outcomes"
        }
        
        self._log_call("simulate_outcome_scenario", {"base_action": base_action}, result)
        return result 