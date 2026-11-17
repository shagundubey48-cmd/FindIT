
import api from "./api";

const itemService = {
  async getItems(filters = {}) {
    const params = {};

    if (filters.q?.trim()) params.q = filters.q.trim();
    if (filters.type) params.type = filters.type;
    if (filters.category) params.category = filters.category;
    if (filters.campus) params.campus = filters.campus;

    const response = await api.get("/items", { params });
    return response.data;
  },

  async getItemById(itemId) {
    const response = await api.get(`/items/${itemId}`);
    return response.data.item;
  },

  async reportLostItem(itemData) {
    const response = await api.post("/items/lost", itemData);
    return response.data;
  },

  async reportFoundItem(itemData) {
    const response = await api.post("/items/found", itemData);
    return response.data;
  },

  async uploadImage(itemId, imageFile) {
    const formData = new FormData();
    formData.append("image", imageFile);

    const response = await api.post(
      `/items/${itemId}/image`,
      formData
    );

    return response.data;
  },

  async updateItem(itemId, itemData) {
    const response = await api.put(`/items/${itemId}`, itemData);
    return response.data;
  },

  async withdrawItem(itemId) {
    const response = await api.patch(`/items/${itemId}/withdraw`);
    return response.data;
  },

  async getMatches(itemId) {
    const response = await api.get(`/items/${itemId}/matches`);
    return response.data;
  }
};

export default itemService;
