package reputation

type Proposal struct {
	ID           string
	Description  string
	VotesFor     float64
	VotesAgainst float64
	Voters       map[string]bool // To prevent double voting
	Active       bool
}

type DAOContract struct {
	proposals  map[string]*Proposal
	reputation *ReputationContract
	quorum     float64
}

func NewDAOContract(repContract *ReputationContract, quorum float64) *DAOContract {
	return &DAOContract{
		proposals:  make(map[string]*Proposal),
		reputation: repContract,
		quorum:     quorum,
	}
}

func (d *DAOContract) ProposeRule(id string, description string, proposerID string) bool {
	if _, exists := d.proposals[id]; exists {
		return false
	}
	// Check proposer reputation
	if d.reputation.GetReputation(proposerID) < 30 {
		return false
	}
	d.proposals[id] = &Proposal{
		ID:           id,
		Description:  description,
		VotesFor:     0,
		VotesAgainst: 0,
		Voters:       make(map[string]bool),
		Active:       true,
	}
	return true
}

func (d *DAOContract) Vote(proposalID string, agentID string, voteFor bool, weight int) bool {
	prop, exists := d.proposals[proposalID]
	if !exists || !prop.Active {
		return false
	}
	if prop.Voters[agentID] {
		return false
	}
	voteWeight := d.reputation.QuadraticVote(agentID, weight)
	if voteFor {
		prop.VotesFor += voteWeight
	} else {
		prop.VotesAgainst += voteWeight
	}
	prop.Voters[agentID] = true
	return true
}

func (d *DAOContract) Enact(proposalID string) bool {
	prop, exists := d.proposals[proposalID]
	if !exists || !prop.Active {
		return false
	}
	totalVotes := prop.VotesFor + prop.VotesAgainst
	if totalVotes == 0 {
		return false
	}
	if prop.VotesFor/totalVotes >= d.quorum {
		prop.Active = false
		// Update chaincode or ethical rules here
		return true
	}
	return false
}

func (d *DAOContract) GetProposal(id string) *Proposal {
	return d.proposals[id]
}

func (d *DAOContract) GetAllProposals() []*Proposal {
	var all []*Proposal
	for _, p := range d.proposals {
		all = append(all, p)
	}
	return all
}
