import { useState, useEffect } from 'react';
import { Users, Calendar, Clock, CheckCircle, TrendingUp } from 'lucide-react';
import { statsAPI, employeeAPI } from '../../services/api';

const StatCard = ({ icon: Icon, title, value, color, bgColor, change }) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {change && (
            <div className="flex items-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">{change}</span>
            </div>
          )}
        </div>
        <div className={`${bgColor} ${color} p-4 rounded-lg`}>
          <Icon className="w-8 h-8" />
        </div>
      </div>
    </div>
  );
};

const RecentEmployee = ({ employee }) => {
  const totalLeave =
    (employee.leave_balance?.Vacation || 0) +
    (employee.leave_balance?.['Sick Leave'] || 0) +
    (employee.leave_balance?.['Personal Leave'] || 0);

  return (
    <div className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg transition-colors">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
          <span className="text-primary-700 font-medium">
            {employee.name.charAt(0)}
          </span>
        </div>
        <div>
          <p className="font-medium text-gray-900">{employee.name}</p>
          <p className="text-sm text-gray-500">{employee.email}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-gray-900">{totalLeave} days</p>
        <p className="text-xs text-gray-500">Total Leave</p>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_employees: 0,
    total_leave_days: 0,
    pending_requests: 0,
    approved_today: 0,
  });
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsData, employeesData] = await Promise.all([
        statsAPI.getStats(),
        employeeAPI.getAllEmployees(),
      ]);
      setStats(statsData);
      setEmployees(employeesData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Users}
          title="Total Employees"
          value={stats.total_employees}
          color="text-blue-600"
          bgColor="bg-blue-50"
          change="+2 this month"
        />
        <StatCard
          icon={Calendar}
          title="Total Leave Days"
          value={stats.total_leave_days}
          color="text-green-600"
          bgColor="bg-green-50"
        />
        <StatCard
          icon={Clock}
          title="Pending Requests"
          value={stats.pending_requests}
          color="text-yellow-600"
          bgColor="bg-yellow-50"
        />
        <StatCard
          icon={CheckCircle}
          title="Approved Today"
          value={stats.approved_today}
          color="text-primary-600"
          bgColor="bg-primary-50"
        />
      </div>

      {/* Recent Employees Section */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Employees Overview</h2>
          <p className="text-sm text-gray-600 mt-1">Recent employee leave balances</p>
        </div>
        <div className="p-4 space-y-2">
          {employees.length > 0 ? (
            employees.map((employee) => (
              <RecentEmployee key={employee.email} employee={employee} />
            ))
          ) : (
            <p className="text-center text-gray-500 py-8">No employees found</p>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Add New Employee</h3>
          <p className="text-primary-100 text-sm mb-4">
            Quickly add a new employee to the system
          </p>
          <button className="bg-white text-primary-700 px-4 py-2 rounded-lg font-medium hover:bg-primary-50 transition-colors">
            Add Employee
          </button>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-lg p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Process Requests</h3>
          <p className="text-green-100 text-sm mb-4">
            Check and process pending leave requests
          </p>
          <button className="bg-white text-green-700 px-4 py-2 rounded-lg font-medium hover:bg-green-50 transition-colors">
            View Requests
          </button>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-lg p-6 text-white">
          <h3 className="text-lg font-semibold mb-2">Generate Report</h3>
          <p className="text-purple-100 text-sm mb-4">
            Create comprehensive leave reports
          </p>
          <button className="bg-white text-purple-700 px-4 py-2 rounded-lg font-medium hover:bg-purple-50 transition-colors">
            Generate
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
