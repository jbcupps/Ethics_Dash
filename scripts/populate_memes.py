import os
import json
import time
import sys
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, InvalidURI
from dotenv import load_dotenv
from bson import ObjectId, json_util
import re
from urllib.parse import quote_plus, urlparse, urlunparse

# Path to external memes JSON file (fallback to inline if missing)
SCRIPT_DIR = os.path.dirname(__file__)
EXTERNAL_MEMES_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'documents', 'memes.json'))

# Load environment variables from .env file
load_dotenv()

# MongoDB connection details
# Get credentials and host separately, construct URI in code
MONGO_HOST = os.getenv("MONGO_HOST", "ai-mongo") # Default to service name
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "ethics_db")
COLLECTION_NAME = "ethical_memes"
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# Construct the URI safely
if MONGO_USERNAME and MONGO_PASSWORD:
    escaped_username = quote_plus(MONGO_USERNAME)
    escaped_password = quote_plus(MONGO_PASSWORD)
    # Assume authSource=admin if using root creds, adjust if needed
    MONGO_URI_RAW = f"mongodb://{escaped_username}:{escaped_password}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=admin"
else:
    # Fallback for unauthenticated local dev (use with caution)
    print("Warning: MONGO_USERNAME or MONGO_PASSWORD not set. Attempting unauthenticated connection.", file=sys.stderr)
    MONGO_URI_RAW = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}"

def escape_mongo_uri(uri):
    """No longer needed as URI is constructed with escaped components."""
    return uri

MONGO_URI = MONGO_URI_RAW # Use the constructed URI directly

print(f"Using MongoDB connection: {MONGO_URI} (DB: {DB_NAME})")

