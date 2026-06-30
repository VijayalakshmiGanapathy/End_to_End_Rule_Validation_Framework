import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export const runValidation = async (payload) => {
  const response = await axios.post(`${API_BASE_URL}/validate-batch`, payload);
  return response.data;
};

export const getBatchOptions = async () => {
  const response = await axios.get(`${API_BASE_URL}/batch-options`);
  return response.data;
};