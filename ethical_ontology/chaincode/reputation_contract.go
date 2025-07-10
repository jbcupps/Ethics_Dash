package reputation

import "math"

type ReputationContract struct {
	reputations map[string]int  // agentID -> reputation score
	tokens      map[string]bool // agentID -> hasToken
}

func NewReputationContract() *ReputationContract {
	return &ReputationContract{
		reputations: make(map[string]int),
		tokens:      make(map[string]bool),
	}
}

func (c *ReputationContract) MintToken(agentID string, virtueScore int) bool {
	if virtueScore > 80 && !c.tokens[agentID] {
		c.tokens[agentID] = true
		c.reputations[agentID] = virtueScore
		return true
	}
	return false
}

func (c *ReputationContract) RevokeToken(agentID string) {
	if c.tokens[agentID] {
		delete(c.tokens, agentID)
		c.reputations[agentID] = 0
	}
}

func (c *ReputationContract) GetReputation(agentID string) int {
	return c.reputations[agentID]
}

func (c *ReputationContract) QuadraticVote(agentID string, voteWeight int) float64 {
	rep := c.GetReputation(agentID)
	return float64(voteWeight) * math.Sqrt(float64(rep))
}

// Stub for proof-of-expertise integration
func (c *ReputationContract) VerifyExpertise(agentID string, domain string) bool {
	// Mock external query
	return true
}
