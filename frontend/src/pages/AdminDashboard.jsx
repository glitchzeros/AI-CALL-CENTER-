import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Key, 
  Smartphone, 
  Users, 
  Activity, 
  Plus, 
  Edit3, 
  Trash2, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Database,
  Wifi,
  WifiOff
} from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner, { CardLoader } from '../components/LoadingSpinner';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [apiKeys, setApiKeys] = useState([]);
  const [modems, setModems] = useState([]);
  const [companyConfigs, setCompanyConfigs] = useState([]);
  const [apiAssignments, setApiAssignments] = useState([]);
  const [modemAssignments, setModemAssignments] = useState([]);

  // Modal states
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [showModemModal, setShowModemModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [stats, keys, modemsData, configs, assignments, modemAssignments] = await Promise.all([
        api.get('/api/admin/dashboard'),
        api.get('/api/admin/api-keys'),
        api.get('/api/admin/modems'),
        api.get('/api/admin/company-configs'),
        api.get('/api/admin/api-key-assignments'),
        api.get('/api/admin/modem-assignments')
      ]);

      setDashboardStats(stats.data);
      setApiKeys(keys.data);
      setModems(modemsData.data);
      setCompanyConfigs(configs.data);
      setApiAssignments(assignments.data);
      setModemAssignments(modemAssignments.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const detectModems = async () => {
    try {
      const response = await api.post('/api/admin/modems/detect');
      setModems(response.data);
      await loadDashboardData(); // Refresh all data
    } catch (error) {
      console.error('Failed to detect modems:', error);
    }
  };

  const updateModemStatus = async () => {
    try {
      await api.post('/api/admin/tasks/update-modem-status');
      await loadDashboardData();
    } catch (error) {
      console.error('Failed to update modem status:', error);
    }
  };

  const cleanupExpiredAssignments = async () => {
    try {
      await api.post('/api/admin/tasks/cleanup-expired');
      await loadDashboardData();
    } catch (error) {
      console.error('Failed to cleanup expired assignments:', error);
    }
  };

  if (loading) {
    return <CardLoader text="Loading admin dashboard..." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-['Cinzel_Decorative'] text-amber-800 mb-2">
            🏛️ Admin Dashboard
          </h1>
          <p className="text-amber-700 font-['Vollkorn']">
            The Scribe's Command Center - Manage API keys, modems, and configurations
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 bg-white rounded-lg p-2 border-2 border-amber-200">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: Activity },
              { id: 'api-keys', label: 'API Keys', icon: Key },
              { id: 'modems', label: 'GSM Modems', icon: Smartphone },
              { id: 'company-configs', label: 'Company Configs', icon: Settings },
              { id: 'assignments', label: 'Assignments', icon: Users }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-amber-600 text-white'
                    : 'text-amber-700 hover:bg-amber-100'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Dashboard Overview */}
        {activeTab === 'dashboard' && (
          <DashboardOverview 
            stats={dashboardStats}
            onDetectModems={detectModems}
            onUpdateModemStatus={updateModemStatus}
            onCleanupExpired={cleanupExpiredAssignments}
          />
        )}

        {/* API Keys Management */}
        {activeTab === 'api-keys' && (
          <ApiKeysManagement 
            apiKeys={apiKeys}
            onRefresh={loadDashboardData}
            showModal={showApiKeyModal}
            setShowModal={setShowApiKeyModal}
            editingItem={editingItem}
            setEditingItem={setEditingItem}
          />
        )}

        {/* Modems Management */}
        {activeTab === 'modems' && (
          <ModemsManagement 
            modems={modems}
            modemAssignments={modemAssignments}
            companyConfigs={companyConfigs}
            apiKeys={apiKeys.filter(key => key.key_type === 'company')}
            onRefresh={loadDashboardData}
            onDetectModems={detectModems}
          />
        )}

        {/* Company Configurations */}
        {activeTab === 'company-configs' && (
          <CompanyConfigsManagement 
            configs={companyConfigs}
            apiKeys={apiKeys.filter(key => key.key_type === 'company')}
            modems={modems}
            onRefresh={loadDashboardData}
            showModal={showConfigModal}
            setShowModal={setShowConfigModal}
            editingItem={editingItem}
            setEditingItem={setEditingItem}
          />
        )}

        {/* Assignments Overview */}
        {activeTab === 'assignments' && (
          <AssignmentsOverview 
            apiAssignments={apiAssignments}
            modemAssignments={modemAssignments}
            onRefresh={loadDashboardData}
          />
        )}
      </div>
    </div>
  );
};

