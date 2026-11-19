import api from "./api";

export const getItemMatches = (id) => api.get(`/items/${id}/matches`);
export const getCombinedMatches = (id) => api.get(`/items/${id}/matched-items`);
export const getImageMatches = (id) => api.get(`/items/${id}/image-matches`);
