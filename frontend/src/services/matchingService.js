import api from "./api";
export const getItemMatches=id=>api.get(`/items/${id}/matches`);
export const getCombinedMatches=id=>api.get(`/items/${id}/combined-matches`);
export const matchByImage=payload=>api.post("/match/image",payload);

