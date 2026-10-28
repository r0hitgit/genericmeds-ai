import axios from 'axios';

// Create configured Axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Response interceptor for consistent error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred while communicating with GenericMeds AI backend.';
    return Promise.reject(new Error(message));
  }
);

export const api = {
  // Medicines
  searchMedicines: (query, limit = 20, offset = 0, janAushadhiOnly = false) => {
    return apiClient.get('/api/v1/medicines/search', {
      params: {
        q: query,
        limit,
        offset,
        jan_aushadhi_only: janAushadhiOnly,
      },
    });
  },

  getMedicineById: (id) => {
    return apiClient.get(`/api/v1/medicines/${id}`);
  },

  // Alternatives
  findAlternatives: (medicineId, maxCandidates = 10, includeJanAushadhiOnly = false) => {
    return apiClient.post('/api/v1/alternatives/search', {
      medicine_id: Number(medicineId),
      max_candidates: maxCandidates,
      include_jan_aushadhi_only: includeJanAushadhiOnly,
    });
  },

  // Price Comparison
  comparePrices: (medicineIds) => {
    return apiClient.post('/api/v1/prices/compare', {
      medicine_ids: medicineIds.map(Number),
    });
  },

  // Brand Lookups
  searchBrands: (query, limit = 20, offset = 0) => {
    return apiClient.get('/api/v1/brands/search', {
      params: { q: query, limit, offset },
    });
  },

  getBrandById: (brandLookupId) => {
    return apiClient.get(`/api/v1/brands/${brandLookupId}`);
  },

  // Kendras
  getNearbyKendras: (lat, lon, radiusKm = 10, limit = 25) => {
    return apiClient.get('/api/v1/kendras/nearby', {
      params: { lat, lon, radius_km: radiusKm, limit },
    });
  },

  searchKendrasManual: ({ state, district, pincode, q, limit = 25, offset = 0 }) => {
    const params = { limit, offset };
    if (state) params.state = state;
    if (district) params.district = district;
    if (pincode) params.pincode = pincode;
    if (q) params.q = q;
    return apiClient.get('/api/v1/kendras/search', { params });
  },

  lookupPincode: (pincode) => {
    return apiClient.get('/api/v1/kendras/lookup-pin', { params: { pincode } });
  },

  getAllKendras: ({ q, is_24x7, limit = 50 } = {}) => {
    const params = { limit };
    if (q) params.q = q;
    if (is_24x7 !== undefined && is_24x7 !== null) params.is_24x7 = is_24x7;
    return apiClient.get('/api/v1/kendras', { params });
  },

  getTherapeuticGroups: () => {
    return apiClient.get('/api/v1/kendras/groups');
  },

  getGuidelines: (therapeuticClass) => {
    const params = {};
    if (therapeuticClass) params.therapeutic_class = therapeuticClass;
    return apiClient.get('/api/v1/kendras/guidelines', { params });
  },

  // AI Chat
  sendChatMessage: ({ message, language = 'en', conversationHistory = [] }) => {
    return apiClient.post('/api/v1/chat', {
      message,
      language,
      conversation_history: conversationHistory,
    });
  },

  // Sources
  getSources: () => {
    return apiClient.get('/api/v1/sources');
  },

  // Health
  getHealth: () => {
    return apiClient.get('/health');
  },
};

export default api;
