import React, { useState, useEffect } from 'react';
import ethicalReviewApi from '../services/api';
import '../App.css';

const Governance = () => {
  const [proposals, setProposals] = useState([]);
  const [newProposal, setNewProposal] = useState({ id: '', description: '' });
  const [agentId, setAgentId] = useState('anonymous'); // For simplicity

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    try {
      const response = await ethicalReviewApi.getGovernanceProposals();
      setProposals(response.proposals);
    } catch (err) {
      console.error('Failed to fetch proposals', err);
    }
  };

  const handlePropose = async () => {
    try {
      await ethicalReviewApi.proposeRule(newProposal.id, newProposal.description, agentId);
      fetchProposals();
      setNewProposal({ id: '', description: '' });
    } catch (err) {
      console.error('Failed to propose', err);
    }
  };

  const handleVote = async (proposalId, voteFor) => {
    try {
      await ethicalReviewApi.voteOnProposal(proposalId, agentId, voteFor);
      fetchProposals();
    } catch (err) {
      console.error('Failed to vote', err);
    }
  };

  const handleEnact = async (proposalId) => {
    try {
      await ethicalReviewApi.enactProposal(proposalId);
      fetchProposals();
    } catch (err) {
      console.error('Failed to enact', err);
    }
  };

  return (
    <div className="governance-page">
      <h1>Governance Dashboard</h1>
      <section>
        <h2>Propose New Rule</h2>
        <input
          type="text"
          placeholder="Proposal ID"
          value={newProposal.id}
          onChange={(e) => setNewProposal({ ...newProposal, id: e.target.value })}
        />
        <textarea
          placeholder="Description"
          value={newProposal.description}
          onChange={(e) => setNewProposal({ ...newProposal, description: e.target.value })}
        />
        <button onClick={handlePropose}>Propose</button>
      </section>
      <section>
        <h2>Current Proposals</h2>
        {proposals.map((prop) => (
          <div key={prop.id} className="proposal">
            <h3>{prop.id}: {prop.description}</h3>
            <p>Approval: {prop.approval_ratio.toFixed(2)}</p>
            <p>Active: {prop.active ? 'Yes' : 'No'}</p>
            {prop.active && (
              <>
                <button onClick={() => handleVote(prop.id, true)}>Vote For</button>
                <button onClick={() => handleVote(prop.id, false)}>Vote Against</button>
                <button onClick={() => handleEnact(prop.id)}>Enact</button>
              </>
            )}
          </div>
        ))}
      </section>
    </div>
  );
};

export default Governance; 