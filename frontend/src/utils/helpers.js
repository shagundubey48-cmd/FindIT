export const formatDate=value=>{if(!value)return "—";const date=new Date(value);return Number.isNaN(date.getTime())?"—":date.toLocaleDateString("en-IN",{day:"numeric",month:"short",year:"numeric"});};
export const getErrorMessage=error=>error?.response?.data?.message||error?.message||"Something went wrong.";
export const titleCase=value=>String(value||"").replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());

