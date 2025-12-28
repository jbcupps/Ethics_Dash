import axios from 'axios';

// Set the base URL for the API
// Default to relative path /api which will be proxied by Nginx in production/docker
// process.env.REACT_APP_API_URL can override this for local dev if needed
const API_URL = process.env.REACT_APP_API_URL || '/api';

// Create an axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API services
export const ethicalReviewApi = {
  // Get list of available models
  getModels: async () => {
    try {
      const response = await apiClient.get('/models');
      // Ensure we return an array, even if the API response is unexpected
      if (response.data && Array.isArray(response.data.models)) {
        return response.data.models;
      }
      console.warn('Unexpected response format when fetching models:', response.data);
      return []; // Return empty array if format is wrong
    } catch (error) {
      console.error('Error fetching models:', error.response || error.message || error);
      // Throw a user-friendly error, keep technical details in console
      throw new Error('Failed to load available models. Please check the connection or backend status.'); 
    }
  },
  
  // MODIFIED: Accept optional endpoints
  analyzePrompt: async (prompt, 
                        originModel = null, 
                        analysisModel = null, 
                        originApiKey = null, 
                        analysisApiKey = null,
                        originApiEndpoint = null, 
                        analysisApiEndpoint = null
                      ) => {
    try {
      const payload = { 
        prompt: prompt 
      };
      // Conditionally add optional fields, ensuring empty strings aren't sent
      if (originModel?.trim()) payload.origin_model = originModel.trim();
      if (analysisModel?.trim()) payload.analysis_model = analysisModel.trim();
      if (originApiKey?.trim()) payload.origin_api_key = originApiKey.trim();
      if (analysisApiKey?.trim()) payload.analysis_api_key = analysisApiKey.trim();
      
      // Only add endpoint if it's a valid non-empty string starting with http/https
      if (originApiEndpoint?.trim() && originApiEndpoint.trim().startsWith('http')) { 
        payload.origin_api_endpoint = originApiEndpoint.trim();
      } else if (originApiEndpoint?.trim()) {
        console.warn('Invalid Origin API Endpoint format provided. Not sending.');
      }
       if (analysisApiEndpoint?.trim() && analysisApiEndpoint.trim().startsWith('http')){
        payload.analysis_api_endpoint = analysisApiEndpoint.trim(); 
      } else if (analysisApiEndpoint?.trim()) {
         console.warn('Invalid Analysis API Endpoint format provided. Not sending.');
      }

      console.log("Sending payload to /analyze:", payload); 
      
      const response = await apiClient.post('/analyze', payload);
      return response.data;
    } catch (error) {
      // Log the detailed error (including response data if available)
      console.error('Error analyzing prompt:', error.response || error.message || error);
      
      // Construct a user-friendly message
      let userMessage = 'Analysis failed. An unknown error occurred.';
      if (error.response && error.response.data && error.response.data.error) {
        // Use the error message from the backend API if available
        userMessage = `Analysis failed: ${error.response.data.error}`;
      } else if (error.request) {
        // Error making the request (e.g., network error)
        userMessage = 'Analysis failed. Could not reach the backend server. Please check your connection.';
      } else {
        // Other errors (e.g., setup issues)
        userMessage = `Analysis failed: ${error.message}`;
      }
      
      // Throw the user-friendly error message
      throw new Error(userMessage);
    }
  },

  // --- NEW: Functions for Ethical Memes API ---
  getMemes: async () => {
    try {
      const response = await apiClient.get('/memes/'); // Ensure trailing slash matches Flask route
      if (response.data && Array.isArray(response.data)) {
        return response.data;
      }
      console.warn('Unexpected response format when fetching memes:', response.data);
      return []; // Return empty array if format is wrong
    } catch (error) {
      console.error('Error fetching memes:', error.response || error.message || error);
      // Throw a user-friendly error
      throw new Error('Failed to load memes. Please check the connection or backend status.');
    }
  },

  // Fetch ontology markdown
  getOntology: async () => {
    try {
      const response = await apiClient.get('/ontology');
      if (response.data && response.data.ontology) {
        return response.data.ontology;
      }
      console.warn('Unexpected response format when fetching ontology:', response.data);
      return '';
    } catch (error) {
      console.error('Error fetching ontology:', error.response || error.message || error);
      throw new Error('Failed to load ontology.');
    }
  },

  // Add createMeme, getMemeById, updateMeme, deleteMeme functions here later
  // if frontend needs to perform these actions directly.

  // Governance methods
  getGovernanceProposals: async () => {
    try {
      const response = await apiClient.get('/govern');
      if (response.data && Array.isArray(response.data.proposals)) {
        return response.data;
      }
      console.warn('Unexpected response format for proposals:', response.data);
      return { proposals: [] };
    } catch (error) {
      console.error('Error fetching proposals:', error);
      throw new Error('Failed to load proposals.');
    }
  },

  proposeRule: async (proposalId, description, proposerId) => {
    try {
      const payload = { action: 'propose', proposal_id: proposalId, description, proposer_id: proposerId };
      const response = await apiClient.post('/govern', payload);
      return response.data;
    } catch (error) {
      console.error('Error proposing rule:', error);
      throw new Error('Failed to propose rule.');
    }
  },

  voteOnProposal: async (proposalId, agentId, voteFor) => {
    try {
      const payload = { action: 'vote', proposal_id: proposalId, agent_id: agentId, vote_for: voteFor };
      const response = await apiClient.post('/govern', payload);
      return response.data;
    } catch (error) {
      console.error('Error voting:', error);
      throw new Error('Failed to vote.');
    }
  },

  enactProposal: async (proposalId) => {
    try {
      const payload = { action: 'enact', proposal_id: proposalId };
      const response = await apiClient.post('/govern', payload);
      return response.data;
    } catch (error) {
      console.error('Error enacting proposal:', error);
      throw new Error('Failed to enact proposal.');
    }
  },

  createAgreement: async (agreement) => {
    try {
      const response = await apiClient.post('/agreements', agreement);
      return response.data;
    } catch (error) {
      console.error('Error creating agreement:', error.response || error.message || error);
      throw new Error('Failed to create agreement.');
    }
  },

  getAgreement: async (agreementId) => {
    try {
      const response = await apiClient.get(`/agreements/${agreementId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching agreement:', error.response || error.message || error);
      throw new Error('Failed to load agreement.');
    }
  },

  addAgreementAction: async (agreementId, actionPayload) => {
    try {
      const response = await apiClient.post(`/agreements/${agreementId}/actions`, actionPayload);
      return response.data;
    } catch (error) {
      console.error('Error updating agreement:', error.response || error.message || error);
      throw new Error('Failed to update agreement.');
    }
  },

  getAgreementHistory: async (agreementId) => {
    try {
      const response = await apiClient.get(`/agreements/${agreementId}/history`);
      return response.data;
    } catch (error) {
      console.error('Error fetching agreement history:', error.response || error.message || error);
      throw new Error('Failed to load agreement history.');
    }
  },
};

export default ethicalReviewApi; 
