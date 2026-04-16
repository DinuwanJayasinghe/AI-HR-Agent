import { useState, useEffect } from 'react';
import {
  UserPlus,
  Search,
  Mail,
  Calendar,
  Edit,
  Trash2,
  ChevronRight,
} from 'lucide-react';
import { employeeAPI } from '../../services/api';
import AddEmployeeModal from './AddEmployeeModal';
import EmployeeDetails from './EmployeeDetails';

const EmployeeCard = ({ employee, onClick }) => {
  const totalLeave =
    (employee.leave_balance?.Vacation || 0) +
    (employee.leave_balance?.['Sick Leave'] || 0) +
    (employee.leave_balance?.['Personal Leave'] || 0);

  return (
    <div
      onClick={() => onClick(employee)}
      className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-lg hover:border-primary-300 transition-all cursor-pointer group"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-4 flex-1">
          <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-white font-semibold text-lg">
              {employee.name.charAt(0)}
            </span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-lg group-hover:text-primary-700 transition-colors">
              {employee.name}
            </h3>
            <div className="flex items-center text-sm text-gray-500 mt-1">
              <Mail className="w-4 h-4 mr-1" />
              {employee.email}
            </div>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3">
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-xs text-blue-600 font-medium">Vacation</p>
          <p className="text-xl font-bold text-blue-700 mt-1">
            {employee.leave_balance?.Vacation || 0}
          </p>
          <p className="text-xs text-blue-600">days</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <p className="text-xs text-green-600 font-medium">Sick Leave</p>
          <p className="text-xl font-bold text-green-700 mt-1">
            {employee.leave_balance?.['Sick Leave'] || 0}
          </p>
          <p className="text-xs text-green-600">days</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-3">
          <p className="text-xs text-purple-600 font-medium">Personal</p>
          <p className="text-xl font-bold text-purple-700 mt-1">
            {employee.leave_balance?.['Personal Leave'] || 0}
          </p>
          <p className="text-xs text-purple-600">days</p>
        </div>
      </div>

      {employee.manager_email && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Manager: <span className="text-gray-700">{employee.manager_email}</span>
          </p>
        </div>
      )}
    </div>
  );
};

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredEmployees(employees);
    } else {
      const filtered = employees.filter(
        (emp) =>
          emp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          emp.email.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredEmployees(filtered);
    }
  }, [searchQuery, employees]);

  const fetchEmployees = async () => {
    try {
      const data = await employeeAPI.getAllEmployees();
      setEmployees(data);
      setFilteredEmployees(data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmployee = async (employeeData) => {
    try {
      await employeeAPI.addEmployee(employeeData);
      await fetchEmployees();
      setShowAddModal(false);
    } catch (error) {
      console.error('Error adding employee:', error);
      alert('Failed to add employee');
    }
  };

  if (selectedEmployee) {
    return (
      <EmployeeDetails
        employee={selectedEmployee}
        onBack={() => setSelectedEmployee(null)}
        onUpdate={fetchEmployees}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
          <p className="text-gray-600 mt-1">
            Manage employee information and leave balances
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2 font-medium"
        >
          <UserPlus className="w-5 h-5" />
          <span>Add Employee</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search employees by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Total Employees</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {filteredEmployees.length}
            </p>
          </div>
          <Calendar className="w-10 h-10 text-primary-600" />
        </div>
      </div>

      {/* Employee Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredEmployees.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEmployees.map((employee) => (
            <EmployeeCard
              key={employee.email}
              employee={employee}
              onClick={setSelectedEmployee}
            />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600">
            {searchQuery
              ? 'No employees found matching your search'
              : 'No employees found. Add your first employee to get started.'}
          </p>
        </div>
      )}

      {/* Add Employee Modal */}
      {showAddModal && (
        <AddEmployeeModal
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddEmployee}
        />
      )}
    </div>
  );
};

export default Employees;
