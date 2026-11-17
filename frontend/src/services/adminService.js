import api from "./api";
export const getAdminDashboard=()=>api.get("/admin/dashboard");
export const getAdminItems=()=>api.get("/admin/items");
export const getAdminClaims=()=>api.get("/admin/claims");
export const getAdminClaim=id=>api.get(`/admin/claims/${id}`);
export const decideAdminClaim=(id,payload)=>api.patch(`/admin/claims/${id}/decision`,payload);
export const moderateAdminItem=(id,payload)=>api.patch(`/admin/items/${id}/moderation`,payload);
export const getAdminUsers=()=>api.get("/admin/users");
export const getAdminStatistics=()=>api.get("/statistics");
export const getUnclaimedItems=()=>api.get("/unclaimed-items");

