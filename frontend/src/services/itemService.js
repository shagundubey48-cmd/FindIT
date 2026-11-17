
import api from "./api";

const itemService = {

  // Get all items with optional filters
  getItems: async (filters = {}) => {
    const response = await api.get("/items", {
      params: filters,
    });

    return response.data;
  },

  // Get lost items
  getLostItems: async (filters = {}) => {
    return itemService.getItems({
      ...filters,
      type: "lost",
    });
  },

  // Get found items
  getFoundItems: async (filters = {}) => {
    return itemService.getItems({
      ...filters,
      type: "found",
    });
  },

  // Report lost item
  reportLost: async (itemData) => {
    const response = await api.post("/items/lost", itemData);
    return response.data;
  },

  // Report found item
  reportFound: async (itemData) => {
    const response = await api.post("/items/found", itemData);
    return response.data;
  },

  // Upload image after item creation
  uploadImage: async (itemId, image) => {
    const formData = new FormData();
    formData.append("image", image);

    const response = await api.post(
      `/items/${itemId}/image`,
      formData
    );

    return response.data;
  },

  // Get single item
  getItemDetails: async (itemId) => {
    const response = await api.get(`/items/${itemId}`);
    return response.data;
  },

  // Update item
  updateItem: async (itemId, itemData) => {
    const response = await api.put(
      `/items/${itemId}`,
      itemData
    );

    return response.data;
  },

  // Withdraw item
  withdrawItem: async (itemId) => {
    const response = await api.patch(
      `/items/${itemId}/withdraw`
    );

    return response.data;
  },

  // Get text matching results
  getMatches: async (itemId) => {
    const response = await api.get(
      `/items/${itemId}/matches`
    );

    return response.data;
  },
};

export default itemService;

