db = db.getSiblingDB('ethical_memes_db');

if (db.ethical_memes.countDocuments() === 0) {
  print('Seeding ethical_memes collection...');

  const memesToInsert = [
    {
      name: "Ethics",
      description: "The branch of philosophy concerned with the principles of right and wrong conduct, the nature of moral judgments, and the criteria for evaluating actions and character",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["philosophy", "conduct", "principles"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Morality",
      description: "A system of principles and judgments based on cultural, religious, and philosophical concepts and beliefs, by which humans determine whether given actions are right or wrong",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["principles", "judgment", "cultural", "religious", "philosophical"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Philosophy",
      description: "A field of study that seeks to understand, analyze, and evaluate moral concepts and theories, encompassing normative ethics, metaethics, and applied ethics",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["study", "analyze", "evaluate", "concepts", "theories"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Ethical Theory",
      description: "A systematic exposition of the principles guiding moral conduct, often categorized into consequentialism, deontology, and virtue ethics",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["systematic", "principles", "conduct", "consequentialism", "deontology", "virtue ethics"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Normativity",
      description: "The characteristic of prescribing norms or standards; in ethics, it refers to the prescriptive aspect of moral statements that guide actions",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["norms", "standards", "prescriptive", "statements", "actions"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Metaethics",
      description: "The subfield of ethics that examines the nature, meaning, and foundations of ethical concepts, such as what \"good\" or \"right\" means",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["subfield", "nature", "meaning", "foundations", "concepts"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Descriptive Ethics",
      description: "The empirical study of people's moral beliefs, practices, and behaviors, often conducted through sociology or anthropology",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["empirical", "study", "beliefs", "practices", "behaviors"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Normative Ethics",
      description: "The study of ethical action, focusing on the criteria of what is morally right and wrong, and developing moral standards that regulate right and wrong conduct",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["study", "action", "criteria", "right", "wrong", "standards"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Applied Ethics",
      description: "The application of moral principles to specific moral issues or fields, such as medical ethics, business ethics, or environmental ethics",
      ethical_dimension: ["Applied"], 
      source_concept: "Foundational Concepts",
      keywords: ["application", "principles", "issues", "fields", "medical", "business", "environmental"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Practical Reason",
      description: "The faculty of the mind engaged in deciding what to do; in ethics, it refers to reasoning directed toward action and the deliberation about means and ends.",
      ethical_dimension: ["Process"], 
      source_concept: "Foundational Concepts",
      keywords: ["faculty", "mind", "deciding", "reasoning", "action", "deliberation"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Realism",
      description: "The metaethical view that there are objective moral facts and values that are independent of human beliefs or feelings.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["objective", "facts", "values", "independent", "beliefs", "feelings"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Anti-Realism",
      description: "The metaethical stance denying the existence of objective moral values, asserting that moral statements do not refer to objective features of the world.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["denying", "objective", "values", "statements", "features"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Subjectivism",
      description: "The doctrine that moral judgments are statements about the feelings, attitudes, or conventions of the individual or society making them.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["judgments", "statements", "feelings", "attitudes", "conventions"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Objectivism",
      description: "The belief that certain moral principles are universally valid, regardless of individual opinions or cultural norms.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["principles", "universally valid", "opinions", "cultural norms"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Relativism",
      description: "The view that moral judgments are true or false only relative to some particular standpoint, such as a cultural or historical context, and that no standpoint is uniquely privileged over all others.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["judgments", "relative", "standpoint", "cultural", "historical", "context"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Absolutism",
      description: "The ethical belief that there are absolute standards against which moral questions can be judged, and that certain actions are right or wrong, regardless of context.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["absolute", "standards", "judged", "actions", "context"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Cognitivism",
      description: "The metaethical view that moral statements express beliefs that can be true or false.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["statements", "express", "beliefs", "true", "false"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Non-Cognitivism",
      description: "The metaethical view that moral statements do not express propositions and cannot be true or false; instead, they express emotions or prescriptions.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["statements", "propositions", "emotions", "prescriptions"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Emotivism",
      description: "A non-cognitivist theory suggesting that moral statements express emotional attitudes rather than factual claims.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["non-cognitivist", "statements", "emotional attitudes", "factual claims"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Prescriptivism",
      description: "A non-cognitivist theory positing that moral statements function as prescriptions or commands, rather than assertions of fact.",
      ethical_dimension: ["Meta"], 
      source_concept: "Foundational Concepts",
      keywords: ["non-cognitivist", "statements", "prescriptions", "commands", "assertions"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 🧠 Metaethical Terms (continued) ---
    {
      name: "Intuitionism",
      description: "The view in metaethics that moral truths are known by a special faculty of intuition, a kind of immediate, non-inferential moral knowledge.",
      ethical_dimension: ["Meta"], 
      source_concept: "Metaethical Terms",
      keywords: ["intuition", "truths", "knowledge", "non-inferential"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Naturalism",
      description: "A theory which holds that moral properties are reducible to natural properties and can be studied through empirical methods.",
      ethical_dimension: ["Meta"], 
      source_concept: "Metaethical Terms",
      keywords: ["properties", "reducible", "natural", "empirical"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Non-Naturalism",
      description: "The belief that moral properties are real but not reducible to any natural or scientific properties; they are sui generis and apprehended through intuition or reason.",
      ethical_dimension: ["Meta"], 
      source_concept: "Metaethical Terms",
      keywords: ["properties", "real", "not reducible", "sui generis", "intuition", "reason"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Error Theory",
      description: "A metaethical position that claims although moral language tries to refer to objective truths, all such claims are systematically false because no moral facts exist.",
      ethical_dimension: ["Meta"], 
      source_concept: "Metaethical Terms",
      keywords: ["language", "objective truths", "systematically false", "no moral facts"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Constructivism",
      description: "The view that moral truths are not discovered but constructed through rational procedures, agreements, or social processes, especially within a framework of reason.",
      ethical_dimension: ["Meta"], 
      source_concept: "Metaethical Terms",
      keywords: ["truths", "constructed", "rational procedures", "agreements", "social processes"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Is-Ought Problem",
      description: "A problem articulated by David Hume, highlighting the difficulty in deriving prescriptive moral conclusions (what ought to be) solely from descriptive premises (what is).",
      ethical_dimension: ["Meta"], 
      source_concept: "Metaethical Terms",
      keywords: ["Hume", "deriving", "prescriptive", "descriptive", "ought", "is"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Open Question Argument",
      description: "A philosophical argument by G.E. Moore suggesting that any attempt to define "good" in natural terms fails because it always remains an open question whether the definition is correct.",
      ethical_dimension: ["Meta"], 
      source_concept: "Metaethical Terms",
      keywords: ["Moore", "define", "good", "natural terms", "fails", "open question"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- ⚖️ Categories of Actions ---
    {
      name: "Right",
      description: "An action that is morally permissible or obligatory; conforms to accepted moral norms or duties.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "permissible", "obligatory", "norms", "duties"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Wrong",
      description: "An action that violates moral norms; impermissible in a moral system.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "violates", "norms", "impermissible"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Permissible",
      description: "An action that is allowed within the bounds of moral norms, though not necessarily obligatory.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "allowed", "bounds", "norms", "not obligatory"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Impermissible",
      description: "An action that is not allowed within moral rules or principles; morally forbidden.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "not allowed", "rules", "principles", "forbidden"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Obligatory",
      description: "An action that one is morally required to perform; failing to do so would be wrong.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "required", "perform", "failing", "wrong"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Supererogatory",
      description: "An action that is morally praiseworthy but not obligatory; it goes beyond duty.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "praiseworthy", "not obligatory", "beyond duty"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Suberogatory",
      description: "An action that is morally disfavored but not strictly forbidden or wrong — a morally "bad" but permissible action.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "disfavored", "not forbidden", "permissible", "bad"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Neutral (Morally)",
      description: "An action that is neither morally right nor wrong; it lacks moral significance altogether.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "neither right nor wrong", "lacks significance"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Prohibited",
      description: "An action that is explicitly forbidden by moral or legal norms; it is a subset of the impermissible.",
      ethical_dimension: ["Normative"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "forbidden", "norms", "impermissible"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Dilemma",
      description: "A situation in which an agent faces conflicting moral obligations, such that fulfilling one would mean violating another.",
      ethical_dimension: ["Situation"], 
      source_concept: "Categories of Actions",
      keywords: ["situation", "agent", "conflicting obligations", "violating"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Conflict",
      description: "A broader term than a dilemma, referring to situations where values, principles, or duties are in tension and cannot all be realized harmoniously.",
      ethical_dimension: ["Situation"], 
      source_concept: "Categories of Actions",
      keywords: ["situation", "values", "principles", "duties", "tension", "harmoniously"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Amoral",
      description: "Describes something or someone not concerned with morality, or lacking the capacity to be judged in moral terms.",
      ethical_dimension: ["Evaluation"], 
      source_concept: "Categories of Actions",
      keywords: ["not concerned", "lacking capacity", "judged"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Immoral",
      description: "Refers to an action or character that intentionally violates moral norms or standards.",
      ethical_dimension: ["Evaluation"], 
      source_concept: "Categories of Actions",
      keywords: ["action", "character", "intentionally violates", "norms", "standards"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- ⚖️ Categories of Actions (continued) ---
    {
      name: "Moral",
      description: "Pertaining to principles of right and wrong behavior; actions or persons aligned with ethical standards or virtues.",
      ethical_dimension: ["Evaluation"], 
      source_concept: "Categories of Actions",
      keywords: ["principles", "right", "wrong", "behavior", "actions", "persons", "standards", "virtues"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Nonmoral",
      description: "Describes areas of life or actions that fall outside the domain of moral evaluation — neither right nor wrong.",
      ethical_dimension: ["Evaluation"], 
      source_concept: "Categories of Actions",
      keywords: ["outside domain", "evaluation", "neither right nor wrong"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Ethically Ambiguous",
      description: "A situation or action whose moral status is unclear or disputed, often due to conflicting norms, insufficient information, or novel ethical contexts.",
      ethical_dimension: ["Situation", "Evaluation"], 
      source_concept: "Categories of Actions",
      keywords: ["situation", "action", "unclear", "disputed", "conflicting norms", "insufficient information", "novel contexts"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 🧍 Moral Agents and Patients ---
    {
      name: "Moral Agent",
      description: "An individual capable of making moral judgments and being held responsible for actions due to the possession of rationality, autonomy, and intent.",
      ethical_dimension: ["Agent"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["individual", "capable", "judgments", "responsible", "actions", "rationality", "autonomy", "intent"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Patient",
      description: "A being worthy of moral consideration, even if it lacks agency; includes humans in diminished states and possibly non-human animals or entities.",
      ethical_dimension: ["Patient"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["being", "worthy", "consideration", "lacks agency", "humans", "animals", "entities"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Standing",
      description: "The status of an entity that entitles it to be considered morally — a prerequisite for being owed duties or rights.",
      ethical_dimension: ["Patient"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["status", "entity", "entitles", "considered morally", "prerequisite", "duties", "rights"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Status",
      description: "The degree or kind of moral consideration an entity is owed based on characteristics such as sentience, rationality, or relational standing.",
      ethical_dimension: ["Patient"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["degree", "kind", "consideration", "owed", "characteristics", "sentience", "rationality", "relational"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Personhood",
      description: "The status of being a person, often involving consciousness, rationality, self-awareness, and moral agency — central to debates in ethics and law.",
      ethical_dimension: ["Agent", "Patient"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["status", "person", "consciousness", "rationality", "self-awareness", "agency", "debates"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Agency",
      description: "The capacity to act intentionally and make choices; in ethics, agency implies the possession of autonomy and responsibility.",
      ethical_dimension: ["Agent"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["capacity", "act intentionally", "make choices", "autonomy", "responsibility"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Intentionality",
      description: "The quality of mental states that are directed at or about something; in ethics, it refers to actions done deliberately or with purpose.",
      ethical_dimension: ["Agent", "Action"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["quality", "mental states", "directed", "actions", "deliberately", "purpose"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Free Will",
      description: "The ability to choose one's actions independently of external compulsion or determinism; a foundational concept in moral responsibility.",
      ethical_dimension: ["Agent"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["ability", "choose", "actions", "independently", "compulsion", "determinism", "responsibility"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Autonomy",
      description: "The capacity to govern oneself according to rational principles; often considered essential to moral agency and human dignity.",
      ethical_dimension: ["Agent"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["capacity", "govern oneself", "rational principles", "essential", "agency", "dignity"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Conscience",
      description: "The internal faculty or sense that distinguishes right from wrong and prompts moral action or self-evaluation.",
      ethical_dimension: ["Agent"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["internal faculty", "sense", "distinguishes", "right", "wrong", "prompts", "action", "self-evaluation"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Development",
      description: "The process through which individuals acquire moral understanding and ethical behavior, often studied through psychological or educational theories (e.g., Kohlberg).",
      ethical_dimension: ["Agent", "Process"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["process", "acquire", "understanding", "behavior", "psychological", "educational", "Kohlberg"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Sensitivity",
      description: "The capacity to recognize and interpret moral features of a situation; a prerequisite to moral judgment and action.",
      ethical_dimension: ["Agent", "Process"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["capacity", "recognize", "interpret", "features", "situation", "prerequisite", "judgment", "action"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Motivation",
      description: "The internal drive or commitment to act according to one's moral beliefs or judgments, despite contrary desires or incentives.",
      ethical_dimension: ["Agent"], 
      source_concept: "Moral Agents and Patients",
      keywords: ["internal drive", "commitment", "act", "beliefs", "judgments", "desires", "incentives"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 🧩 Responsibility and Reasoning ---
    {
      name: "Accountability",
      description: "The condition of being answerable for one's actions, particularly in moral, social, or institutional contexts.",
      ethical_dimension: ["Agent", "Social"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["condition", "answerable", "actions", "moral", "social", "institutional"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Responsibility",
      description: "The ethical obligation to be answerable for one's actions, presupposing free will, awareness, and intention.",
      ethical_dimension: ["Agent"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["obligation", "answerable", "actions", "free will", "awareness", "intention"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Blameworthiness",
      description: "The quality of being justly subject to blame for a moral fault or wrongdoing due to agency and awareness.",
      ethical_dimension: ["Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["quality", "blame", "fault", "wrongdoing", "agency", "awareness"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Praiseworthiness",
      description: "The quality of deserving moral approval or commendation, based on the voluntary and virtuous nature of one's action.",
      ethical_dimension: ["Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["quality", "deserving", "approval", "commendation", "voluntary", "virtuous", "action"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 🧩 Responsibility and Reasoning (continued) ---
    {
      name: "Moral Judgment",
      description: "The evaluative process by which individuals determine whether an action, intention, or character is right or wrong, often involving rational deliberation and moral principles.",
      ethical_dimension: ["Process", "Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["process", "evaluate", "determine", "action", "intention", "character", "right", "wrong", "deliberation", "principles"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Reasoning",
      description: "The cognitive process of thinking through ethical dilemmas, applying principles and values to reach a conclusion about what one ought to do.",
      ethical_dimension: ["Process"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["cognitive process", "thinking", "dilemmas", "applying principles", "values", "conclusion", "ought"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Luck",
      description: "A condition in which an agent is morally judged for actions or outcomes that were significantly influenced by factors beyond their control (Thomas Nagel, Bernard Williams).",
      ethical_dimension: ["Situation", "Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["condition", "judged", "actions", "outcomes", "influenced", "beyond control", "Nagel", "Williams"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Rationality",
      description: "The quality or capacity of being guided by reason or logic; in ethics, often used to describe the consistency and coherence of moral decisions.",
      ethical_dimension: ["Agent", "Process"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["quality", "capacity", "guided", "reason", "logic", "consistency", "coherence", "decisions"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Deliberation",
      description: "The reflective consideration of reasons for and against potential actions, central to moral agency and decision-making.",
      ethical_dimension: ["Process"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["reflective", "consideration", "reasons", "potential actions", "agency", "decision-making"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Double Effect (Doctrine of)",
      description: "A moral principle stating that it is permissible to perform an action that has both good and bad effects if the bad effect is not intended and the good effect outweighs the bad (e.g., Aquinas on self-defense).",
      ethical_dimension: ["Principle", "Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["principle", "permissible", "action", "good effect", "bad effect", "not intended", "outweighs", "Aquinas"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Proportionality",
      description: "The ethical principle that actions, particularly harmful ones, must be proportionate to the ends sought or the good achieved.",
      ethical_dimension: ["Principle", "Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["principle", "actions", "harmful", "proportionate", "ends sought", "good achieved"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Foreseeability",
      description: "The extent to which the outcomes of an action can be predicted; in ethics, relevant to assessing responsibility for unintended consequences.",
      ethical_dimension: ["Process", "Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["extent", "outcomes", "predicted", "assessing responsibility", "unintended consequences"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Negligence",
      description: "The failure to exercise appropriate care, leading to harm; in moral and legal reasoning, a breach of duty due to carelessness or inattention.",
      ethical_dimension: ["Evaluation"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["failure", "exercise care", "harm", "breach of duty", "carelessness", "inattention"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Complicity",
      description: "The condition of being morally or legally implicated in the wrongdoing of another, through action, support, or willful ignorance.",
      ethical_dimension: ["Evaluation", "Social"], 
      source_concept: "Responsibility and Reasoning",
      keywords: ["condition", "implicated", "wrongdoing", "action", "support", "willful ignorance"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 🧪 Values and Norms ---
    {
      name: "Value",
      description: "A standard or principle considered important or desirable, guiding human behavior and judgment across ethical, aesthetic, or practical domains.",
      ethical_dimension: ["Foundation"], 
      source_concept: "Values and Norms",
      keywords: ["standard", "principle", "important", "desirable", "guiding behavior", "judgment"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Intrinsic Value",
      description: "The value something has in itself, for its own sake, independent of external consequences or use.",
      ethical_dimension: ["Foundation"], 
      source_concept: "Values and Norms",
      keywords: ["value", "in itself", "for its own sake", "independent", "consequences", "use"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Instrumental Value",
      description: "The value something has as a means to an end — its usefulness in achieving some other goal.",
      ethical_dimension: ["Foundation"], 
      source_concept: "Values and Norms",
      keywords: ["value", "means to an end", "usefulness", "achieving goal"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Norm",
      description: "A rule or principle that prescribes ethical behavior, widely recognized and often internalized by moral agents.",
      ethical_dimension: ["Normative"], 
      source_concept: "Values and Norms",
      keywords: ["rule", "principle", "prescribes behavior", "recognized", "internalized", "agents"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Social Norm",
      description: "A customary rule of behavior shared by a group or society, not necessarily moral but often socially enforced.",
      ethical_dimension: ["Social"], 
      source_concept: "Values and Norms",
      keywords: ["customary rule", "behavior", "shared", "group", "society", "enforced"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Custom",
      description: "A long-established practice or tradition that shapes expectations and conduct, sometimes overlapping with moral norms.",
      ethical_dimension: ["Social"], 
      source_concept: "Values and Norms",
      keywords: ["practice", "tradition", "shapes expectations", "conduct", "overlapping"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Cultural Relativism",
      description: "The view that moral values and practices are determined by cultural context and cannot be judged by external standards.",
      ethical_dimension: ["Meta", "Social"], 
      source_concept: "Values and Norms",
      keywords: ["view", "values", "practices", "determined", "cultural context", "judged", "external standards"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Universalism",
      description: "The ethical position that certain moral principles apply to all people, regardless of culture, time, or situation.",
      ethical_dimension: ["Meta"], 
      source_concept: "Values and Norms",
      keywords: ["position", "principles", "apply to all", "regardless", "culture", "time", "situation"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Pluralism",
      description: "The acceptance of multiple moral values, systems, or perspectives, often with the view that they can coexist or be balanced.",
      ethical_dimension: ["Meta", "Social"], 
      source_concept: "Values and Norms",
      keywords: ["acceptance", "multiple", "values", "systems", "perspectives", "coexist", "balanced"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Tolerance",
      description: "The willingness to accept or permit beliefs, practices, or persons that one may disapprove of, often seen as a moral virtue in diverse societies.",
      ethical_dimension: ["Virtue", "Social"], 
      source_concept: "Values and Norms",
      keywords: ["willingness", "accept", "permit", "beliefs", "practices", "persons", "disapprove", "virtue", "diverse"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 🧾 Duties and Principles ---
    {
      name: "Ought",
      description: "A modal term indicating moral obligation or normative expectation; expresses what one is morally required, permitted, or advised to do.",
      ethical_dimension: ["Normative"], 
      source_concept: "Duties and Principles",
      keywords: ["modal term", "obligation", "expectation", "required", "permitted", "advised"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Duty",
      description: "A moral requirement to act (or refrain from acting) in a certain way, derived from ethical principles, social roles, or rational obligation.",
      ethical_dimension: ["Normative", "Deontological"], 
      source_concept: "Duties and Principles",
      keywords: ["requirement", "act", "refrain", "derived", "principles", "roles", "obligation"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Obligation",
      description: "A binding moral, legal, or social requirement that compels an individual to act or refrain from acting; broader than "duty" and often contextual.",
      ethical_dimension: ["Normative", "Social"], 
      source_concept: "Duties and Principles",
      keywords: ["binding", "requirement", "compels", "act", "refrain", "contextual"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Responsibility",
      description: "The state or fact of being morally answerable for one's actions or roles, often tied to the capacity to understand consequences and make choices.",
      ethical_dimension: ["Agent", "Evaluation"], 
      source_concept: "Duties and Principles",
      keywords: ["state", "fact", "answerable", "actions", "roles", "capacity", "consequences", "choices"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Rule",
      description: "A specific prescribed guideline or directive for conduct, often deriving from a broader principle or normative system.",
      ethical_dimension: ["Normative"], 
      source_concept: "Duties and Principles",
      keywords: ["guideline", "directive", "conduct", "deriving", "principle", "system"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Principle",
      description: "A fundamental moral truth or proposition serving as the foundation for a system of belief or behavior.",
      ethical_dimension: ["Foundation", "Normative"], 
      source_concept: "Duties and Principles",
      keywords: ["fundamental", "truth", "proposition", "foundation", "system", "belief", "behavior"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Maxim",
      description: "A subjective principle of action — a personal rule or intention — particularly central in Kantian ethics as something to be universalized.",
      ethical_dimension: ["Principle", "Deontological"], 
      source_concept: "Duties and Principles",
      keywords: ["subjective principle", "action", "personal rule", "intention", "Kantian", "universalized"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Deontological Constraint",
      description: "A moral limitation placed on permissible action, even in the pursuit of good ends; often used in deontology to forbid certain acts regardless of consequences.",
      ethical_dimension: ["Deontological", "Normative"], 
      source_concept: "Duties and Principles",
      keywords: ["limitation", "permissible action", "good ends", "forbid", "acts", "consequences"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Universalizability",
      description: "The principle that a moral rule must apply equally to all relevantly similar cases; central to Kant's categorical imperative.",
      ethical_dimension: ["Principle", "Deontological"], 
      source_concept: "Duties and Principles",
      keywords: ["principle", "rule", "apply equally", "similar cases", "Kant", "categorical imperative"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Golden Rule",
      description: "The ethical principle of treating others as one would like to be treated oneself; found in many religious and philosophical traditions.",
      ethical_dimension: ["Principle", "Social"], 
      source_concept: "Duties and Principles",
      keywords: ["principle", "treating others", "treated oneself", "religious", "philosophical"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Categorical Imperative",
      description: "In Kantian ethics, an unconditional moral command that applies universally, regardless of desires or consequences.",
      ethical_dimension: ["Principle", "Deontological"], 
      source_concept: "Duties and Principles",
      keywords: ["Kantian", "unconditional", "command", "applies universally", "desires", "consequences"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Hypothetical Imperative",
      description: "A conditional command that applies only if one has the relevant desire or goal (e.g., \"If you want to be healthy, you ought to exercise\").",
      ethical_dimension: ["Principle"], 
      source_concept: "Duties and Principles",
      keywords: ["conditional", "command", "applies if", "desire", "goal"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Social Contract",
      description: "A theoretical agreement among individuals to form a society and abide by rules and norms for mutual benefit, foundational to political and ethical theory.",
      ethical_dimension: ["Theory", "Social", "Political"], 
      source_concept: "Duties and Principles",
      keywords: ["theoretical agreement", "individuals", "form society", "abide by rules", "mutual benefit"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Contractualism",
      description: "A normative ethical theory (e.g., T.M. Scanlon) asserting that moral principles are those that no one could reasonably reject in a social agreement.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Duties and Principles",
      keywords: ["theory", "Scanlon", "principles", "reasonably reject", "social agreement"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Prima Facie Duty",
      description: "A duty that is morally binding unless overridden by a stronger conflicting duty; introduced by W.D. Ross to account for moral pluralism.",
      ethical_dimension: ["Normative", "Deontological"], 
      source_concept: "Duties and Principles",
      keywords: ["duty", "binding", "unless overridden", "conflicting duty", "Ross", "pluralism"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Moral Law",
      description: "A system of universal moral rules binding on all rational beings, often contrasted with legal or religious law; central to Kantian ethics.",
      ethical_dimension: ["Foundation", "Normative"], 
      source_concept: "Duties and Principles",
      keywords: ["system", "universal rules", "binding", "rational beings", "Kantian"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Good Will",
      description: "In Kantian ethics, the only thing good without qualification; the will to act according to duty for its own sake, grounded in moral law.",
      ethical_dimension: ["Foundation", "Deontological"], 
      source_concept: "Duties and Principles",
      keywords: ["Kantian", "good without qualification", "will", "act", "duty", "moral law"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 💡 Theories and Frameworks ---
    {
      name: "Utilitarianism",
      description: "A moral theory that holds the right action is the one that produces the greatest overall happiness or utility for the greatest number.",
      ethical_dimension: ["Theory", "Consequentialist"], 
      source_concept: "Theories and Frameworks",
      keywords: ["theory", "right action", "greatest happiness", "utility", "greatest number"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Consequentialism",
      description: "An ethical theory asserting that the rightness or wrongness of actions depends solely on their consequences or outcomes.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Theories and Frameworks",
      keywords: ["theory", "rightness", "wrongness", "actions", "depends solely", "consequences", "outcomes"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Deontology",
      description: "An ethical theory that prioritizes duties and rules over outcomes; actions are right or wrong based on their adherence to moral norms.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Theories and Frameworks",
      keywords: ["theory", "prioritizes duties", "rules", "outcomes", "adherence", "norms"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 💡 Theories and Frameworks (continued) ---
    {
      name: "Virtue Ethics",
      description: "An ethical theory emphasizing character and the cultivation of virtues over rules or consequences; often associated with Aristotle.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Theories and Frameworks",
      keywords: ["theory", "character", "cultivation", "virtues", "rules", "consequences", "Aristotle"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Care Ethics",
      description: "A normative ethical theory that prioritizes relationships, empathy, and care as central moral values; often associated with feminist moral philosophy.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Theories and Frameworks",
      keywords: ["theory", "relationships", "empathy", "care", "values", "feminist philosophy"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Natural Law Theory",
      description: "The belief that moral norms are grounded in human nature and can be discovered through reason; historically rooted in Aristotle and Aquinas.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Theories and Frameworks",
      keywords: ["belief", "norms", "grounded", "human nature", "discovered", "reason", "Aristotle", "Aquinas"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Divine Command Theory",
      description: "The view that moral duties are grounded in the commands or will of God; an action is right if God commands it.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Theories and Frameworks",
      keywords: ["view", "duties", "grounded", "commands", "will of God", "action right"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Ethical Egoism",
      description: "A normative theory asserting that individuals ought to act in their own self-interest.",
      ethical_dimension: ["Theory", "Normative"], 
      source_concept: "Theories and Frameworks",
      keywords: ["theory", "individuals", "ought", "act", "self-interest"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Hedonism",
      description: "The view that pleasure is the highest good and the proper aim of human life; can be psychological or ethical.",
      ethical_dimension: ["Theory", "Value"], 
      source_concept: "Theories and Frameworks",
      keywords: ["view", "pleasure", "highest good", "aim", "human life", "psychological", "ethical"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Pragmatism",
      description: "A philosophical tradition emphasizing the practical consequences of beliefs and theories, including ethical ideas.",
      ethical_dimension: ["Theory"], 
      source_concept: "Theories and Frameworks",
      keywords: ["tradition", "practical consequences", "beliefs", "theories", "ethical ideas"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Existential Ethics",
      description: "Ethical views grounded in existentialist philosophy, emphasizing individual choice, freedom, and authenticity in moral decision-making.",
      ethical_dimension: ["Theory"], 
      source_concept: "Theories and Frameworks",
      keywords: ["views", "existentialist", "individual choice", "freedom", "authenticity", "decision-making"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Outcome",
      description: "The end result or consequence of an action; central to consequentialist moral evaluation.",
      ethical_dimension: ["Consequentialist"], 
      source_concept: "Theories and Frameworks",
      keywords: ["end result", "consequence", "action", "central", "evaluation"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Utility",
      description: "A measure of overall happiness or satisfaction used in consequentialist ethics, especially in utilitarianism.",
      ethical_dimension: ["Consequentialist"], 
      source_concept: "Theories and Frameworks",
      keywords: ["measure", "happiness", "satisfaction", "consequentialist", "utilitarianism"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Greatest Happiness Principle",
      description: "The principle that the morally right action is the one that produces the greatest happiness for the greatest number (central to utilitarianism).",
      ethical_dimension: ["Principle", "Consequentialist"], 
      source_concept: "Theories and Frameworks",
      keywords: ["principle", "right action", "greatest happiness", "greatest number", "utilitarianism"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Act Utilitarianism",
      description: "A form of utilitarianism that evaluates individual actions based on the net utility they produce.",
      ethical_dimension: ["Theory", "Consequentialist"], 
      source_concept: "Theories and Frameworks",
      keywords: ["form", "utilitarianism", "evaluates", "individual actions", "net utility"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Rule Utilitarianism",
      description: "A form of utilitarianism that evaluates moral rules based on whether adherence to them generally maximizes utility.",
      ethical_dimension: ["Theory", "Consequentialist"], 
      source_concept: "Theories and Frameworks",
      keywords: ["form", "utilitarianism", "evaluates", "moral rules", "adherence", "maximizes utility"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    // --- 🌱 Virtues and Vices ---
    {
      name: "Virtue",
      description: "A stable and commendable trait of character that disposes an individual to act morally well.",
      ethical_dimension: ["Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["stable", "commendable", "trait", "character", "disposes", "act morally"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Vice",
      description: "A stable and blameworthy trait of character that disposes an individual to act immorally or harmfully.",
      ethical_dimension: ["Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["stable", "blameworthy", "trait", "character", "disposes", "act immorally", "harmfully"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Temperance",
      description: "The virtue of self-restraint in desires and pleasures, especially bodily or appetitive ones.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["virtue", "self-restraint", "desires", "pleasures", "bodily", "appetitive"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Courage",
      description: "The virtue of facing fear, danger, or adversity with resolve and moral strength.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["virtue", "facing fear", "danger", "adversity", "resolve", "moral strength"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Justice (as Virtue)",
      description: "The virtue that disposes individuals to give each person their due and to uphold fairness and equality in social relations.",
      ethical_dimension: ["Virtue", "Social"], 
      source_concept: "Virtues and Vices",
      keywords: ["virtue", "disposes", "give due", "uphold fairness", "equality", "social relations"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Prudence",
      description: "The virtue of practical wisdom — the ability to deliberate rightly about what is good and how to act accordingly.",
      ethical_dimension: ["Virtue", "Process"], 
      source_concept: "Virtues and Vices",
      keywords: ["virtue", "practical wisdom", "ability", "deliberate rightly", "good", "act accordingly"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Fortitude",
      description: "The moral strength to endure pain or adversity with steadfastness and moral resolve.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["moral strength", "endure pain", "adversity", "steadfastness", "moral resolve"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Honesty",
      description: "The virtue of being truthful, transparent, and sincere in speech and conduct.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["virtue", "truthful", "transparent", "sincere", "speech", "conduct"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Integrity",
      description: "The quality of moral wholeness and consistency; living in alignment with one's moral principles across all areas of life.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["quality", "moral wholeness", "consistency", "alignment", "principles", "life"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Compassion",
      description: "A sympathetic awareness of another's suffering with the desire to alleviate it; central in care ethics.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["sympathetic awareness", "suffering", "desire alleviate", "care ethics"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Altruism",
      description: "The ethical concern for the welfare of others, often to the exclusion of self-interest.",
      ethical_dimension: ["Virtue", "Action"], 
      source_concept: "Virtues and Vices",
      keywords: ["concern", "welfare of others", "exclusion", "self-interest"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Gratitude",
      description: "A moral disposition of appreciation and thankfulness, especially for kindness received.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["disposition", "appreciation", "thankfulness", "kindness received"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Humility",
      description: "A virtue characterized by a modest view of one's own importance and openness to others.",
      ethical_dimension: ["Virtue", "Character"], 
      source_concept: "Virtues and Vices",
      keywords: ["virtue", "modest view", "importance", "openness"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Forgiveness",
      description: "The voluntary act of letting go of resentment or claims against someone who has committed a moral wrong.",
      ethical_dimension: ["Virtue", "Action"], 
      source_concept: "Virtues and Vices",
      keywords: ["voluntary act", "letting go", "resentment", "claims", "moral wrong"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Eudaimonia",
      description: "Often translated as "flourishing" or "human fulfillment"; the highest good in Aristotelian ethics, achieved through a life of virtue.",
      ethical_dimension: ["Value", "Virtue Ethics"], 
      source_concept: "Virtues and Vices",
      keywords: ["flourishing", "fulfillment", "highest good", "Aristotelian", "life of virtue"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Phronesis",
      description: "Practical wisdom or moral insight; the intellectual virtue that enables right reasoning about how to live virtuously.",
      ethical_dimension: ["Virtue", "Process"], 
      source_concept: "Virtues and Vices",
      keywords: ["practical wisdom", "moral insight", "intellectual virtue", "right reasoning", "live virtuously"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Aretê",
      description: "Excellence of character or function; in Greek virtue ethics, the full realization of a thing's potential.",
      ethical_dimension: ["Virtue", "Virtue Ethics"], 
      source_concept: "Virtues and Vices",
      keywords: ["excellence", "character", "function", "Greek", "realization", "potential"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Telos",
      description: "The ultimate purpose or end of a thing; in ethics, it refers to the final goal toward which moral life is directed.",
      ethical_dimension: ["Foundation", "Virtue Ethics"], 
      source_concept: "Virtues and Vices",
      keywords: ["purpose", "end", "final goal", "moral life", "directed"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    },
    {
      name: "Habituation",
      description: "The process by which moral character is developed through repeated practice and reinforcement of virtuous behavior (central to Aristotle's ethics).",
      ethical_dimension: ["Process", "Virtue Ethics"], 
      source_concept: "Virtues and Vices",
      keywords: ["process", "character developed", "repeated practice", "reinforcement", "virtuous behavior", "Aristotle"],
      variations: [],
      examples: [],
      related_memes: [],
      dimension_specific_attributes: {},
      morphisms: [],
      cross_category_mappings: [],
      is_merged_token: false,
      merged_from_tokens: [],
      metadata: {
        created_at: new Date(),
        updated_at: new Date(),
        version: 1
      }
    }
    // NOTE: Only terms from the first 650 lines of Meme_Inventory.md are included.
    //       The full file needs to be parsed to include all terms.
  ];

  try {
    // Use ordered: false to attempt inserting all documents, skipping duplicates
    const result = db.ethical_memes.insertMany(memesToInsert, { ordered: false });
    print(`Seeding complete. Successfully inserted ${result.insertedIds.length} ethical memes.`);
  } catch (e) {
    print(`Error during seeding: ${e}`);
    // Check for bulk write errors specifically
    if (e.name === 'BulkWriteError') {
      print(`Number of documents inserted before error (or during unordered insert): ${e.result.nInserted}`);
      print(`Number of write errors (e.g., duplicates): ${e.result.getWriteErrors().length}`);
      e.result.getWriteErrors().forEach(err => {
        print(`  - Error Code: ${err.code}, Message: ${err.errmsg}`);
      });
    } else {
       // Print generic error
       print(e);
    }
  }
} else {
  print('Ethical memes collection already exists, skipping seeding.');
} 