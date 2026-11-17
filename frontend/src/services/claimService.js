import api from "./api";
export const createClaim=(itemId,payload)=>api.post(`/items/${itemId}/claims`,payload);
export const getMyClaims=()=>api.get("/claims/my");
export const getClaim=id=>api.get(`/claims/${id}`);
export const getItemClaims=id=>api.get(`/items/${id}/claims`);
export const withdrawClaim=id=>api.patch(`/claims/${id}/withdraw`);

