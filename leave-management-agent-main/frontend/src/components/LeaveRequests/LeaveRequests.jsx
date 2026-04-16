import { useState, useEffect } from 'react';
import { Calendar, Clock, CheckCircle, XCircle, AlertCircle, Filter } from 'lucide-react';
import { leaveRequestAPI } from '../../services/api';

const StatusBadge = ({ status }) => {
  const styles = {
    approved: 'bg-green-100 text-green-800 border-green-200',
    rejected: 'bg-red-100 text-red-800 border-red-200',
    pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  };

  const icons = {
    approved: CheckCircle,
    rejected: XCircle,
    pending: Clock,
  };

  const Icon = icons[status] || AlertCircle;

  return (
    <span
      className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium border ${
        styles[status] || 'bg-gray-100 text-gray-800 border-gray-200'
      }`}
    >
      <Icon className="w-3 h-3" />
      <span className="capitalize">{status}</span>
    </span>
  );
};

const LeaveRequestCard = ({ request }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-700 font-medium">
              {request.employee_name?.charAt(0) || 'U'}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{request.employee_name}</h3>
            <p className="text-sm text-gray-500">{request.employee_email}</p>
          </div>
        </div>
        <StatusBadge status={request.status} />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Leave Type</span>
          <span className="text-sm font-medium text-gray-900">{request.leave_type}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Start Date</span>
          <span className="text-sm font-medium text-gray-900">{request.start_date}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">End Date</span>
          <span className="text-sm font-medium text-gray-900">{request.end_date}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Days</span>
          <span className="text-sm font-medium text-gray-900">
            {request.days_requested} days
          </span>
        </div>
      </div>

      {request.reason && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Reason:</span> {request.reason}
          </p>
        </div>
      )}

      {request.status === 'pending' && (
        <div className="mt-4 flex items-center space-x-2">
          <button className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium">
            Approve
          </button>
          <button className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm font-medium">
            Reject
          </button>
        </div>
      )}
    </div>
  );
};

const LeaveRequests = () => {
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequests();
  }, []);

  useEffect(() => {
    if (filter === 'all') {
      setFilteredRequests(requests);
    } else {
      setFilteredRequests(requests.filter((req) => req.status === filter));
    }
  }, [filter, requests]);

  const fetchRequests = async () => {
    try {
      const data = await leaveRequestAPI.getAllLeaveRequests();
      setRequests(data);
      setFilteredRequests(data);
    } catch (error) {
      console.error('Error fetching leave requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    total: requests.length,
    pending: requests.filter((r) => r.status === 'pending').length,
    approved: requests.filter((r) => r.status === 'approved').length,
    rejected: requests.filter((r) => r.status === 'rejected').length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Leave Requests</h1>
        <p className="text-gray-600 mt-1">
          Review and manage employee leave requests
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Requests</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total}</p>
            </div>
            <Calendar className="w-10 h-10 text-gray-400" />
          </div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-yellow-700">Pending</p>
              <p className="text-2xl font-bold text-yellow-900 mt-1">{stats.pending}</p>
            </div>
            <Clock className="w-10 h-10 text-yellow-600" />
          </div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-700">Approved</p>
              <p className="text-2xl font-bold text-green-900 mt-1">{stats.approved}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-700">Rejected</p>
              <p className="text-2xl font-bold text-red-900 mt-1">{stats.rejected}</p>
            </div>
            <XCircle className="w-10 h-10 text-red-600" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <div className="flex items-center space-x-2">
            {['all', 'pending', 'approved', 'rejected'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === status
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Requests List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredRequests.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRequests.map((request, index) => (
            <LeaveRequestCard key={index} request={request} />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">
            {filter === 'all'
              ? 'No leave requests found. Requests will appear here once employees submit them via email.'
              : `No ${filter} leave requests found.`}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            The system automatically processes leave requests sent via email.
          </p>
        </div>
      )}
    </div>
  );
};

export default LeaveRequests;
