import api from "./api";

export const getMyHandovers = () => api.get("/handovers/my");
export const getHandoverHistory = (itemId) =>
  api.get(`/items/${itemId}/handover-history`);
export const confirmHandover = (claimId, payload = {}) =>
  api.post(`/admin/claims/${claimId}/handover`, payload);

export const submitFeedback = (handoverId, payload) =>
  api.post(`/handovers/${handoverId}/feedback`, payload);
export const getMyFeedback = () => api.get("/feedback/my");
