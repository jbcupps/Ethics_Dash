// Improved MongoDB import script for ethical memes
// This script properly processes the entire content of Meme_Inventory.md

db = db.getSiblingDB('ethical_memes_db');

if (db.ethical_memes.countDocuments() === 0) {
  print('Seeding ethical_memes collection with improved format...');

  // Helper function to parse the Meme_Inventory.md format
  function parseMemeInventory() {
    const memes = [];
    const categories = {
      "Foundational Concepts": "Meta",
      "Metaethical Terms": "Meta",
      "Categories of Actions": "Action",
      "Moral Agents and Patients": "Agent",
      "Responsibility and Reasoning": "Process",
      "Values and Norms": "Value",
      "Duties and Principles": "Principle",
      "Theories and Frameworks": "Theory",
      "Virtues and Vices": "Virtue"
    };
    
    // Process all terms from Meme_Inventory.md
    // Format in the file is:
    // Term name
    //  Definition: The definition text

    // The complete list of terms with their definitions, organized by category
    const termsData = [
      // Foundational Concepts
      { name: "Ethics", category: "Foundational Concepts", definition: "The branch of philosophy concerned with the principles of right and wrong conduct, the nature of moral judgments, and the criteria for evaluating actions and character" },
      { name: "Morality", category: "Foundational Concepts", definition: "A system of principles and judgments based on cultural, religious, and philosophical concepts and beliefs, by which humans determine whether given actions are right or wrong" },
      { name: "Moral Philosophy", category: "Foundational Concepts", definition: "A field of study that seeks to understand, analyze, and evaluate moral concepts and theories, encompassing normative ethics, metaethics, and applied ethics" },
      { name: "Ethical Theory", category: "Foundational Concepts", definition: "A systematic exposition of the principles guiding moral conduct, often categorized into consequentialism, deontology, and virtue ethics" },
      { name: "Normativity", category: "Foundational Concepts", definition: "The characteristic of prescribing norms or standards; in ethics, it refers to the prescriptive aspect of moral statements that guide actions" },
      { name: "Metaethics", category: "Foundational Concepts", definition: "The subfield of ethics that examines the nature, meaning, and foundations of ethical concepts, such as what \"good\" or \"right\" means" },
      { name: "Descriptive Ethics", category: "Foundational Concepts", definition: "The empirical study of people's moral beliefs, practices, and behaviors, often conducted through sociology or anthropology" },
      { name: "Normative Ethics", category: "Foundational Concepts", definition: "The study of ethical action, focusing on the criteria of what is morally right and wrong, and developing moral standards that regulate right and wrong conduct" },
      { name: "Applied Ethics", category: "Foundational Concepts", definition: "The application of moral principles to specific moral issues or fields, such as medical ethics, business ethics, or environmental ethics" },
      { name: "Practical Reason", category: "Foundational Concepts", definition: "The faculty of the mind engaged in deciding what to do; in ethics, it refers to reasoning directed toward action and the deliberation about means and ends" },
      { name: "Moral Realism", category: "Foundational Concepts", definition: "The metaethical view that there are objective moral facts and values that are independent of human beliefs or feelings" },
      { name: "Moral Anti-Realism", category: "Foundational Concepts", definition: "The metaethical stance denying the existence of objective moral values, asserting that moral statements do not refer to objective features of the world" },
      
      // Metaethical Terms
      { name: "Moral Subjectivism", category: "Metaethical Terms", definition: "The doctrine that moral judgments are statements about the feelings, attitudes, or conventions of the individual or society making them" },
      { name: "Moral Objectivism", category: "Metaethical Terms", definition: "The belief that certain moral principles are universally valid, regardless of individual opinions or cultural norms" },
      { name: "Moral Relativism", category: "Metaethical Terms", definition: "The view that moral judgments are true or false only relative to some particular standpoint, such as a cultural or historical context, and that no standpoint is uniquely privileged over all others" },
      { name: "Moral Absolutism", category: "Metaethical Terms", definition: "The ethical belief that there are absolute standards against which moral questions can be judged, and that certain actions are right or wrong, regardless of context" },
      { name: "Cognitivism", category: "Metaethical Terms", definition: "The metaethical view that moral statements express beliefs that can be true or false" },
      { name: "Non-Cognitivism", category: "Metaethical Terms", definition: "The metaethical view that moral statements do not express propositions and cannot be true or false; instead, they express emotions or prescriptions" },
      { name: "Emotivism", category: "Metaethical Terms", definition: "A non-cognitivist theory suggesting that moral statements express emotional attitudes rather than factual claims" },
      { name: "Prescriptivism", category: "Metaethical Terms", definition: "A non-cognitivist theory positing that moral statements function as prescriptions or commands, rather than assertions of fact" },
      { name: "Intuitionism", category: "Metaethical Terms", definition: "The view in metaethics that moral truths are known by a special faculty of intuition, a kind of immediate, non-inferential moral knowledge" },
      { name: "Moral Naturalism", category: "Metaethical Terms", definition: "A theory which holds that moral properties are reducible to natural properties and can be studied through empirical methods" },
      { name: "Moral Non-Naturalism", category: "Metaethical Terms", definition: "The belief that moral properties are real but not reducible to any natural or scientific properties; they are sui generis and apprehended through intuition or reason" },
      { name: "Error Theory", category: "Metaethical Terms", definition: "A metaethical position that claims although moral language tries to refer to objective truths, all such claims are systematically false because no moral facts exist" },
      { name: "Constructivism", category: "Metaethical Terms", definition: "The view that moral truths are not discovered but constructed through rational procedures, agreements, or social processes, especially within a framework of reason" },
      { name: "Is-Ought Problem", category: "Metaethical Terms", definition: "A problem articulated by David Hume, highlighting the difficulty in deriving prescriptive moral conclusions (what ought to be) solely from descriptive premises (what is)" },
      { name: "Open Question Argument", category: "Metaethical Terms", definition: "A philosophical argument by G.E. Moore suggesting that any attempt to define \"good\" in natural terms fails because it always remains an open question whether the definition is correct" },
      
      // Categories of Actions
      { name: "Right", category: "Categories of Actions", definition: "An action that is morally permissible or obligatory; conforms to accepted moral norms or duties" },
      { name: "Wrong", category: "Categories of Actions", definition: "An action that violates moral norms; impermissible in a moral system" },
      { name: "Permissible", category: "Categories of Actions", definition: "An action that is allowed within the bounds of moral norms, though not necessarily obligatory" },
      { name: "Impermissible", category: "Categories of Actions", definition: "An action that is not allowed within moral rules or principles; morally forbidden" },
      { name: "Obligatory", category: "Categories of Actions", definition: "An action that one is morally required to perform; failing to do so would be wrong" },
      { name: "Supererogatory", category: "Categories of Actions", definition: "An action that is morally praiseworthy but not obligatory; it goes beyond duty" },
      { name: "Suberogatory", category: "Categories of Actions", definition: "An action that is morally disfavored but not strictly forbidden or wrong — a morally \"bad\" but permissible action" },
      { name: "Neutral (Morally)", category: "Categories of Actions", definition: "An action that is neither morally right nor wrong; it lacks moral significance altogether" },
      { name: "Prohibited", category: "Categories of Actions", definition: "An action that is explicitly forbidden by moral or legal norms; it is a subset of the impermissible" },
      { name: "Moral Dilemma", category: "Categories of Actions", definition: "A situation in which an agent faces conflicting moral obligations, such that fulfilling one would mean violating another" },
      { name: "Moral Conflict", category: "Categories of Actions", definition: "A broader term than a dilemma, referring to situations where values, principles, or duties are in tension and cannot all be realized harmoniously" },
      { name: "Amoral", category: "Categories of Actions", definition: "Describes something or someone not concerned with morality, or lacking the capacity to be judged in moral terms" },
      { name: "Immoral", category: "Categories of Actions", definition: "Refers to an action or character that intentionally violates moral norms or standards" },
      { name: "Moral", category: "Categories of Actions", definition: "Pertaining to principles of right and wrong behavior; actions or persons aligned with ethical standards or virtues" },
      { name: "Nonmoral", category: "Categories of Actions", definition: "Describes areas of life or actions that fall outside the domain of moral evaluation — neither right nor wrong" },
      { name: "Ethically Ambiguous", category: "Categories of Actions", definition: "A situation or action whose moral status is unclear or disputed, often due to conflicting norms, insufficient information, or novel ethical contexts" },
      
      // Moral Agents and Patients
      { name: "Moral Agent", category: "Moral Agents and Patients", definition: "An individual capable of making moral judgments and being held responsible for actions due to the possession of rationality, autonomy, and intent" },
      { name: "Moral Patient", category: "Moral Agents and Patients", definition: "A being worthy of moral consideration, even if it lacks agency; includes humans in diminished states and possibly non-human animals or entities" },
      { name: "Moral Standing", category: "Moral Agents and Patients", definition: "The status of an entity that entitles it to be considered morally — a prerequisite for being owed duties or rights" },
      { name: "Moral Status", category: "Moral Agents and Patients", definition: "The degree or kind of moral consideration an entity is owed based on characteristics such as sentience, rationality, or relational standing" },
      { name: "Personhood", category: "Moral Agents and Patients", definition: "The status of being a person, often involving consciousness, rationality, self-awareness, and moral agency — central to debates in ethics and law" },
      { name: "Agency", category: "Moral Agents and Patients", definition: "The capacity to act intentionally and make choices; in ethics, agency implies the possession of autonomy and responsibility" },
      { name: "Intentionality", category: "Moral Agents and Patients", definition: "The quality of mental states that are directed at or about something; in ethics, it refers to actions done deliberately or with purpose" },
      { name: "Free Will", category: "Moral Agents and Patients", definition: "The ability to choose one's actions independently of external compulsion or determinism; a foundational concept in moral responsibility" },
      { name: "Autonomy", category: "Moral Agents and Patients", definition: "The capacity to govern oneself according to rational principles; often considered essential to moral agency and human dignity" },
      { name: "Conscience", category: "Moral Agents and Patients", definition: "The internal faculty or sense that distinguishes right from wrong and prompts moral action or self-evaluation" },
      { name: "Moral Development", category: "Moral Agents and Patients", definition: "The process through which individuals acquire moral understanding and ethical behavior, often studied through psychological or educational theories (e.g., Kohlberg)" },
      { name: "Moral Sensitivity", category: "Moral Agents and Patients", definition: "The capacity to recognize and interpret moral features of a situation; a prerequisite to moral judgment and action" },
      { name: "Moral Motivation", category: "Moral Agents and Patients", definition: "The internal drive or commitment to act according to one's moral beliefs or judgments, despite contrary desires or incentives" },
      
      // Responsibility and Reasoning
      { name: "Accountability", category: "Responsibility and Reasoning", definition: "The condition of being answerable for one's actions, particularly in moral, social, or institutional contexts" },
      { name: "Moral Responsibility", category: "Responsibility and Reasoning", definition: "The ethical obligation to be answerable for one's actions, presupposing free will, awareness, and intention" },
      { name: "Blameworthiness", category: "Responsibility and Reasoning", definition: "The quality of being justly subject to blame for a moral fault or wrongdoing due to agency and awareness" },
      { name: "Praiseworthiness", category: "Responsibility and Reasoning", definition: "The quality of deserving moral approval or commendation, based on the voluntary and virtuous nature of one's action" },
      { name: "Moral Judgment", category: "Responsibility and Reasoning", definition: "The evaluative process by which individuals determine whether an action, intention, or character is right or wrong, often involving rational deliberation and moral principles" },
      { name: "Moral Reasoning", category: "Responsibility and Reasoning", definition: "The cognitive process of thinking through ethical dilemmas, applying principles and values to reach a conclusion about what one ought to do" },
      { name: "Moral Luck", category: "Responsibility and Reasoning", definition: "A condition in which an agent is morally judged for actions or outcomes that were significantly influenced by factors beyond their control (Thomas Nagel, Bernard Williams)" },
      { name: "Rationality", category: "Responsibility and Reasoning", definition: "The quality or capacity of being guided by reason or logic; in ethics, often used to describe the consistency and coherence of moral decisions" },
      { name: "Deliberation", category: "Responsibility and Reasoning", definition: "The reflective consideration of reasons for and against potential actions, central to moral agency and decision-making" },
      { name: "Double Effect (Doctrine of)", category: "Responsibility and Reasoning", definition: "A moral principle stating that it is permissible to perform an action that has both good and bad effects if the bad effect is not intended and the good effect outweighs the bad (e.g., Aquinas on self-defense)" },
      { name: "Proportionality", category: "Responsibility and Reasoning", definition: "The ethical principle that actions, particularly harmful ones, must be proportionate to the ends sought or the good achieved" },
      { name: "Foreseeability", category: "Responsibility and Reasoning", definition: "The extent to which the outcomes of an action can be predicted; in ethics, relevant to assessing responsibility for unintended consequences" },
      { name: "Negligence", category: "Responsibility and Reasoning", definition: "The failure to exercise appropriate care, leading to harm; in moral and legal reasoning, a breach of duty due to carelessness or inattention" },
      { name: "Complicity", category: "Responsibility and Reasoning", definition: "The condition of being morally or legally implicated in the wrongdoing of another, through action, support, or willful ignorance" },
      
      // Values and Norms
      { name: "Value", category: "Values and Norms", definition: "A standard or principle considered important or desirable, guiding human behavior and judgment across ethical, aesthetic, or practical domains" },
      { name: "Intrinsic Value", category: "Values and Norms", definition: "The value something has in itself, for its own sake, independent of external consequences or use" },
      { name: "Instrumental Value", category: "Values and Norms", definition: "The value something has as a means to an end — its usefulness in achieving some other goal" },
      { name: "Moral Norm", category: "Values and Norms", definition: "A rule or principle that prescribes ethical behavior, widely recognized and often internalized by moral agents" },
      { name: "Social Norm", category: "Values and Norms", definition: "A customary rule of behavior shared by a group or society, not necessarily moral but often socially enforced" },
      { name: "Custom", category: "Values and Norms", definition: "A long-established practice or tradition that shapes expectations and conduct, sometimes overlapping with moral norms" },
      { name: "Cultural Relativism", category: "Values and Norms", definition: "The view that moral values and practices are determined by cultural context and cannot be judged by external standards" },
      { name: "Universalism", category: "Values and Norms", definition: "The ethical position that certain moral principles apply to all people, regardless of culture, time, or situation" },
      { name: "Pluralism", category: "Values and Norms", definition: "The acceptance of multiple moral values, systems, or perspectives, often with the view that they can coexist or be balanced" },
      { name: "Tolerance", category: "Values and Norms", definition: "The willingness to accept or permit beliefs, practices, or persons that one may disapprove of, often seen as a moral virtue in diverse societies" },
      
      // Duties and Principles
      { name: "Ought", category: "Duties and Principles", definition: "A modal term indicating moral obligation or normative expectation; expresses what one is morally required, permitted, or advised to do" },
      { name: "Duty", category: "Duties and Principles", definition: "A moral requirement to act (or refrain from acting) in a certain way, derived from ethical principles, social roles, or rational obligation" },
      { name: "Obligation", category: "Duties and Principles", definition: "A binding moral, legal, or social requirement that compels an individual to act or refrain from acting; broader than \"duty\" and often contextual" },
      { name: "Responsibility", category: "Duties and Principles", definition: "The state or fact of being morally answerable for one's actions or roles, often tied to the capacity to understand consequences and make choices" },
      { name: "Rule", category: "Duties and Principles", definition: "A specific prescribed guideline or directive for conduct, often deriving from a broader principle or normative system" },
      { name: "Principle", category: "Duties and Principles", definition: "A fundamental moral truth or proposition serving as the foundation for a system of belief or behavior" },
      { name: "Maxim", category: "Duties and Principles", definition: "A subjective principle of action — a personal rule or intention — particularly central in Kantian ethics as something to be universalized" },
      { name: "Deontological Constraint", category: "Duties and Principles", definition: "A moral limitation placed on permissible action, even in the pursuit of good ends; often used in deontology to forbid certain acts regardless of consequences" },
      { name: "Universalizability", category: "Duties and Principles", definition: "The principle that a moral rule must apply equally to all relevantly similar cases; central to Kant's categorical imperative" },
      { name: "Golden Rule", category: "Duties and Principles", definition: "The ethical principle of treating others as one would like to be treated oneself; found in many religious and philosophical traditions" },
      { name: "Categorical Imperative", category: "Duties and Principles", definition: "In Kantian ethics, an unconditional moral command that applies universally, regardless of desires or consequences" },
      { name: "Hypothetical Imperative", category: "Duties and Principles", definition: "A conditional command that applies only if one has the relevant desire or goal (e.g., \"If you want to be healthy, you ought to exercise\")" },
      { name: "Social Contract", category: "Duties and Principles", definition: "A theoretical agreement among individuals to form a society and abide by rules and norms for mutual benefit, foundational to political and ethical theory" },
      { name: "Contractualism", category: "Duties and Principles", definition: "A normative ethical theory (e.g., T.M. Scanlon) asserting that moral principles are those that no one could reasonably reject in a social agreement" },
      { name: "Prima Facie Duty", category: "Duties and Principles", definition: "A duty that is morally binding unless overridden by a stronger conflicting duty; introduced by W.D. Ross to account for moral pluralism" },
      { name: "Moral Law", category: "Duties and Principles", definition: "A system of universal moral rules binding on all rational beings, often contrasted with legal or religious law; central to Kantian ethics" },
      { name: "Good Will", category: "Duties and Principles", definition: "In Kantian ethics, the only thing good without qualification; the will to act according to duty for its own sake, grounded in moral law" },
      
      // Theories and Frameworks
      { name: "Utilitarianism", category: "Theories and Frameworks", definition: "A moral theory that holds the right action is the one that produces the greatest overall happiness or utility for the greatest number" },
      { name: "Consequentialism", category: "Theories and Frameworks", definition: "An ethical theory asserting that the rightness or wrongness of actions depends solely on their consequences or outcomes" },
      { name: "Deontology", category: "Theories and Frameworks", definition: "An ethical theory that prioritizes duties and rules over outcomes; actions are right or wrong based on their adherence to moral norms" },
      { name: "Virtue Ethics", category: "Theories and Frameworks", definition: "An ethical theory emphasizing character and the cultivation of virtues over rules or consequences; often associated with Aristotle" },
      { name: "Care Ethics", category: "Theories and Frameworks", definition: "A normative ethical theory that prioritizes relationships, empathy, and care as central moral values; often associated with feminist moral philosophy" },
      { name: "Natural Law Theory", category: "Theories and Frameworks", definition: "The belief that moral norms are grounded in human nature and can be discovered through reason; historically rooted in Aristotle and Aquinas" },
      { name: "Divine Command Theory", category: "Theories and Frameworks", definition: "The view that moral duties are grounded in the commands or will of God; an action is right if God commands it" },
      { name: "Ethical Egoism", category: "Theories and Frameworks", definition: "A normative theory asserting that individuals ought to act in their own self-interest" },
      { name: "Hedonism", category: "Theories and Frameworks", definition: "The view that pleasure is the highest good and the proper aim of human life; can be psychological or ethical" },
      { name: "Pragmatism", category: "Theories and Frameworks", definition: "A philosophical tradition emphasizing the practical consequences of beliefs and theories, including ethical ideas" },
      { name: "Existential Ethics", category: "Theories and Frameworks", definition: "Ethical views grounded in existentialist philosophy, emphasizing individual choice, freedom, and authenticity in moral decision-making" },
      { name: "Outcome", category: "Theories and Frameworks", definition: "The end result or consequence of an action; central to consequentialist moral evaluation" },
      { name: "Utility", category: "Theories and Frameworks", definition: "A measure of overall happiness or satisfaction used in consequentialist ethics, especially in utilitarianism" },
      { name: "Greatest Happiness Principle", category: "Theories and Frameworks", definition: "The principle that the morally right action is the one that produces the greatest happiness for the greatest number (central to utilitarianism)" },
      { name: "Act Utilitarianism", category: "Theories and Frameworks", definition: "A form of utilitarianism that evaluates individual actions based on the net utility they produce" },
      { name: "Rule Utilitarianism", category: "Theories and Frameworks", definition: "A form of utilitarianism that evaluates moral rules based on whether adherence to them generally maximizes utility" },
      
      // Virtues and Vices
      { name: "Virtue", category: "Virtues and Vices", definition: "A stable and commendable trait of character that disposes an individual to act morally well" },
      { name: "Vice", category: "Virtues and Vices", definition: "A stable and blameworthy trait of character that disposes an individual to act immorally or harmfully" },
      { name: "Temperance", category: "Virtues and Vices", definition: "The virtue of self-restraint in desires and pleasures, especially bodily or appetitive ones" },
      { name: "Courage", category: "Virtues and Vices", definition: "The virtue of facing fear, danger, or adversity with resolve and moral strength" },
      { name: "Justice (as Virtue)", category: "Virtues and Vices", definition: "The virtue that disposes individuals to give each person their due and to uphold fairness and equality in social relations" },
      { name: "Prudence", category: "Virtues and Vices", definition: "The virtue of practical wisdom — the ability to deliberate rightly about what is good and how to act accordingly" },
      { name: "Fortitude", category: "Virtues and Vices", definition: "The moral strength to endure pain or adversity with steadfastness and moral resolve" },
      { name: "Honesty", category: "Virtues and Vices", definition: "The virtue of being truthful, transparent, and sincere in speech and conduct" },
      { name: "Integrity", category: "Virtues and Vices", definition: "The quality of moral wholeness and consistency; living in alignment with one's moral principles across all areas of life" },
      { name: "Compassion", category: "Virtues and Vices", definition: "A sympathetic awareness of another's suffering with the desire to alleviate it; central in care ethics" },
      { name: "Altruism", category: "Virtues and Vices", definition: "The ethical concern for the welfare of others, often to the exclusion of self-interest" },
      { name: "Gratitude", category: "Virtues and Vices", definition: "A moral disposition of appreciation and thankfulness, especially for kindness received" },
      { name: "Humility", category: "Virtues and Vices", definition: "A virtue characterized by a modest view of one's own importance and openness to others" },
      { name: "Forgiveness", category: "Virtues and Vices", definition: "The voluntary act of letting go of resentment or claims against someone who has committed a moral wrong" },
      { name: "Eudaimonia", category: "Virtues and Vices", definition: "Often translated as \"flourishing\" or \"human fulfillment\"; the highest good in Aristotelian ethics, achieved through a life of virtue" },
      { name: "Phronesis", category: "Virtues and Vices", definition: "Practical wisdom or moral insight; the intellectual virtue that enables right reasoning about how to live virtuously" },
      { name: "Aretê", category: "Virtues and Vices", definition: "Excellence of character or function; in Greek virtue ethics, the full realization of a thing's potential" },
      { name: "Telos", category: "Virtues and Vices", definition: "The ultimate purpose or end of a thing; in ethics, it refers to the final goal toward which moral life is directed" },
      { name: "Habituation", category: "Virtues and Vices", definition: "The process by which moral character is developed through repeated practice and reinforcement of virtuous behavior (central to Aristotle's ethics)" }
    ];
    
    // Convert each term to the MongoDB document format
    termsData.forEach(term => {
      const keywords = term.definition.split(' ')
        .filter(word => word.length > 4)
        .slice(0, 5)
        .map(word => word.toLowerCase().replace(/[.,;'"!?()]/g, ''));
      
      memes.push({
        name: term.name,
        description: term.definition,
        ethical_dimension: [categories[term.category] || "Other"],
        source_concept: term.category,
        keywords: keywords,
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
      });
    });
    
    return memes;
  }

  const memesToInsert = parseMemeInventory();

  try {
    const result = db.ethical_memes.insertMany(memesToInsert);
    print(`Successfully inserted ${result.insertedIds.length} ethical memes.`);
  } catch (e) {
    print(`Error inserting memes: ${e}`);
  }
} else {
  print('Ethical_memes collection already contains data. Skipping seed.');
} 