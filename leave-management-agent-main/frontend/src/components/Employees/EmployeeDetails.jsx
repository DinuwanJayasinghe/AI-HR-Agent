import { useState } from 'react';
import { ArrowLeft, Mail, UserCog, Edit2, Save, X } from 'lucide-react';
import { employeeAPI } from '../../services/api';

const EmployeeDetails = ({ employee, onBack, onUpdate }) => {
  const [editing, setEditing] = useState(false);
  const [balances, setBalances] = useState({
    Vacation: employee.leave_balance?.Vacation || 0,
    'Sick Leave': employee.leave_balance?.['Sick Leave'] || 0,
    'Personal Leave': employee.leave_balance?.['Personal Leave'] || 0,
  });

  const handleSave = async () => {
    try {
      await Promise.all([
        employeeAPI.updateLeaveBalance(employee.email, 'Vacation', balances.Vacation),
        employeeAPI.updateLeaveBalance(employee.email, 'Sick Leave', balances['Sick Leave']),
        employeeAPI.updateLeaveBalance(
          employee.email,
          'Personal Leave',
          balances['Personal Leave']
        ),
      ]);
      await onUpdate();
      setEditing(false);
      alert('Leave balances updated successfully');
    } catch (error) {
      console.error('Error updating balances:', error);
      alert('Failed to update leave balances');
    }
  };

  const handleBalanceChange = (type, value) => {
    setBalances((prev) => ({
      ...prev,
      [type]: parseInt(value) || 0,
    }));
  };

  const totalLeave = Object.values(balances).reduce((sum, val) => sum + val, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Back to Employees</span>
        </button>
        {!editing ? (
          <button
            onClick={() => setEditing(true)}
            className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            <Edit2 className="w-4 h-4" />
            <span>Edit Balances</span>
          </button>
        ) : (
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                setEditing(false);
                setBalances({
                  Vacation: employee.leave_balance?.Vacation || 0,
                  'Sick Leave': employee.leave_balance?.['Sick Leave'] || 0,
                  'Personal Leave': employee.leave_balance?.['Personal Leave'] || 0,
                });
              }}
              className="flex items-center space-x-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              <X className="w-4 h-4" />
              <span>Cancel</span>
            </button>
            <button
              onClick={handleSave}
              className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </button>
          </div>
        )}
      </div>

      {/* Employee Profile Card */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-primary-500 to-primary-700 px-6 py-8">
          <div className="flex items-center space-x-4">
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-primary-700 font-bold text-3xl">
                {employee.name.charAt(0)}
              </span>
            </div>
            <div className="text-white">
              <h1 className="text-2xl font-bold">{employee.name}</h1>
              <div className="flex items-center mt-2 space-x-4">
                <div className="flex items-center space-x-2">
                  <Mail className="w-4 h-4" />
                  <span>{employee.email}</span>
                </div>
                {employee.manager_email && (
                  <div className="flex items-center space-x-2">
                    <UserCog className="w-4 h-4" />
                    <span>{employee.manager_email}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-sm text-gray-600 font-medium">Total Leave Days</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{totalLeave}</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-blue-600 font-medium">Vacation</p>
              <p className="text-3xl font-bold text-blue-700 mt-2">{balances.Vacation}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <p className="text-sm text-green-600 font-medium">Sick Leave</p>
              <p className="text-3xl font-bold text-green-700 mt-2">
                {balances['Sick Leave']}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
              <p className="text-sm text-purple-600 font-medium">Personal Leave</p>
              <p className="text-3xl font-bold text-purple-700 mt-2">
                {balances['Personal Leave']}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Leave Balances */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Leave Balance Management</h2>

        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Vacation Days
              </label>
              <input
                type="number"
                min="0"
                value={balances.Vacation}
                onChange={(e) => handleBalanceChange('Vacation', e.target.value)}
                disabled={!editing}
                className={`w-full px-4 py-3 border rounded-lg text-lg font-semibold ${
                  editing
                    ? 'border-blue-300 bg-blue-50 text-blue-900 focus:outline-none focus:ring-2 focus:ring-blue-500'
                    : 'border-gray-300 bg-gray-50 text-gray-700'
                }`}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sick Leave Days
              </label>
              <input
                type="number"
                min="0"
                value={balances['Sick Leave']}
                onChange={(e) => handleBalanceChange('Sick Leave', e.target.value)}
                disabled={!editing}
                className={`w-full px-4 py-3 border rounded-lg text-lg font-semibold ${
                  editing
                    ? 'border-green-300 bg-green-50 text-green-900 focus:outline-none focus:ring-2 focus:ring-green-500'
                    : 'border-gray-300 bg-gray-50 text-gray-700'
                }`}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Personal Leave Days
              </label>
              <input
                type="number"
                min="0"
                value={balances['Personal Leave']}
                onChange={(e) => handleBalanceChange('Personal Leave', e.target.value)}
                disabled={!editing}
                className={`w-full px-4 py-3 border rounded-lg text-lg font-semibold ${
                  editing
                    ? 'border-purple-300 bg-purple-50 text-purple-900 focus:outline-none focus:ring-2 focus:ring-purple-500'
                    : 'border-gray-300 bg-gray-50 text-gray-700'
                }`}
              />
            </div>
          </div>

          {editing && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Changes will be applied immediately to the employee's
                leave balance. Make sure to verify the values before saving.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Leave History (Placeholder) */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Leave History</h2>
        <p className="text-gray-600 text-center py-8">
          No leave history available. Leave requests will appear here once processed.
        </p>
      </div>
    </div>
  );
};

export default EmployeeDetails;
