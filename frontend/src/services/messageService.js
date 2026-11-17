import api from "./api";
export const getConversations=()=>api.get("/conversations");
export const getMessages=id=>api.get(`/conversations/${id}/messages`);
export const sendMessage=(id,body)=>api.post(`/conversations/${id}/messages`,{body});
export const startConversation=(itemId,body)=>api.post(`/items/${itemId}/conversations`,{body});