# --- Paste the generated JSON data here ---
# Ensure each JSON object is a valid Python dictionary within the list
# Replace ISODate strings with datetime objects
MEMES_DATA_TEXT = """
[
  {
    "name": "Duty of Honesty",
    "description": "The obligation to communicate truthfully, derived from the moral law's requirement to act on maxims that can be universalized without contradiction (lying cannot be universalized).",
    "ethical_dimension": ["Deontology", "Memetics"],
    "source_concept": "Duty",
    "keywords": ["deontology", "kant", "duty", "honesty", "truthfulness", "moral law", "maxim"],
    "variations": ["Do not lie", "Tell the truth", "Be truthful"],
    "examples": ["Returning lost property to its owner even if inconvenient.", "Refusing to spread false gossip.", "Providing accurate information when asked directly."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": false
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Religious Texts", "Law", "Parenting", "Text"],
        "relevant_selection_pressures": ["Social Cohesion", "Utility", "Social Conformity", "Clarity of definition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Respect for Persons",
    "description": "The duty to treat all rational beings as ends in themselves, never merely as means to an end, based on the inherent dignity and autonomy of rational nature.",
    "ethical_dimension": ["Deontology", "Memetics"],
    "source_concept": "Moral Law",
    "keywords": ["deontology", "kant", "respect", "dignity", "autonomy", "rational agents", "ends in themselves"],
    "variations": ["Treat others with respect", "Don't use people", "Recognize inherent worth"],
    "examples": ["Not manipulating someone to achieve a personal goal.", "Seeking informed consent before involving someone in an action.", "Acknowledging the rights and perspectives of others."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": true
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Philosophy Texts", "Text", "Education"],
        "relevant_selection_pressures": ["Social Cohesion", "Value of Experience", "Philosophical Tradition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Duty to Keep Promises",
    "description": "The obligation to fulfill commitments freely made, as the maxim of breaking promises when convenient cannot be universalized without contradiction.",
    "ethical_dimension": ["Deontology", "Memetics"],
    "source_concept": "Duty",
    "keywords": ["deontology", "kant", "duty", "promise", "commitment", "fidelity", "moral law"],
    "variations": ["Keep your word", "Honor your commitments", "A promise made is a debt unpaid"],
    "examples": ["Fulfilling a contractual agreement.", "Showing up for a meeting as agreed.", "Keeping a secret confided in trust."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": false
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Text", "Law", "Education", "Mentorship"],
        "relevant_selection_pressures": ["Utility", "Clarity of definition", "Social Cohesion", "Need for Nuance"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Act from Good Will",
    "description": "The principle that an action only has true moral worth if performed out of duty and respect for the moral law itself, not from inclination, desire, or expected consequences. It requires a pure moral intention.",
    "ethical_dimension": ["Deontology", "Memetics"],
    "source_concept": "Good Will",
    "keywords": ["deontology", "kant", "good will", "duty", "moral worth", "intention", "motivation"],
    "variations": ["Do the right thing for the right reason", "Intention matters", "Act out of principle"],
    "examples": ["Helping someone solely because it is the right thing to do, not for praise or reward.", "Telling the truth even when it is difficult, out of respect for honesty.", "Resisting a temptation because it violates a moral rule."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": true
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Philosophy Texts", "Religious Texts", "Education"],
        "relevant_selection_pressures": ["Philosophical Tradition", "Complexity", "Value of Experience"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Categorical Imperative",
    "description": "Kant's supreme moral principle: Act only according to that maxim whereby you can, at the same time, will that it should become a universal law. It serves as the test for determining moral duties.",
    "ethical_dimension": ["Deontology", "Memetics"],
    "source_concept": "Moral Law",
    "keywords": ["deontology", "kant", "categorical imperative", "moral law", "universalizability", "maxim", "duty"],
    "variations": ["Universalizability Principle", "Formula of Universal Law", "What if everyone did that?"],
    "examples": ["Testing the maxim 'I will lie when it benefits me' - fails because universal lying undermines trust and communication.", "Testing the maxim 'I will help others in need' - passes as it can be willed universally."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": true
      },
      "memetics": {
        "estimated_transmissibility": "Low",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Philosophy Texts", "Education", "Academic Papers"],
        "relevant_selection_pressures": ["Logical Rigor", "Philosophical Tradition", "Clarity of definition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Maximize Happiness",
    "description": "The core principle of utilitarianism, advocating actions that produce the greatest amount of happiness or pleasure for the largest number of individuals affected.",
    "ethical_dimension": ["Teleology", "Memetics"],
    "source_concept": "Principle of Utility",
    "keywords": ["teleology", "utilitarianism", "consequences", "utility", "happiness", "pleasure", "greatest good"],
    "variations": ["Greatest good for the greatest number", "Promote overall well-being", "Maximize positive outcomes"],
    "examples": ["Implementing a public health policy expected to save many lives, despite minor inconveniences.", "Choosing a career path that allows one to contribute significantly to societal welfare.", "Donating resources to effective charities."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Happiness",
        "scope": "Universal",
        "time_horizon": "Long-term"
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Philosophy Texts", "Education", "Law", "Oral"],
        "relevant_selection_pressures": ["Intuitive Appeal (promoting happiness)", "Logical Rigor", "Utility"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Minimize Suffering",
    "description": "A formulation of utilitarianism (Negative Utilitarianism) prioritizing the reduction or elimination of pain, suffering, and disutility for all affected beings.",
    "ethical_dimension": ["Teleology", "Memetics"],
    "source_concept": "Net Benefit",
    "keywords": ["teleology", "utilitarianism", "consequences", "suffering", "pain", "harm reduction", "negative utilitarianism"],
    "variations": ["Reduce overall harm", "Prevent pain", "Alleviate suffering"],
    "examples": ["Focusing aid efforts on alleviating extreme poverty and disease.", "Developing safer technologies to prevent accidents.", "Advocating for animal welfare to reduce non-human suffering."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Well-being",
        "scope": "Universal",
        "time_horizon": "Long-term"
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Philosophy Texts", "Text", "Education", "Mentorship"],
        "relevant_selection_pressures": ["Value of Experience", "Need for Nuance", "Complexity"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Calculate Utility",
    "description": "The process central to teleological ethics involving assessing and comparing the expected net benefits (happiness minus suffering, or other metrics) of different possible actions to determine the morally optimal choice.",
    "ethical_dimension": ["Teleology", "Memetics"],
    "source_concept": "Net Benefit",
    "keywords": ["teleology", "utilitarianism", "consequences", "utility", "calculation", "cost-benefit", "decision making"],
    "variations": ["Weigh the pros and cons", "Assess the outcomes", "Utility calculus"],
    "examples": ["A government agency performing a cost-benefit analysis for a proposed regulation.", "An individual considering the likely positive and negative effects of two job offers.", "A non-profit evaluating different interventions based on expected impact."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Preference",
        "scope": "Group",
        "time_horizon": "Mixed"
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Education", "Mentorship", "Text", "Academic Papers"],
        "relevant_selection_pressures": ["Logical Rigor", "Utility", "Practicality (decision-making)", "Clarity of definition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Consequentialism",
    "description": "The broad class of ethical theories holding that the consequences of one's conduct are the ultimate basis for any judgment about the rightness or wrongness of that conduct. Morality is derived from outcomes.",
    "ethical_dimension": ["Teleology", "Memetics"],
    "source_concept": "Consequence",
    "keywords": ["teleology", "consequentialism", "outcomes", "results", "ends", "utilitarianism"],
    "variations": ["Focus on outcomes", "Results matter most", "Judge actions by their effects"],
    "examples": ["Utilitarianism (judging by overall happiness).", "Ethical Egoism (judging by self-interest outcomes).", "Rule Consequentialism (judging rules by the consequences of following them)."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Other",
        "scope": "Universal",
        "time_horizon": "Long-term"
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Philosophy Texts", "Education"],
        "relevant_selection_pressures": ["Practicality (decision-making)", "Clarity of definition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "The Ends Justify the Means",
    "description": "A controversial memetic variant often associated with teleology, suggesting that a desired outcome (end) can legitimize any action (means) taken to achieve it, regardless of the action's intrinsic morality.",
    "ethical_dimension": ["Teleology", "Memetics"],
    "source_concept": "Consequence",
    "keywords": ["teleology", "consequentialism", "ends", "means", "outcome", "justification", "controversial"],
    "variations": ["Results are all that matter", "By any means necessary"],
    "examples": ["Lying on a resume to get a job that allows one to do significant good.", "Using violence to overthrow a tyrannical regime, believing the outcome of freedom justifies it.", "(Often used critically) Justifying unethical business practices by pointing to profits."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Other",
        "scope": "Individual",
        "time_horizon": "Short-term"
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "Medium",
        "estimated_adaptability": "High",
        "fidelity_level": "Low",
        "common_transmission_pathways": ["Oral", "Folklore", "Social Media"],
        "relevant_selection_pressures": ["Utility", "Practicality (decision-making)", "Group Benefit"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Courage",
    "description": "The virtue of facing difficulty, danger, pain, or uncertainty with firmness and without fear. In Aristotelian terms, it is the mean between cowardice (deficiency) and rashness (excess).",
    "ethical_dimension": ["Areteology", "Memetics"],
    "source_concept": "Virtue",
    "keywords": ["areteology", "aristotle", "character", "virtue", "courage", "bravery", "mean"],
    "variations": ["Be brave", "Stand up for what's right", "Face your fears"],
    "examples": ["A soldier facing battle.", "A whistleblower exposing corruption despite personal risk.", "Someone admitting a mistake even when it's embarrassing."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["Perseverance", "Integrity", "Confidence"],
        "related_vices": ["Cowardice", "Rashness"],
        "role_of_phronesis": "High",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Oral", "Folklore", "Mentorship", "Text"],
        "relevant_selection_pressures": ["Social Cohesion", "Group Benefit", "Value of Experience"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Honesty",
    "description": "The virtue of being truthful and sincere in one's communication and actions. It involves representing reality accurately and avoiding deception, aligning one's words and deeds with the truth.",
    "ethical_dimension": ["Areteology", "Memetics"],
    "source_concept": "Virtue",
    "keywords": ["areteology", "aristotle", "character", "virtue", "honesty", "truthfulness", "sincerity", "integrity"],
    "variations": ["Be honest", "Tell the truth", "Integrity"],
    "examples": ["Accurately representing one's qualifications.", "Giving sincere feedback.", "Admitting fault when responsible.", "Conducting business transparently."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["Integrity", "Fairness", "Trustworthiness"],
        "related_vices": ["Dishonesty", "Deceitfulness", "Duplicity"],
        "role_of_phronesis": "Medium",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Parenting", "Education", "Religious Texts", "Text", "Law"],
        "relevant_selection_pressures": ["Utility", "Social Cohesion", "Fairness Intuition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Compassion",
    "description": "The virtue of recognizing and responding with kindness and empathy to the suffering of others. It involves feeling concern for others' well-being and acting to alleviate their pain or hardship.",
    "ethical_dimension": ["Areteology", "Memetics"],
    "source_concept": "Virtue",
    "keywords": ["areteology", "character", "virtue", "compassion", "empathy", "kindness", "benevolence"],
    "variations": ["Be compassionate", "Show kindness", "Empathize with others", "Help those in need"],
    "examples": ["Volunteering time to help the less fortunate.", "Comforting someone who is grieving.", "Donating to disaster relief efforts.", "Listening actively to someone's problems."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["Kindness", "Generosity", "Benevolence", "Empathy"],
        "related_vices": ["Callousness", "Indifference", "Cruelty"],
        "role_of_phronesis": "Medium",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Religious Texts", "Oral", "Parenting", "Mentorship"],
        "relevant_selection_pressures": ["Social Cohesion", "Group Benefit", "Value of Experience"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Habituation - Practice Makes Virtue",
    "description": "The Aristotelian principle that moral virtues are developed through repeated practice and habit, not merely through intellectual understanding. Consistently performing virtuous actions cultivates a virtuous character.",
    "ethical_dimension": ["Areteology", "Memetics"],
    "source_concept": "Habit",
    "keywords": ["areteology", "aristotle", "character", "habit", "practice", "virtue", "habituation"],
    "variations": ["Practice makes perfect (in virtue)", "Cultivate good habits", "Act virtuously consistently"],
    "examples": ["Making a daily effort to exercise patience.", "Consistently choosing honesty in small matters.", "Regularly practicing generosity through small acts.", "Developing a routine of reflection on one's actions."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["All virtues"],
        "related_vices": ["All vices"],
        "role_of_phronesis": "Medium",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Mentorship", "Parenting", "Education", "Philosophy Texts"],
        "relevant_selection_pressures": ["Utility", "Value of Experience", "Practicality (decision-making)"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Eudaimonia - Human Flourishing",
    "description": "The ultimate aim of areteology: achieving a state of 'living well' or human flourishing. This is not mere pleasure, but a deep, objective well-being attained through the active exercise of virtue guided by reason.",
    "ethical_dimension": ["Areteology", "Memetics"],
    "source_concept": "Flourishing",
    "keywords": ["areteology", "aristotle", "character", "eudaimonia", "flourishing", "living well", "happiness", "telos"],
    "variations": ["Live a flourishing life", "Achieve true happiness", "Fulfill your human potential", "Live virtuously"],
    "examples": ["Living a life characterized by courage, wisdom, justice, and temperance.", "Engaging in meaningful activities that exercise one's capacities.", "Building strong relationships based on mutual respect and virtue."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["All virtues"],
        "related_vices": ["All vices"],
        "role_of_phronesis": "High",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "Low",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "Low",
        "common_transmission_pathways": ["Philosophy Texts", "Education", "Mentorship"],
        "relevant_selection_pressures": ["Philosophical Tradition", "Value of Experience", "Complexity"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "The Golden Rule",
    "description": "The principle of treating others as one wants to be treated. It resonates across ethical frameworks due to its emphasis on reciprocity, fairness, and empathy.",
    "ethical_dimension": ["Deontology", "Teleology", "Areteology", "Memetics"],
    "source_concept": "Universal Moral Meme",
    "keywords": ["golden rule", "reciprocity", "fairness", "empathy", "deontology", "teleology", "areteology", "universal"],
    "variations": ["Do unto others as you would have them do unto you", "Treat others the way you want to be treated", "(Negative form) Do not do to others what you would not want done to yourself"],
    "examples": ["Sharing resources because you would want others to share with you if you were in need.", "Avoiding harmful gossip because you wouldn't want others to gossip about you.", "Designing policies that you would find acceptable if you were subject to them."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": true
      },
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Happiness",
        "scope": "Universal",
        "time_horizon": "Long-term"
      },
      "virtue_ethics": {
        "related_virtues": ["Compassion", "Empathy", "Fairness", "Kindness", "Justice"],
        "related_vices": ["Selfishness", "Callousness", "Unfairness"],
        "role_of_phronesis": "Medium",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Religious Texts", "Philosophy Texts", "Folklore", "Parenting", "Text"],
        "relevant_selection_pressures": ["Social Cohesion", "Fairness Intuition", "Cognitive Appeal", "Clarity of definition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Do No Harm (Primum Non Nocere)",
    "description": "A fundamental ethical principle, especially prominent in medicine, obligating one to avoid causing harm. It is a core component of ethical consideration across different frameworks.",
    "ethical_dimension": ["Deontology", "Teleology", "Areteology", "Memetics"],
    "source_concept": "Universal Moral Meme",
    "keywords": ["do no harm", "non-maleficence", "primum non nocere", "harm reduction", "safety", "deontology", "teleology", "areteology"],
    "variations": ["First, do no harm", "Avoid causing suffering", "Prevent harm"],
    "examples": ["A doctor avoiding treatments where the potential harm outweighs the benefit.", "Engineers designing products with safety features.", "Avoiding actions known to cause environmental damage.", "Refraining from spreading malicious rumors."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": true
      },
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Well-being",
        "scope": "Universal",
        "time_horizon": "Mixed"
      },
      "virtue_ethics": {
        "related_virtues": ["Compassion", "Care", "Prudence", "Benevolence"],
        "related_vices": ["Malice", "Negligence", "Recklessness", "Cruelty"],
        "role_of_phronesis": "High",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Education", "Law", "Religious Texts", "Text", "Parenting"],
        "relevant_selection_pressures": ["Utility", "Social Cohesion", "Value of Experience", "Fairness Intuition"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Justice / Fairness",
    "description": "The principle of giving individuals what they are due or deserve, often involving concepts of rights, equality, impartiality, and equity. It is a cornerstone of social and individual ethics.",
    "ethical_dimension": ["Deontology", "Teleology", "Areteology", "Memetics"],
    "source_concept": "Universal Moral Meme",
    "keywords": ["justice", "fairness", "equity", "rights", "desert", "deontology", "teleology", "areteology"],
    "variations": ["Be just", "Fairness for all", "Uphold rights", "Give people what they deserve"],
    "examples": ["Implementing fair legal procedures.", "Distributing resources equitably.", "Correcting historical injustices.", "Treating individuals impartially regardless of background."],
    "related_memes": [],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable",
        "respects_rational_agents": true,
        "focus_on_intent": true
      },
      "teleology": {
        "focus": "Consequences/Outcomes",
        "utility_metric": "Well-being",
        "scope": "Universal",
        "time_horizon": "Long-term"
      },
      "virtue_ethics": {
        "related_virtues": ["Fairness", "Integrity", "Impartiality", "Courage"],
        "related_vices": ["Unfairness", "Bias", "Corruption", "Greed"],
        "role_of_phronesis": "High",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Law", "Philosophy Texts", "Religious Texts", "Education", "Text"],
        "relevant_selection_pressures": ["Social Cohesion", "Fairness Intuition", "Utility", "Group Benefit"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  }
]
"""

