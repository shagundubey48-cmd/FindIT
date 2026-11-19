import api from "./api";

export const createClaim = (itemId, payload) =>
  api.post(`/items/${itemId}/claims`, payload);
export const getMyClaims = () => api.get("/claims");
export const getClaim = (id) => api.get(`/claims/${id}`);
export const submitClaimEvidence = (id, payload) =>
  api.put(`/claims/${id}/evidence`, payload);
export const getHandoverQr = (claimId) =>
  api.get(`/claims/${claimId}/handover-qr`, { responseType: "blob" });
export const getItemQr = (itemId) =>
  api.get(`/items/${itemId}/qr`, { responseType: "blob" });

// Secret question (finder sets it, claimant answers it before claiming)
export const getSecretQuestion = (itemId) =>
  api.get(`/items/${itemId}/secret-question`);
export const setSecretQuestion = (itemId, payload) =>
  api.put(`/items/${itemId}/secret-question`, payload);
export const verifySecretAnswer = (itemId, answer) =>
  api.post(`/items/${itemId}/secret-question/verify`, { answer });
