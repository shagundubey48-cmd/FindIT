// Single source of truth for form/filter options.
// These values must match what the backend stores and filters on.
export const CATEGORIES = [
  "Electronics",
  "Accessories",
  "Bags",
  "Clothing",
  "Stationery",
  "Documents",
  "Other",
];

export const CAMPUSES = ["JIIT Sector 62", "JIIT Sector 128"];

export const ITEM_TYPES = ["lost", "found"];

export const PROOF_TYPES = [
  { value: "identifying_mark", label: "Identifying mark" },
  { value: "serial_number", label: "Serial number" },
  { value: "purchase_proof", label: "Purchase proof" },
  { value: "other", label: "Other" },
];

export const API_ERROR = "Something went wrong. Please try again.";