def parse_datetime(iso_str):
    """Parses ISO 8601 string (with Z) to datetime object."""
    # Remove 'Z' and parse, assuming UTC
    if iso_str.endswith('Z'):
        iso_str = iso_str[:-1] + '+00:00'
    return datetime.fromisoformat(iso_str)

def deserialize_data(text):
    """Parses the JSON string and converts ISODate strings to datetime objects."""
    try:
        # Attempt to load directly, assuming valid JSON
        # Explicitly remove potential BOM before parsing
        text_cleaned = text.lstrip('\ufeff')
        data = json.loads(text_cleaned)
        for item in data:
            if 'metadata' in item:
                # Check if dates are strings and parse them
                if 'created_at' in item['metadata'] and isinstance(item['metadata']['created_at'], str):
                    item['metadata']['created_at'] = parse_datetime(item['metadata']['created_at'])
                if 'updated_at' in item['metadata'] and isinstance(item['metadata']['updated_at'], str):
                    item['metadata']['updated_at'] = parse_datetime(item['metadata']['updated_at'])
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

def wait_for_mongodb(max_retries=30, retry_interval=2):
    """Wait for MongoDB to become available"""
    print(f"Checking MongoDB connection at {MONGO_URI}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            # Create a client with a shorter timeout
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            client.admin.command('ping')
            print(f"MongoDB connection successful on attempt {attempt}")
            client.close()
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"MongoDB connection attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Max retries reached. MongoDB connection failed.")
                return False