// Dashboard Overview Component
const DashboardOverview = ({ stats, onDetectModems, onUpdateModemStatus, onCleanupExpired }) => (
  <div className="space-y-6">
    {/* Stats Cards */}
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        title="Available Client Keys"
        value={stats?.available_client_keys || 0}
        icon={Key}
        color="green"
      />
      <StatCard
        title="Assigned Client Keys"
        value={stats?.assigned_client_keys || 0}
        icon={Users}
        color="blue"
      />
      <StatCard
        title="Online Modems"
        value={stats?.online_modems || 0}
        icon={Wifi}
        color="green"
      />
      <StatCard
        title="Active Subscribers"
        value={stats?.active_subscribers || 0}
        icon={CheckCircle}
        color="purple"
      />
    </div>

    {/* Quick Actions */}
    <div className="bg-white rounded-lg border-2 border-amber-200 p-6">
      <h3 className="text-xl font-['Cinzel_Decorative'] text-amber-800 mb-4">
        Quick Actions
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={onDetectModems}
          className="flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg transition-colors"
        >
          <Smartphone className="h-5 w-5" />
          <span>Detect Modems</span>
        </button>
        <button
          onClick={onUpdateModemStatus}
          className="flex items-center justify-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg transition-colors"
        >
          <RefreshCw className="h-5 w-5" />
          <span>Update Status</span>
        </button>
        <button
          onClick={onCleanupExpired}
          className="flex items-center justify-center space-x-2 bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-lg transition-colors"
        >
          <Trash2 className="h-5 w-5" />
          <span>Cleanup Expired</span>
        </button>
      </div>
    </div>
  </div>
);

// Stat Card Component
const StatCard = ({ title, value, icon: Icon, color }) => {
  const colorClasses = {
    green: 'bg-green-100 text-green-800 border-green-200',
    blue: 'bg-blue-100 text-blue-800 border-blue-200',
    purple: 'bg-purple-100 text-purple-800 border-purple-200',
    orange: 'bg-orange-100 text-orange-800 border-orange-200'
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{title}</p>
          <p className="text-3xl font-bold">{value}</p>
        </div>
        <Icon className="h-8 w-8 opacity-75" />
      </div>
    </div>
  );
};

