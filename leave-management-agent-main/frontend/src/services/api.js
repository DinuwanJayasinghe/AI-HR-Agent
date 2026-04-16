import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const employeeAPI = {
  // Get all employees
  getAllEmployees: async () => {
    const response = await api.get('/employees');
    return response.data;
  },

  // Get a specific employee
  getEmployee: async (email) => {
    const response = await api.get(`/employees/${email}`);
    return response.data;
  },

  // Add a new employee
  addEmployee: async (employeeData) => {
    const response = await api.post('/employees', employeeData);
    return response.data;
  },

  // Get leave balance for an employee
  getLeaveBalance: async (email) => {
    const response = await api.get(`/leave-balance/${email}`);
    return response.data;
  },

  // Update leave balance
  updateLeaveBalance: async (email, leaveType, balance) => {
    const response = await api.put(`/leave-balance/${email}`, {
      leave_type: leaveType,
      balance: balance,
    });
    return response.data;
  },
};

export const leaveRequestAPI = {
  // Get all leave requests
  getAllLeaveRequests: async () => {
    const response = await api.get('/leave-requests');
    return response.data;
  },
};

export const statsAPI = {
  // Get dashboard statistics
  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },
};

export default api;