def populate_db():
    """Connects to MongoDB and inserts the meme data."""
    
    # Wait for MongoDB to be available
    if not wait_for_mongodb():
        print("Exiting: Could not connect to MongoDB")
        return
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Load memes data from external file if it exists, otherwise use inline text
        if os.path.isfile(EXTERNAL_MEMES_PATH):
            print(f"Loading memes from external file: {EXTERNAL_MEMES_PATH}")
            # Add encoding='utf-8-sig' to handle potential BOM
            with open(EXTERNAL_MEMES_PATH, 'r', encoding='utf-8-sig') as f:
                memes_data = deserialize_data(f.read())
        else:
            print("External memes file not found. Using inline data.")
            memes_data = deserialize_data(MEMES_DATA_TEXT)

        if not memes_data:
            print("No valid meme data to insert.")
            return

        # Optional: Clear existing data before inserting (use with caution)
        # print(f"Deleting existing documents from {DB_NAME}.{COLLECTION_NAME}...")
        # delete_result = collection.delete_many({})
        # print(f"Deleted {delete_result.deleted_count} documents.")

        print(f"Upserting {len(memes_data)} memes into {DB_NAME}.{COLLECTION_NAME} (idempotent)...")

        # Build bulk upsert operations to avoid duplicate-key errors on restart
        bulk_ops = []
        for meme in memes_data:
            bulk_ops.append(
                UpdateOne(
                    {"name": meme.get("name")},  # unique key
                    {"$setOnInsert": meme},
                    upsert=True
                )
            )

        if bulk_ops:
            result = collection.bulk_write(bulk_ops, ordered=False)
            inserted = len(result.upserted_ids) if result.upserted_ids else 0
            print(f"Bulk upsert complete – {inserted} new memes inserted, existing records left untouched.")
        else:
            print("No bulk operations generated – nothing to insert.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    print("Starting MongoDB population script...")
    populate_db()
    print("Script finished.") 