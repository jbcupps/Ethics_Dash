from ..base_contract import BaseSmartContract

class CoreOntologyContract(BaseSmartContract):
    def __init__(self):
        super().__init__("CoreOntology", "1.0.0")
        self.shared_rules = {
            "universal_respect": "Treat all beings with inherent dignity."
        }

    def get_shared_rule(self, rule_name: str) -> str:
        return self.shared_rules.get(rule_name, "Rule not found") 