import os
import json
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId, json_util

# Load environment variables from .env file
load_dotenv()

# MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI", "mongodb://ai-mongo:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "ethics_db")
COLLECTION_NAME = "ethical_memes"

# --- Paste the generated JSON data here ---
# Ensure each JSON object is a valid Python dictionary within the list
# Replace ISODate strings with datetime objects
MEMES_DATA_TEXT = """
[
  {
    "name": "Duty of Honesty",
    "description": "The obligation to communicate truthfully, derived from the moral law's requirement to act on maxims that can be universalized without contradiction (lying cannot be universalized).",
    "ethical_dimension": ["Deontology"],
    "source_concept": "Duty",
    "keywords": ["deontology", "kant", "duty", "honesty", "truthfulness", "moral law", "maxim"],
    "variations": ["Do not lie", "Tell the truth", "Be truthful"],
    "examples": ["Returning lost property to its owner even if inconvenient.", "Refusing to spread false gossip.", "Providing accurate information when asked directly."],
    "related_memes": ["Categorical Imperative", "Moral Law", "Good Will"],
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
        "common_transmission_pathways": ["Religious Texts", "Law", "Parenting", "Social Norms"],
        "relevant_selection_pressures": ["Social Order", "Trust", "Cooperation", "Legal Systems"]
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
    "ethical_dimension": ["Deontology"],
    "source_concept": "Moral Law",
    "keywords": ["deontology", "kant", "respect", "dignity", "autonomy", "rational agents", "ends in themselves"],
    "variations": ["Treat others with respect", "Don't use people", "Recognize inherent worth"],
    "examples": ["Not manipulating someone to achieve a personal goal.", "Seeking informed consent before involving someone in an action.", "Acknowledging the rights and perspectives of others."],
    "related_memes": ["Categorical Imperative", "Duty", "Good Will"],
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
        "common_transmission_pathways": ["Philosophy", "Human Rights Discourse", "Ethical Codes"],
        "relevant_selection_pressures": ["Social Harmony", "Individual Rights", "Moral Progress"]
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
    "ethical_dimension": ["Deontology"],
    "source_concept": "Duty",
    "keywords": ["deontology", "kant", "duty", "promise", "commitment", "fidelity", "moral law"],
    "variations": ["Keep your word", "Honor your commitments", "A promise made is a debt unpaid"],
    "examples": ["Fulfilling a contractual agreement.", "Showing up for a meeting as agreed.", "Keeping a secret confided in trust."],
    "related_memes": ["Duty of Honesty", "Categorical Imperative", "Moral Law"],
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
        "common_transmission_pathways": ["Social Norms", "Law", "Business Ethics", "Personal Relationships"],
        "relevant_selection_pressures": ["Trust", "Reliability", "Social Cooperation", "Reputation"]
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
    "ethical_dimension": ["Deontology"],
    "source_concept": "Good Will",
    "keywords": ["deontology", "kant", "good will", "duty", "moral worth", "intention", "motivation"],
    "variations": ["Do the right thing for the right reason", "Intention matters", "Act out of principle"],
    "examples": ["Helping someone solely because it is the right thing to do, not for praise or reward.", "Telling the truth even when it is difficult, out of respect for honesty.", "Resisting a temptation because it violates a moral rule."],
    "related_memes": ["Duty", "Moral Law", "Categorical Imperative", "Respect for Persons"],
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
        "common_transmission_pathways": ["Philosophy", "Religious Ethics", "Moral Education"],
        "relevant_selection_pressures": ["Moral Integrity", "Character Development", "Philosophical Discourse"]
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
    "ethical_dimension": ["Deontology"],
    "source_concept": "Moral Law",
    "keywords": ["deontology", "kant", "categorical imperative", "moral law", "universalizability", "maxim", "duty"],
    "variations": ["Universalizability Principle", "Formula of Universal Law", "What if everyone did that?"],
    "examples": ["Testing the maxim 'I will lie when it benefits me' - fails because universal lying undermines trust and communication.", "Testing the maxim 'I will help others in need' - passes as it can be willed universally."],
    "related_memes": ["Moral Law", "Duty", "Respect for Persons", "Act from Good Will"],
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
        "common_transmission_pathways": ["Philosophy Texts", "Ethics Courses", "Academic Discourse"],
        "relevant_selection_pressures": ["Philosophical Rigor", "Moral Theory Development", "Rational Consistency"]
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
    "ethical_dimension": ["Teleology"],
    "source_concept": "Principle of Utility",
    "keywords": ["teleology", "utilitarianism", "consequences", "utility", "happiness", "pleasure", "greatest good"],
    "variations": ["Greatest good for the greatest number", "Promote overall well-being", "Maximize positive outcomes"],
    "examples": ["Implementing a public health policy expected to save many lives, despite minor inconveniences.", "Choosing a career path that allows one to contribute significantly to societal welfare.", "Donating resources to effective charities."],
    "related_memes": ["Minimize Suffering", "Calculate Utility", "Consequentialism"],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Outcomes",
        "utility_metric": "Happiness/Pleasure",
        "scope": "All Affected Beings",
        "time_horizon": "Long-term (ideal) / Contextual"
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Philosophy", "Economics", "Public Policy", "Popular Sayings"],
        "relevant_selection_pressures": ["Intuitive Appeal", "Rational Calculation", "Social Welfare Focus"]
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
    "ethical_dimension": ["Teleology"],
    "source_concept": "Net Benefit",
    "keywords": ["teleology", "utilitarianism", "consequences", "suffering", "pain", "harm reduction", "negative utilitarianism"],
    "variations": ["Reduce overall harm", "Prevent pain", "Alleviate suffering"],
    "examples": ["Focusing aid efforts on alleviating extreme poverty and disease.", "Developing safer technologies to prevent accidents.", "Advocating for animal welfare to reduce non-human suffering."],
    "related_memes": ["Maximize Happiness", "Calculate Utility", "Consequentialism", "Do No Harm"],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Outcomes",
        "utility_metric": "Absence of Suffering/Pain",
        "scope": "All Affected Beings",
        "time_horizon": "Long-term (ideal) / Contextual"
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Philosophy", "Animal Rights Movements", "Effective Altruism", "Humanitarianism"],
        "relevant_selection_pressures": ["Empathy", "Compassion", "Focus on Extreme Negative States"]
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
    "ethical_dimension": ["Teleology"],
    "source_concept": "Net Benefit",
    "keywords": ["teleology", "utilitarianism", "consequences", "utility", "calculation", "cost-benefit", "decision making"],
    "variations": ["Weigh the pros and cons", "Assess the outcomes", "Utility calculus"],
    "examples": ["A government agency performing a cost-benefit analysis for a proposed regulation.", "An individual considering the likely positive and negative effects of two job offers.", "A non-profit evaluating different interventions based on expected impact."],
    "related_memes": ["Maximize Happiness", "Minimize Suffering", "Consequentialism"],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Outcomes",
        "utility_metric": "Context-dependent (Happiness, Welfare, Preference Satisfaction, etc.)",
        "scope": "Context-dependent (Individual, Group, Societal)",
        "time_horizon": "Context-dependent (Short-term, Long-term)"
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Economics", "Policy Analysis", "Decision Theory", "Management Science"],
        "relevant_selection_pressures": ["Rationality", "Efficiency", "Data-Driven Decisions", "Problem Solving"]
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
    "ethical_dimension": ["Teleology"],
    "source_concept": "Consequence",
    "keywords": ["teleology", "consequentialism", "outcomes", "results", "ends", "utilitarianism"],
    "variations": ["Focus on outcomes", "Results matter most", "Judge actions by their effects"],
    "examples": ["Utilitarianism (judging by overall happiness).", "Ethical Egoism (judging by self-interest outcomes).", "Rule Consequentialism (judging rules by the consequences of following them)."],
    "related_memes": ["Maximize Happiness", "Minimize Suffering", "Calculate Utility", "The Ends Justify the Means"],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Outcomes",
        "utility_metric": "Various (depends on specific theory)",
        "scope": "Various (depends on specific theory)",
        "time_horizon": "Various (depends on specific theory)"
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Philosophy", "Ethics Education"],
        "relevant_selection_pressures": ["Focus on Practical Results", "Alignment with Cause-Effect Reasoning"]
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
    "ethical_dimension": ["Teleology"],
    "source_concept": "Consequence",
    "keywords": ["teleology", "consequentialism", "ends", "means", "outcome", "justification", "controversial"],
    "variations": ["Results are all that matter", "By any means necessary"],
    "examples": ["Lying on a resume to get a job that allows one to do significant good.", "Using violence to overthrow a tyrannical regime, believing the outcome of freedom justifies it.", "(Often used critically) Justifying unethical business practices by pointing to profits."],
    "related_memes": ["Consequentialism", "Maximize Happiness"],
    "dimension_specific_attributes": {
      "teleology": {
        "focus": "Outcomes",
        "utility_metric": "Achieving the desired end",
        "scope": "Often Agent-centric or Goal-centric",
        "time_horizon": "Short-term / Goal achievement"
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "Medium",
        "estimated_adaptability": "High",
        "fidelity_level": "Low",
        "common_transmission_pathways": ["Popular Sayings", "Political Rhetoric", "Colloquial Usage"],
        "relevant_selection_pressures": ["Simplicity", "Justification for Expediency", "Goal-Oriented Thinking"]
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
    "ethical_dimension": ["Virtue Ethics"],
    "source_concept": "Virtue",
    "keywords": ["virtue ethics", "aristotle", "character", "virtue", "courage", "bravery", "mean"],
    "variations": ["Be brave", "Stand up for what's right", "Face your fears"],
    "examples": ["A soldier facing battle.", "A whistleblower exposing corruption despite personal risk.", "Someone admitting a mistake even when it's embarrassing."],
    "related_memes": ["Honesty", "Justice", "Phronesis", "Act Virtuously"],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["Perseverance", "Integrity", "Confidence"],
        "related_vices": ["Cowardice", "Rashness"],
        "role_of_phronesis": "Essential (to determine the right time, way, and object of courageous action)",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Stories", "Myths", "History", "Role Models", "Military Training"],
        "relevant_selection_pressures": ["Social Admiration", "Survival Needs", "Hero Archetypes", "Overcoming Challenges"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Honesty (Virtue)",
    "description": "The virtue of being truthful, sincere, and fair in one's actions and communications. It involves a disposition towards truth and transparency.",
    "ethical_dimension": ["Virtue Ethics"],
    "source_concept": "Virtue",
    "keywords": ["virtue ethics", "aristotle", "character", "virtue", "honesty", "truthfulness", "sincerity", "integrity"],
    "variations": ["Be honest", "Tell the truth", "Integrity"],
    "examples": ["Accurately representing one's qualifications.", "Giving sincere feedback.", "Admitting fault when responsible.", "Conducting business transparently."],
    "related_memes": ["Courage", "Justice", "Phronesis", "Duty of Honesty"],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["Integrity", "Fairness", "Trustworthiness"],
        "related_vices": ["Dishonesty", "Deceitfulness", "Duplicity"],
        "role_of_phronesis": "Important (to know how and when to communicate truth appropriately)",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Parenting", "Education", "Religious Teachings", "Social Norms", "Professional Codes"],
        "relevant_selection_pressures": ["Trust", "Social Cohesion", "Reputation", "Fairness"]
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
    "description": "The virtue involving sensitivity to the suffering of others coupled with a desire to alleviate it. It combines empathy with benevolent action.",
    "ethical_dimension": ["Virtue Ethics"],
    "source_concept": "Virtue",
    "keywords": ["virtue ethics", "character", "virtue", "compassion", "empathy", "kindness", "benevolence"],
    "variations": ["Be compassionate", "Show kindness", "Empathize with others", "Help those in need"],
    "examples": ["Volunteering time to help the less fortunate.", "Comforting someone who is grieving.", "Donating to disaster relief efforts.", "Listening actively to someone's problems."],
    "related_memes": ["Kindness", "Justice", "Good Will", "Minimize Suffering"],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["Kindness", "Generosity", "Benevolence", "Empathy"],
        "related_vices": ["Callousness", "Indifference", "Cruelty"],
        "role_of_phronesis": "Important (to guide compassionate action effectively and appropriately)",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Religious Teachings", "Stories", "Role Models", "Parenting", "Humanitarian Appeals"],
        "relevant_selection_pressures": ["Social Bonding", "Cooperation", "Empathy", "Alleviation of Suffering"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Develop Good Habits",
    "description": "The principle that virtues are cultivated through consistent practice (habituation). Ethical character is built by repeatedly performing virtuous actions until they become second nature.",
    "ethical_dimension": ["Virtue Ethics"],
    "source_concept": "Habit",
    "keywords": ["virtue ethics", "aristotle", "character", "habit", "practice", "virtue", "habituation"],
    "variations": ["Practice makes perfect (in virtue)", "Cultivate good habits", "Act virtuously consistently"],
    "examples": ["Making a daily effort to exercise patience.", "Consistently choosing honesty in small matters.", "Regularly practicing generosity through small acts.", "Developing a routine of reflection on one's actions."],
    "related_memes": ["Act Virtuously", "Phronesis", "Virtue", "Seek Eudaimonia"],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["All virtues are developed through habit"],
        "related_vices": ["Bad habits lead to vices"],
        "role_of_phronesis": "Important (to choose the right actions to practice)",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "Medium",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "Medium",
        "common_transmission_pathways": ["Self-Help Literature", "Parenting Advice", "Educational Psychology", "Philosophy"],
        "relevant_selection_pressures": ["Personal Growth", "Character Development", "Effectiveness", "Goal Achievement"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Seek Eudaimonia",
    "description": "The ultimate aim of virtue ethics: achieving a state of 'living well' or human flourishing. This is not mere pleasure, but a deep, objective well-being attained through the active exercise of virtue guided by reason.",
    "ethical_dimension": ["Virtue Ethics"],
    "source_concept": "Flourishing (Eudaimonia)",
    "keywords": ["virtue ethics", "aristotle", "character", "eudaimonia", "flourishing", "living well", "happiness", "telos"],
    "variations": ["Live a flourishing life", "Achieve true happiness", "Fulfill your human potential", "Live virtuously"],
    "examples": ["Living a life characterized by courage, wisdom, justice, and temperance.", "Engaging in meaningful activities that exercise one's capacities.", "Building strong relationships based on mutual respect and virtue."],
    "related_memes": ["Virtue", "Phronesis", "Develop Good Habits", "Act Virtuously"],
    "dimension_specific_attributes": {
      "virtue_ethics": {
        "related_virtues": ["All virtues contribute"],
        "related_vices": ["Vices impede eudaimonia"],
        "role_of_phronesis": "Essential (for navigating life virtuously)",
        "contributes_to_eudaimonia": true // It *is* eudaimonia
      },
      "memetics": {
        "estimated_transmissibility": "Low",
        "estimated_persistence": "High",
        "estimated_adaptability": "Medium",
        "fidelity_level": "Low",
        "common_transmission_pathways": ["Philosophy Texts", "Classical Education", "Existential Psychology"],
        "relevant_selection_pressures": ["Desire for Meaning", "Philosophical Inquiry", "Search for Purpose"]
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
    "ethical_dimension": ["Deontology", "Teleology", "Virtue Ethics"],
    "source_concept": "Universal Moral Meme",
    "keywords": ["golden rule", "reciprocity", "fairness", "empathy", "deontology", "teleology", "virtue ethics", "universal"],
    "variations": ["Do unto others as you would have them do unto you", "Treat others the way you want to be treated", "(Negative form) Do not do to others what you would not want done to yourself"],
    "examples": ["Sharing resources because you would want others to share with you if you were in need.", "Avoiding harmful gossip because you wouldn't want others to gossip about you.", "Designing policies that you would find acceptable if you were subject to them."],
    "related_memes": ["Respect for Persons", "Maximize Happiness", "Compassion", "Justice"],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable (often seen as derivable from or compatible with the CI)",
        "respects_rational_agents": true,
        "focus_on_intent": true
      },
      "teleology": {
        "focus": "Outcomes (promotes mutual benefit, reduces conflict, increases overall happiness)",
        "utility_metric": "Happiness / Reduced Harm / Social Harmony",
        "scope": "Interpersonal / Societal",
        "time_horizon": "Ongoing / Long-term"
      },
      "virtue_ethics": {
        "related_virtues": ["Compassion", "Empathy", "Fairness", "Kindness", "Justice"],
        "related_vices": ["Selfishness", "Callousness", "Unfairness"],
        "role_of_phronesis": "Important (to apply the rule wisely in complex situations)",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Religious Texts", "Philosophy", "Folklore", "Parenting", "Cultural Norms"],
        "relevant_selection_pressures": ["Social Cooperation", "Fairness Intuition", "Empathy", "Conflict Reduction", "Simplicity"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Do No Harm",
    "description": "The principle of avoiding actions that cause harm, injury, or suffering to others. A foundational precept in many ethical systems, particularly prominent in medical ethics (Primum non nocere).",
    "ethical_dimension": ["Deontology", "Teleology", "Virtue Ethics"],
    "source_concept": "Cross-cutting Principle",
    "keywords": ["do no harm", "non-maleficence", "primum non nocere", "harm reduction", "safety", "deontology", "teleology", "virtue ethics"],
    "variations": ["First, do no harm", "Avoid causing suffering", "Prevent harm"],
    "examples": ["A doctor refusing a treatment where risks outweigh benefits.", "Engineers designing products with safety features.", "Avoiding actions known to cause environmental damage.", "Refraining from spreading malicious rumors."],
    "related_memes": ["Minimize Suffering", "Respect for Persons", "Compassion", "Justice"],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true,
        "universalizability_test": "Applicable (a maxim of causing harm is generally not universalizable)",
        "respects_rational_agents": true,
        "focus_on_intent": true // Often involves intent to avoid harm
      },
      "teleology": {
        "focus": "Outcomes (minimizing negative consequences)",
        "utility_metric": "Absence of Harm/Suffering",
        "scope": "All Affected Beings",
        "time_horizon": "Immediate / Long-term"
      },
      "virtue_ethics": {
        "related_virtues": ["Compassion", "Care", "Prudence (Phronesis)", "Benevolence"],
        "related_vices": ["Malice", "Negligence", "Recklessness", "Cruelty"],
        "role_of_phronesis": "Essential (to foresee potential harms and act carefully)",
        "contributes_to_eudaimonia": true
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High",
        "fidelity_level": "High",
        "common_transmission_pathways": ["Medical Ethics", "Professional Codes", "Religious Teachings", "Legal Principles", "Parenting"],
        "relevant_selection_pressures": ["Safety", "Trust", "Well-being", "Risk Aversion", "Empathy"]
      }
    },
    "metadata": {
      "created_at": {"$date": "2024-04-08T16:20:00Z"},
      "updated_at": {"$date": "2024-04-08T16:20:00Z"},
      "version": 1
    }
  },
  {
    "name": "Justice",
    "description": "The principle of fairness, equity, and upholding rights. It involves giving each person their due and rectifying wrongs, interpreted differently but valued across ethical frameworks.",
    "ethical_dimension": ["Deontology", "Teleology", "Virtue Ethics"],
    "source_concept": "Cross-cutting Principle",
    "keywords": ["justice", "fairness", "equity", "rights", "desert", "deontology", "teleology", "virtue ethics"],
    "variations": ["Be just", "Fairness for all", "Uphold rights", "Give people what they deserve"],
    "examples": ["Implementing fair legal procedures.", "Distributing resources equitably.", "Correcting historical injustices.", "Treating individuals impartially regardless of background."],
    "related_memes": ["Respect for Persons", "Maximize Happiness (via fair distribution)", "Honesty (Virtue)", "Courage (to uphold justice)", "The Golden Rule", "Do No Harm"],
    "dimension_specific_attributes": {
      "deontology": {
        "is_rule_based": true, // Often involves rules of fair procedure/distribution
        "universalizability_test": "Applicable (unjust maxims typically fail universalization)",
        "respects_rational_agents": true, // Central to rights-based justice
        "focus_on_intent": true // Acting with just intent
      },
      "teleology": {
        "focus": "Outcomes (a just society often maximizes well-being, reduces conflict)",
        "utility_metric": "Fair Distribution / Social Harmony / Rights Protection",
        "scope": "Societal / Interpersonal",
        "time_horizon": "Long-term"
      },
      "virtue_ethics": {
        "related_virtues": ["Fairness", "Integrity", "Impartiality", "Courage", "Phronesis"],
        "related_vices": ["Unfairness", "Bias", "Corruption", "Greed"],
        "role_of_phronesis": "Essential (to discern what is just in complex situations)",
        "contributes_to_eudaimonia": true // Justice is a key component of a flourishing society and individual character
      },
      "memetics": {
        "estimated_transmissibility": "High",
        "estimated_persistence": "High",
        "estimated_adaptability": "High", // Concept adapts to different domains (social, economic, legal)
        "fidelity_level": "Medium", // Specific interpretations vary widely
        "common_transmission_pathways": ["Legal Systems", "Political Philosophy", "Religious Texts", "Social Movements", "Education"],
        "relevant_selection_pressures": ["Social Stability", "Fairness Intuition", "Rights Movements", "Cooperation", "Conflict Resolution"]
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
        data = json.loads(text)
        for item in data:
            if 'metadata' in item:
                if 'created_at' in item['metadata'] and isinstance(item['metadata']['created_at'], dict) and '$date' in item['metadata']['created_at']:
                    item['metadata']['created_at'] = parse_datetime(item['metadata']['created_at']['$date'])
                if 'updated_at' in item['metadata'] and isinstance(item['metadata']['updated_at'], dict) and '$date' in item['metadata']['updated_at']:
                    item['metadata']['updated_at'] = parse_datetime(item['metadata']['updated_at']['$date'])
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

def populate_db():
    """Connects to MongoDB and inserts the meme data."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Deserialize the JSON data with datetime conversion
        memes_data = deserialize_data(MEMES_DATA_TEXT)

        if not memes_data:
            print("No valid meme data to insert.")
            return

        # Optional: Clear existing data before inserting (use with caution)
        # print(f"Deleting existing documents from {DB_NAME}.{COLLECTION_NAME}...")
        # delete_result = collection.delete_many({})
        # print(f"Deleted {delete_result.deleted_count} documents.")

        print(f"Inserting {len(memes_data)} documents into {DB_NAME}.{COLLECTION_NAME}...")

        # Insert the data
        # Use insert_many for efficiency
        insert_result = collection.insert_many(memes_data)

        print(f"Successfully inserted {len(insert_result.inserted_ids)} documents.")

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