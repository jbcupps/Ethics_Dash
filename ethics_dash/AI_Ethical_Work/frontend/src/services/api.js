import axios from 'axios';

// Set the base URL for the API
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

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
      return Array.isArray(response.data.models) ? response.data.models : [];
    } catch (error) {
      console.error('Error fetching models:', error);
      // Return empty array on error so the UI doesn't break
      return []; 
      // Optionally re-throw or handle more gracefully
      // throw error;
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
      console.error('Error analyzing prompt:', error);
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw new Error('An unknown error occurred while analyzing the prompt.');
    }
  }
};

export default ethicalReviewApi; 