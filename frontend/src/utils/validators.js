export const isRequired=value=>String(value??"").trim().length>0;
export const isValidEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value||"");
export const isValidDate=value=>!Number.isNaN(Date.parse(value));

