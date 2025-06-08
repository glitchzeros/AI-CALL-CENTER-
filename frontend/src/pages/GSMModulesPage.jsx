import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { 
  Smartphone, 
  Plus, 
  Edit, 
  Trash2, 
  Wifi, 
  WifiOff, 
  CreditCard,
  RefreshCw,
  Eye,
  EyeOff
} from 'lucide-react'
import toast from 'react-hot-toast'
import { gsmModulesAPI } from '../services/api'

const GSMModulesPage = () => {
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingModule, setEditingModule] = useState(null)
  const [demoCodes, setDemoCodes] = useState([])
  const [showDemoCodes, setShowDemoCodes] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue
  } = useForm()

  useEffect(() => {
    loadModules()
    loadDemoCodes()
  }, [])

  const loadModules = async () => {
    try {
      const response = await gsmModulesAPI.getModules()
      setModules(response.data)
    } catch (error) {
      toast.error('Failed to load GSM modules')
    } finally {
      setLoading(false)
    }
  }

  const loadDemoCodes = async () => {
    try {
      const response = await gsmModulesAPI.getDemoCodes()
      setDemoCodes(response.data.demo_codes)
    } catch (error) {
      console.error('Failed to load demo codes:', error)
    }
  }

  const onSubmit = async (data) => {
    try {
      if (editingModule) {
        await gsmModulesAPI.updateModule(editingModule.id, data)
        toast.success('GSM module updated successfully')
      } else {
        await gsmModulesAPI.createModule(data)
        toast.success('GSM module created successfully')
      }
      
      setShowCreateModal(false)
      setEditingModule(null)
      reset()
      loadModules()
      loadDemoCodes()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save GSM module')
    }
  }

  const handleEdit = (module) => {
    setEditingModule(module)
    setValue('device_id', module.device_id)
    setValue('phone_number', module.phone_number)
    setValue('control_port', module.control_port)
    setValue('audio_port', module.audio_port)
    setValue('bank_card_number', module.bank_card_number)
    setValue('bank_card_holder_name', module.bank_card_holder_name)
    setValue('is_demo_mode', module.is_demo_mode)
    setShowCreateModal(true)
  }

  const handleDelete = async (moduleId) => {
    if (!confirm('Are you sure you want to delete this GSM module?')) return

    try {
      await gsmModulesAPI.deleteModule(moduleId)
      toast.success('GSM module deleted successfully')
      loadModules()
      loadDemoCodes()
    } catch (error) {
      toast.error('Failed to delete GSM module')
    }
  }

  const handleRegenerateDemoCode = async (moduleId) => {
    try {
      const response = await gsmModulesAPI.regenerateDemoCode(moduleId)
      toast.success(`New demo code: ${response.data.new_demo_code}`)
      loadModules()
      loadDemoCodes()
    } catch (error) {
      toast.error('Failed to regenerate demo code')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'text-green-600'
      case 'idle': return 'text-blue-600'
      case 'busy': return 'text-yellow-600'
      case 'offline': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status) => {
    return status === 'offline' ? <WifiOff size={16} /> : <Wifi size={16} />
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-quill w-8 h-8"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="heading-decorative text-3xl">GSM Modules Management</h1>
          <p className="text-coffee-brown mt-2">
            Manage your GSM hardware modules and bank card associations
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowDemoCodes(!showDemoCodes)}
            className="btn-secondary flex items-center space-x-2"
          >
            {showDemoCodes ? <EyeOff size={20} /> : <Eye size={20} />}
            <span>{showDemoCodes ? 'Hide' : 'Show'} Demo Codes</span>
          </button>
          <button
            onClick={() => {
              setEditingModule(null)
              reset()
              setShowCreateModal(true)
            }}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>Add Module</span>
          </button>
        </div>
      </div>

      {/* Demo Codes Panel */}
      {showDemoCodes && demoCodes.length > 0 && (
        <div className="paper-panel">
          <h3 className="text-lg font-semibold text-coffee-brown mb-4">Demo SMS Codes</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {demoCodes.map((demo, index) => (
              <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Smartphone size={16} className="text-yellow-600" />
                  <span className="font-medium text-yellow-800">{demo.phone_number}</span>
                </div>
                <div className="font-mono text-lg font-bold text-yellow-900 mb-2">
                  {demo.demo_code}
                </div>
                {demo.bank_card_number && (
                  <div className="text-sm text-yellow-700">
                    <div className="flex items-center space-x-1">
                      <CreditCard size={12} />
                      <span>{demo.bank_card_number}</span>
                    </div>
                    {demo.bank_card_holder_name && (
                      <div className="text-xs mt-1">{demo.bank_card_holder_name}</div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modules List */}
      <div className="paper-panel">
        <h3 className="text-lg font-semibold text-coffee-brown mb-4">GSM Modules</h3>
        
        {modules.length === 0 ? (
          <div className="text-center py-8">
            <Smartphone size={48} className="mx-auto text-coffee-sienna mb-4" />
            <p className="text-coffee-brown">No GSM modules configured</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary mt-4"
            >
              Add First Module
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-coffee-cream">
                  <th className="text-left py-3 px-4">Device ID</th>
                  <th className="text-left py-3 px-4">Phone Number</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Bank Card</th>
                  <th className="text-left py-3 px-4">Mode</th>
                  <th className="text-left py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {modules.map((module) => (
                  <tr key={module.id} className="border-b border-coffee-cream hover:bg-coffee-cream/30">
                    <td className="py-3 px-4 font-mono">{module.device_id}</td>
                    <td className="py-3 px-4">{module.phone_number || 'N/A'}</td>
                    <td className="py-3 px-4">
                      <div className={`flex items-center space-x-2 ${getStatusColor(module.status)}`}>
                        {getStatusIcon(module.status)}
                        <span className="capitalize">{module.status}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {module.bank_card_number ? (
                        <div>
                          <div className="font-mono text-sm">{module.bank_card_number}</div>
                          {module.bank_card_holder_name && (
                            <div className="text-xs text-coffee-sienna">{module.bank_card_holder_name}</div>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400">Not set</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        module.is_demo_mode 
                          ? 'bg-yellow-100 text-yellow-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {module.is_demo_mode ? 'Demo' : 'Real'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleEdit(module)}
                          className="text-coffee-sienna hover:text-coffee-brown"
                          title="Edit module"
                        >
                          <Edit size={16} />
                        </button>
                        {module.is_demo_mode && (
                          <button
                            onClick={() => handleRegenerateDemoCode(module.id)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Regenerate demo code"
                          >
                            <RefreshCw size={16} />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(module.id)}
                          className="text-red-600 hover:text-red-800"
                          title="Delete module"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-coffee-brown mb-4">
              {editingModule ? 'Edit GSM Module' : 'Add GSM Module'}
            </h3>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Device ID *
                </label>
                <input
                  type="text"
                  className="input-paper w-full"
                  placeholder="e.g., SIM800C_001"
                  {...register('device_id', {
                    required: 'Device ID is required'
                  })}
                />
                {errors.device_id && (
                  <p className="text-red-600 text-sm mt-1">{errors.device_id.message}</p>
                )}
              </div>

              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Phone Number *
                </label>
                <input
                  type="text"
                  className="input-paper w-full"
                  placeholder="+998901234567"
                  {...register('phone_number', {
                    required: 'Phone number is required'
                  })}
                />
                {errors.phone_number && (
                  <p className="text-red-600 text-sm mt-1">{errors.phone_number.message}</p>
                )}
              </div>

              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Control Port
                </label>
                <input
                  type="text"
                  className="input-paper w-full"
                  placeholder="/dev/ttyUSB0"
                  {...register('control_port')}
                />
              </div>

              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Audio Port
                </label>
                <input
                  type="text"
                  className="input-paper w-full"
                  placeholder="/dev/ttyUSB1"
                  {...register('audio_port')}
                />
              </div>

              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Bank Card Number
                </label>
                <input
                  type="text"
                  className="input-paper w-full"
                  placeholder="8600 1234 5678 9012"
                  {...register('bank_card_number')}
                />
              </div>

              <div>
                <label className="block text-coffee-brown font-medium mb-2">
                  Bank Card Holder Name
                </label>
                <input
                  type="text"
                  className="input-paper w-full"
                  placeholder="JOHN DOE"
                  {...register('bank_card_holder_name')}
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_demo_mode"
                  className="rounded border-coffee-cream"
                  {...register('is_demo_mode')}
                />
                <label htmlFor="is_demo_mode" className="text-coffee-brown">
                  Demo Mode (generates demo SMS codes)
                </label>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingModule(null)
                    reset()
                  }}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary flex-1"
                >
                  {editingModule ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default GSMModulesPage