// API Keys Management Component
const ApiKeysManagement = ({ apiKeys, onRefresh, showModal, setShowModal, editingItem, setEditingItem }) => {
  const [newApiKey, setNewApiKey] = useState({
    api_key: '',
    key_type: 'client',
    daily_limit: 1000,
    monthly_limit: 30000,
    notes: ''
  });

  const handleCreateApiKey = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/admin/api-keys', newApiKey);
      setShowModal(false);
      setNewApiKey({
        api_key: '',
        key_type: 'client',
        daily_limit: 1000,
        monthly_limit: 30000,
        notes: ''
      });
      onRefresh();
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  };

  const handleDeleteApiKey = async (keyId) => {
    if (window.confirm('Are you sure you want to delete this API key?')) {
      try {
        await api.delete(`/api/admin/api-keys/${keyId}`);
        onRefresh();
      } catch (error) {
        console.error('Failed to delete API key:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-['Cinzel_Decorative'] text-amber-800">
          API Keys Management
        </h2>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>Add API Key</span>
        </button>
      </div>

      {/* API Keys Table */}
      <div className="bg-white rounded-lg border-2 border-amber-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-amber-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                  API Key
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                  Usage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                  Limits
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-amber-800 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-amber-200">
              {apiKeys.map((key) => (
                <tr key={key.id} className="hover:bg-amber-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-mono text-gray-900">
                      {key.api_key.substring(0, 20)}...
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      key.key_type === 'company' 
                        ? 'bg-purple-100 text-purple-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {key.key_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={key.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {key.usage_count || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {key.daily_limit}/{key.monthly_limit}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setEditingItem(key)}
                        className="text-amber-600 hover:text-amber-900"
                      >
                        <Edit3 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteApiKey(key.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create API Key Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-['Cinzel_Decorative'] text-amber-800 mb-4">
              Add New API Key
            </h3>
            <form onSubmit={handleCreateApiKey} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="text"
                  value={newApiKey.api_key}
                  onChange={(e) => setNewApiKey({...newApiKey, api_key: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                  placeholder="AIzaSy..."
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Key Type
                </label>
                <select
                  value={newApiKey.key_type}
                  onChange={(e) => setNewApiKey({...newApiKey, key_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                >
                  <option value="client">Client</option>
                  <option value="company">Company</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Daily Limit
                  </label>
                  <input
                    type="number"
                    value={newApiKey.daily_limit}
                    onChange={(e) => setNewApiKey({...newApiKey, daily_limit: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monthly Limit
                  </label>
                  <input
                    type="number"
                    value={newApiKey.monthly_limit}
                    onChange={(e) => setNewApiKey({...newApiKey, monthly_limit: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={newApiKey.notes}
                  onChange={(e) => setNewApiKey({...newApiKey, notes: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                  rows="3"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
                >
                  Create API Key
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const statusConfig = {
    available: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
    assigned: { color: 'bg-blue-100 text-blue-800', icon: Users },
    expired: { color: 'bg-red-100 text-red-800', icon: XCircle },
    disabled: { color: 'bg-gray-100 text-gray-800', icon: XCircle },
    online: { color: 'bg-green-100 text-green-800', icon: Wifi },
    offline: { color: 'bg-red-100 text-red-800', icon: WifiOff },
    busy: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
    error: { color: 'bg-red-100 text-red-800', icon: AlertTriangle }
  };

  const config = statusConfig[status] || statusConfig.offline;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${config.color}`}>
      <Icon className="h-3 w-3 mr-1" />
      {status}
    </span>
  );
};

// Modems Management Component
const ModemsManagement = ({ modems, modemAssignments, companyConfigs, apiKeys, onRefresh, onDetectModems }) => {
  const [assigningModem, setAssigningModem] = useState(null);
  const [assignmentData, setAssignmentData] = useState({
    company_number: '',
    role_type: 'company_number',
    gemini_api_key_id: ''
  });

  const handleAssignModem = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/api/admin/modems/${assigningModem.id}/assign`, assignmentData);
      setAssigningModem(null);
      setAssignmentData({
        company_number: '',
        role_type: 'company_number',
        gemini_api_key_id: ''
      });
      onRefresh();
    } catch (error) {
      console.error('Failed to assign modem:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-['Cinzel_Decorative'] text-amber-800">
          GSM Modems Management
        </h2>
        <button
          onClick={onDetectModems}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Smartphone className="h-4 w-4" />
          <span>Detect Modems</span>
        </button>
      </div>

      {/* Modems Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modems.map((modem) => (
          <div key={modem.id} className="bg-white rounded-lg border-2 border-amber-200 p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold text-gray-900">{modem.device_name || modem.device_path}</h3>
                <p className="text-sm text-gray-600">{modem.device_path}</p>
              </div>
              <StatusBadge status={modem.status} />
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Phone:</span>
                <span className="font-mono">{modem.phone_number || 'Unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Role:</span>
                <span className={`px-2 py-1 rounded text-xs ${
                  modem.role_type === 'unassigned' 
                    ? 'bg-gray-100 text-gray-800'
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {modem.role_type.replace('_', ' ')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Signal:</span>
                <span>{modem.signal_strength || 0}%</span>
              </div>
              {modem.assigned_to_company && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Company:</span>
                  <span className="font-semibold">{modem.assigned_to_company}</span>
                </div>
              )}
            </div>

            {modem.role_type === 'unassigned' && (
              <button
                onClick={() => setAssigningModem(modem)}
                className="w-full mt-4 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Assign Modem
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Assignment Modal */}
      {assigningModem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-['Cinzel_Decorative'] text-amber-800 mb-4">
              Assign Modem: {assigningModem.device_name}
            </h3>
            <form onSubmit={handleAssignModem} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Number
                </label>
                <input
                  type="text"
                  value={assignmentData.company_number}
                  onChange={(e) => setAssignmentData({...assignmentData, company_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                  placeholder="e.g., 1000 or +1234567890"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role Type
                </label>
                <select
                  value={assignmentData.role_type}
                  onChange={(e) => setAssignmentData({...assignmentData, role_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                >
                  <option value="company_number">Company Number</option>
                  <option value="client_number">Client Number</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Gemini API Key (Optional)
                </label>
                <select
                  value={assignmentData.gemini_api_key_id}
                  onChange={(e) => setAssignmentData({...assignmentData, gemini_api_key_id: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                >
                  <option value="">Select API Key</option>
                  {apiKeys.filter(key => key.status === 'available').map(key => (
                    <option key={key.id} value={key.id}>
                      {key.api_key.substring(0, 20)}... ({key.key_type})
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setAssigningModem(null)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
                >
                  Assign Modem
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Company Configurations Management Component
const CompanyConfigsManagement = ({ configs, apiKeys, modems, onRefresh, showModal, setShowModal, editingItem, setEditingItem }) => {
  const [configData, setConfigData] = useState({
    company_number: '',
    system_prompt: '',
    ai_personality: 'professional',
    gemini_api_key_id: '',
    modem_assignment_id: '',
    voice_settings: {},
    is_active: true
  });

  const [promptTemplates] = useState([
    {
      name: "Professional Customer Service",
      template: "You are a professional customer service AI assistant for {company_number}. Be helpful, polite, and efficient in your responses. Always maintain a professional tone and focus on solving customer problems."
    },
    {
      name: "Technical Support",
      template: "You are a technical support AI specialist for {company_number}. Help users with technical issues, provide clear step-by-step solutions, and ask relevant questions to diagnose problems."
    },
    {
      name: "Sales Assistant",
      template: "You are a sales AI assistant for {company_number}. Be enthusiastic and help customers find the right products or services. Highlight benefits and guide customers through purchasing."
    }
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingItem) {
        await api.put(`/api/admin/company-configs/${editingItem.company_number}`, configData);
      } else {
        await api.post('/api/admin/company-configs', configData);
      }
      setShowModal(false);
      setEditingItem(null);
      setConfigData({
        company_number: '',
        system_prompt: '',
        ai_personality: 'professional',
        gemini_api_key_id: '',
        modem_assignment_id: '',
        voice_settings: {},
        is_active: true
      });
      onRefresh();
    } catch (error) {
      console.error('Failed to save company config:', error);
    }
  };

  const handleEdit = (config) => {
    setConfigData(config);
    setEditingItem(config);
    setShowModal(true);
  };

  const applyTemplate = (template) => {
    setConfigData({
      ...configData,
      system_prompt: template.template.replace('{company_number}', configData.company_number || 'your company')
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-['Cinzel_Decorative'] text-amber-800">
          Company Configurations
        </h2>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>Add Configuration</span>
        </button>
      </div>

      {/* Configurations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {configs.map((config) => (
          <div key={config.id} className="bg-white rounded-lg border-2 border-amber-200 p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Company {config.company_number}
                </h3>
                <p className="text-sm text-gray-600 capitalize">
                  {config.ai_personality} personality
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(config)}
                  className="text-amber-600 hover:text-amber-900"
                >
                  <Edit3 className="h-4 w-4" />
                </button>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  config.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {config.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">System Prompt:</h4>
                <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg line-clamp-3">
                  {config.system_prompt}
                </p>
              </div>

              {config.gemini_api_key_id && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">API Key:</span>
                  <span className="font-mono text-xs">Assigned</span>
                </div>
              )}

              {config.modem_assignment_id && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Modem:</span>
                  <span className="text-green-600">Assigned</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Configuration Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-['Cinzel_Decorative'] text-amber-800 mb-4">
              {editingItem ? 'Edit' : 'Create'} Company Configuration
            </h3>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company Number
                    </label>
                    <input
                      type="text"
                      value={configData.company_number}
                      onChange={(e) => setConfigData({...configData, company_number: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                      placeholder="e.g., 1000 or +1234567890"
                      required
                      disabled={editingItem}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      AI Personality
                    </label>
                    <select
                      value={configData.ai_personality}
                      onChange={(e) => setConfigData({...configData, ai_personality: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                    >
                      <option value="professional">Professional</option>
                      <option value="friendly">Friendly</option>
                      <option value="technical">Technical</option>
                      <option value="sales">Sales</option>
                      <option value="support">Support</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Gemini API Key
                    </label>
                    <select
                      value={configData.gemini_api_key_id}
                      onChange={(e) => setConfigData({...configData, gemini_api_key_id: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                    >
                      <option value="">Select API Key</option>
                      {apiKeys.filter(key => key.status === 'available' || key.id === configData.gemini_api_key_id).map(key => (
                        <option key={key.id} value={key.id}>
                          {key.api_key.substring(0, 20)}... ({key.key_type})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Assigned Modem
                    </label>
                    <select
                      value={configData.modem_assignment_id}
                      onChange={(e) => setConfigData({...configData, modem_assignment_id: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                    >
                      <option value="">Select Modem</option>
                      {modems.filter(modem => modem.role_type === 'unassigned' || modem.id === configData.modem_assignment_id).map(modem => (
                        <option key={modem.id} value={modem.id}>
                          {modem.device_name || modem.device_path} ({modem.phone_number || 'No number'})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_active"
                      checked={configData.is_active}
                      onChange={(e) => setConfigData({...configData, is_active: e.target.checked})}
                      className="h-4 w-4 text-amber-600 focus:ring-amber-500 border-gray-300 rounded"
                    />
                    <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                      Active Configuration
                    </label>
                  </div>
                </div>

                {/* Right Column */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      System Prompt Templates
                    </label>
                    <div className="space-y-2">
                      {promptTemplates.map((template, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => applyTemplate(template)}
                          className="w-full text-left px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                        >
                          {template.name}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      System Prompt
                    </label>
                    <textarea
                      value={configData.system_prompt}
                      onChange={(e) => setConfigData({...configData, system_prompt: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500"
                      rows="8"
                      placeholder="Enter the system prompt for this company number..."
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      This prompt will be used to instruct the AI on how to behave for this company number.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingItem(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
                >
                  {editingItem ? 'Update' : 'Create'} Configuration
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Assignments Overview Component
const AssignmentsOverview = ({ apiAssignments, modemAssignments, onRefresh }) => {
  const handleUnassignApiKey = async (userId) => {
    if (window.confirm('Are you sure you want to unassign this API key?')) {
      try {
        await api.post(`/api/admin/users/${userId}/unassign-api-key`, {
          user_id: userId,
          return_to_pool: true
        });
        onRefresh();
      } catch (error) {
        console.error('Failed to unassign API key:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-['Cinzel_Decorative'] text-amber-800">
        Assignments Overview
      </h2>

      {/* API Key Assignments */}
      <div className="bg-white rounded-lg border-2 border-amber-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          API Key Assignments
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-amber-100">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-amber-800 uppercase">
                  User Email
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-amber-800 uppercase">
                  Company Number
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-amber-800 uppercase">
                  API Key
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-amber-800 uppercase">
                  Subscription
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-amber-800 uppercase">
                  Usage
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-amber-800 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-amber-200">
              {apiAssignments.map((assignment) => (
                <tr key={assignment.id} className="hover:bg-amber-50">
                  <td className="px-4 py-2 text-sm text-gray-900">
                    {assignment.email}
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-900">
                    {assignment.company_number || 'N/A'}
                  </td>
                  <td className="px-4 py-2 text-sm font-mono text-gray-900">
                    {assignment.api_key.substring(0, 15)}...
                  </td>
                  <td className="px-4 py-2 text-sm">
                    <div className="flex flex-col">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        assignment.subscription_status === 'active' 
                          ? 'bg-green-100 text-green-800'
                          : assignment.subscription_status === 'expiring_soon'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {assignment.subscription_status}
                      </span>
                      <span className="text-xs text-gray-500 mt-1">
                        Until {new Date(assignment.subscription_end).toLocaleDateString()}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-2 text-sm text-gray-900">
                    {assignment.usage_count}/{assignment.monthly_limit}
                  </td>
                  <td className="px-4 py-2 text-sm">
                    <button
                      onClick={() => handleUnassignApiKey(assignment.user_id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <XCircle className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modem Assignments */}
      <div className="bg-white rounded-lg border-2 border-amber-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Modem Assignments
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modemAssignments.map((assignment) => (
            <div key={assignment.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900">
                  {assignment.device_name || assignment.device_path}
                </h4>
                <StatusBadge status={assignment.status} />
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <div>Phone: {assignment.phone_number || 'Unknown'}</div>
                <div>Company: {assignment.assigned_to_company || 'Unassigned'}</div>
                <div>Role: {assignment.role_type.replace('_', ' ')}</div>
                {assignment.signal_strength && (
                  <div>Signal: {assignment.signal_strength}%</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;