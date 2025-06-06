import React, { useState, useCallback, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import Layout from '../components/Layout'
import { workflowsAPI } from '../services/api'
import { useSound } from '../hooks/useSound'
import { useTranslation, LanguageSelector } from '../hooks/useTranslation'
import toast from 'react-hot-toast'
import {
  Save,
  Play,
  Pause,
  Plus,
  Trash2,
  Settings,
  Zap,
  MessageSquare,
  Phone,
  CreditCard,
  Send,
  X,
  Check,
  Edit3
} from 'lucide-react'

const InvocationEditorPage = () => {
  const { playPaperSlide, playPenScratch, playBookClose, playPaperUnfold } = useSound()
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  
  // State management
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [canvasNodes, setCanvasNodes] = useState([])
  const [canvasConnections, setCanvasConnections] = useState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false)
  const [draggedInvocation, setDraggedInvocation] = useState(null)
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectionStart, setConnectionStart] = useState(null)
  const [workflowName, setWorkflowName] = useState('')
  const [isNewWorkflow, setIsNewWorkflow] = useState(true)

  // Canvas refs
  const canvasRef = useRef(null)
  const svgRef = useRef(null)

  // Fetch workflows
  const { data: workflows, isLoading } = useQuery('workflows', workflowsAPI.getWorkflows)

  // Save workflow mutation
  const saveWorkflowMutation = useMutation(
    (workflowData) => {
      if (isNewWorkflow) {
        return workflowsAPI.createWorkflow(workflowData)
      } else {
        return workflowsAPI.updateWorkflow(selectedWorkflow.id, workflowData)
      }
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('workflows')
        toast.success('Workflow saved successfully')
        playBookClose()
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to save workflow')
      }
    }
  )

  // Invocation types - The Book of Invocations
  const invocationTypes = [
    {
      id: 'payment_ritual',
      name: 'The Payment Ritual',
      description: 'Complex payment flow with SMS confirmation',
      icon: CreditCard,
      color: 'coffee-sienna',
      category: 'Financial'
    },
    {
      id: 'send_sms',
      name: 'The Messenger',
      description: 'Send SMS messages',
      icon: MessageSquare,
      color: 'coffee-brown',
      category: 'Communication'
    },
    {
      id: 'telegram_send',
      name: 'The Telegram Channeler',
      description: 'Send Telegram messages',
      icon: Send,
      color: 'coffee-blue',
      category: 'Communication'
    },
    {
      id: 'hang_up',
      name: 'The Final Word',
      description: 'Terminate voice call',
      icon: Phone,
      color: 'red-600',
      category: 'Voice'
    },
    {
      id: 'ai_response',
      name: "The Scribe's Reply",
      description: 'Get AI conversational response',
      icon: Zap,
      color: 'coffee-green',
      category: 'Intelligence'
    }
  ]

  // Load workflow
  const loadWorkflow = useCallback((workflow) => {
    setSelectedWorkflow(workflow)
    setWorkflowName(workflow.name)
    setIsNewWorkflow(false)
    
    const workflowData = workflow.workflow_data || {}
    setCanvasNodes(workflowData.nodes || [])
    setCanvasConnections(workflowData.connections || [])
    
    playPaperUnfold()
  }, [playPaperUnfold])

  // Create new workflow
  const createNewWorkflow = useCallback(() => {
    setSelectedWorkflow(null)
    setWorkflowName('New Workflow')
    setIsNewWorkflow(true)
    setCanvasNodes([])
    setCanvasConnections([])
    setSelectedNode(null)
    
    playPaperSlide()
  }, [playPaperSlide])

  // Handle drag start from invocation palette
  const handleInvocationDragStart = (invocation) => {
    setDraggedInvocation(invocation)
    playPaperSlide()
  }

  // Handle drop on canvas
  const handleCanvasDrop = useCallback((e) => {
    e.preventDefault()
    
    if (!draggedInvocation) return
    
    const canvasRect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - canvasRect.left
    const y = e.clientY - canvasRect.top
    
    const newNode = {
      id: `node_${Date.now()}`,
      type: draggedInvocation.id,
      name: draggedInvocation.name,
      x: x - 75, // Center the node
      y: y - 40,
      config: {
        spark: '',
        working: '',
        consequence: '',
        next_stitch: ''
      }
    }
    
    setCanvasNodes(prev => [...prev, newNode])
    setDraggedInvocation(null)
    playPenScratch()
  }, [draggedInvocation, playPenScratch])

  // Handle node selection
  const handleNodeClick = (node) => {
    setSelectedNode(node)
    setIsConfigModalOpen(true)
    playPaperUnfold()
  }

  // Handle node configuration save
  const handleConfigSave = (config) => {
    if (!selectedNode) return
    
    setCanvasNodes(prev => 
      prev.map(node => 
        node.id === selectedNode.id 
          ? { ...node, config }
          : node
      )
    )
    
    setIsConfigModalOpen(false)
    setSelectedNode(null)
    toast.success('Node configuration saved')
  }

  // Handle connection creation
  const handleConnectionStart = (nodeId) => {
    if (isConnecting) {
      // Complete connection
      if (connectionStart && connectionStart !== nodeId) {
        const newConnection = {
          id: `conn_${Date.now()}`,
          from: connectionStart,
          to: nodeId
        }
        
        setCanvasConnections(prev => [...prev, newConnection])
        playPenScratch()
      }
      
      setIsConnecting(false)
      setConnectionStart(null)
    } else {
      // Start connection
      setIsConnecting(true)
      setConnectionStart(nodeId)
    }
  }

  // Save workflow
  const handleSaveWorkflow = () => {
    if (!workflowName.trim()) {
      toast.error('Please enter a workflow name')
      return
    }

    const workflowData = {
      name: workflowName,
      workflow_data: {
        nodes: canvasNodes,
        connections: canvasConnections
      }
    }

    saveWorkflowMutation.mutate(workflowData)
  }

  // Delete node
  const handleDeleteNode = (nodeId) => {
    setCanvasNodes(prev => prev.filter(node => node.id !== nodeId))
    setCanvasConnections(prev => 
      prev.filter(conn => conn.from !== nodeId && conn.to !== nodeId)
    )
  }

  // Get invocation by type
  const getInvocationType = (type) => {
    return invocationTypes.find(inv => inv.id === type)
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="loading-quill mb-4"></div>
            <p className="text-coffee-brown">The Scribe is preparing the canvas...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-coffee-khaki border-b-2 border-coffee-sienna">
          <div className="flex items-center space-x-4">
            <LanguageSelector />
            <h1 className="heading-primary text-xl">{t('invocationEditor', 'title')}</h1>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="input-paper px-3 py-1 text-lg font-medium"
              placeholder={t('invocationEditor', 'workflowNamePlaceholder')}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={createNewWorkflow}
              className="btn-secondary flex items-center space-x-2"
            >
              <Plus size={16} />
              <span>{t('invocationEditor', 'new')}</span>
            </button>
            
            <button
              onClick={handleSaveWorkflow}
              disabled={saveWorkflowMutation.isLoading}
              className="btn-primary flex items-center space-x-2"
            >
              {saveWorkflowMutation.isLoading ? (
                <div className="loading-quill w-4 h-4"></div>
              ) : (
                <Save size={16} />
              )}
              <span>{t('invocationEditor', 'save')}</span>
            </button>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Workflow List Sidebar */}
          <div className="w-64 bg-coffee-beige border-r-2 border-coffee-tan p-4 overflow-y-auto">
            <h2 className="heading-secondary text-lg mb-4">Saved Workflows</h2>
            <div className="space-y-2">
              {workflows?.map(workflow => (
                <div
                  key={workflow.id}
                  onClick={() => loadWorkflow(workflow)}
                  className={`p-3 rounded cursor-pointer transition-colors ${
                    selectedWorkflow?.id === workflow.id
                      ? 'bg-coffee-tan border-2 border-coffee-sienna'
                      : 'bg-coffee-khaki hover:bg-coffee-tan border border-coffee-tan'
                  }`}
                >
                  <h3 className="font-medium text-coffee-brown">{workflow.name}</h3>
                  <p className="text-sm text-coffee-sienna">
                    {workflow.is_active ? 'Active' : 'Inactive'}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Main Editor Area */}
          <div className="flex flex-1">
            {/* Canvas */}
            <div className="flex-1 relative">
              <div
                ref={canvasRef}
                className="canvas-paper w-full h-full relative overflow-hidden"
                onDrop={handleCanvasDrop}
                onDragOver={(e) => e.preventDefault()}
              >
                {/* SVG for connections */}
                <svg
                  ref={svgRef}
                  className="absolute inset-0 w-full h-full pointer-events-none"
                  style={{ zIndex: 1 }}
                >
                  {canvasConnections.map(connection => {
                    const fromNode = canvasNodes.find(n => n.id === connection.from)
                    const toNode = canvasNodes.find(n => n.id === connection.to)
                    
                    if (!fromNode || !toNode) return null
                    
                    const fromX = fromNode.x + 150
                    const fromY = fromNode.y + 40
                    const toX = toNode.x
                    const toY = toNode.y + 40
                    
                    return (
                      <line
                        key={connection.id}
                        x1={fromX}
                        y1={fromY}
                        x2={toX}
                        y2={toY}
                        className="logic-thread"
                      />
                    )
                  })}
                </svg>

                {/* Nodes */}
                {canvasNodes.map(node => {
                  const invocationType = getInvocationType(node.type)
                  const Icon = invocationType?.icon || Zap
                  
                  return (
                    <div
                      key={node.id}
                      className="invocation-node absolute"
                      style={{ 
                        left: node.x, 
                        top: node.y,
                        zIndex: 2
                      }}
                      onClick={() => handleNodeClick(node)}
                    >
                      <div className="flex items-center space-x-2 mb-2">
                        <Icon size={20} className={`text-${invocationType?.color || 'coffee-brown'}`} />
                        <h3 className="font-medium text-coffee-brown text-sm">{node.name}</h3>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleConnectionStart(node.id)
                          }}
                          className={`p-1 rounded text-xs ${
                            isConnecting && connectionStart === node.id
                              ? 'bg-coffee-sienna text-coffee-beige'
                              : 'bg-coffee-tan text-coffee-brown hover:bg-coffee-sienna hover:text-coffee-beige'
                          }`}
                        >
                          {isConnecting && connectionStart === node.id ? 'Click target' : 'Connect'}
                        </button>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteNode(node.id)
                          }}
                          className="p-1 rounded text-xs bg-red-100 text-red-600 hover:bg-red-200"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  )
                })}

                {/* Canvas instructions */}
                {canvasNodes.length === 0 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-coffee-sienna">
                      <Edit3 size={48} className="mx-auto mb-4 opacity-50" />
                      <p className="text-lg font-medium">Drag Invocations from the palette</p>
                      <p className="text-sm">to begin crafting your Scribe's behavior</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Invocation Palette */}
            <div className="w-80 bg-coffee-beige border-l-2 border-coffee-tan p-4 overflow-y-auto">
              <h2 className="heading-secondary text-lg mb-4">Book of Invocations</h2>
              
              <div className="space-y-3">
                {invocationTypes.map(invocation => {
                  const Icon = invocation.icon
                  
                  return (
                    <div
                      key={invocation.id}
                      draggable
                      onDragStart={() => handleInvocationDragStart(invocation)}
                      className="p-4 bg-coffee-khaki border-2 border-coffee-tan rounded-lg cursor-move hover:border-coffee-sienna transition-colors"
                    >
                      <div className="flex items-center space-x-3 mb-2">
                        <Icon size={24} className={`text-${invocation.color}`} />
                        <div>
                          <h3 className="font-medium text-coffee-brown">{invocation.name}</h3>
                          <p className="text-xs text-coffee-sienna">{invocation.category}</p>
                        </div>
                      </div>
                      <p className="text-sm text-coffee-brown">{invocation.description}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Configuration Modal */}
        {isConfigModalOpen && selectedNode && (
          <ConfigurationModal
            node={selectedNode}
            onSave={handleConfigSave}
            onClose={() => {
              setIsConfigModalOpen(false)
              setSelectedNode(null)
            }}
          />
        )}
      </div>
    </Layout>
  )
}

// Configuration Modal Component
const ConfigurationModal = ({ node, onSave, onClose }) => {
  const [config, setConfig] = useState(node.config || {})
  const invocationType = node.type

  const handleSave = () => {
    onSave(config)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="modal-scroll max-w-2xl w-full mx-4 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="heading-secondary">Configuration Scroll</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-coffee-tan rounded-full"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-6">
          {/* The Spark */}
          <div>
            <label className="block text-coffee-brown font-medium mb-2">
              The Spark (Origin/Trigger)
            </label>
            <textarea
              value={config.spark || ''}
              onChange={(e) => setConfig(prev => ({ ...prev, spark: e.target.value }))}
              className="input-paper w-full h-20 resize-none"
              placeholder="What event or condition initiates this node?"
            />
          </div>

          {/* The Working */}
          <div>
            <label className="block text-coffee-brown font-medium mb-2">
              The Working (What Happens)
            </label>
            <textarea
              value={config.working || ''}
              onChange={(e) => setConfig(prev => ({ ...prev, working: e.target.value }))}
              className="input-paper w-full h-20 resize-none"
              placeholder="What action does this node perform?"
            />
          </div>

          {/* Invocation-specific fields */}
          {invocationType === 'payment_ritual' && (
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                Bank Card Number
              </label>
              <input
                type="text"
                value={config.bank_card || ''}
                onChange={(e) => setConfig(prev => ({ ...prev, bank_card: e.target.value }))}
                className="input-paper w-full"
                placeholder="Client's bank card number"
              />
              
              <label className="block text-coffee-brown font-medium mb-2 mt-4">
                Reassurance Script
              </label>
              <textarea
                value={config.reassurance_script || ''}
                onChange={(e) => setConfig(prev => ({ ...prev, reassurance_script: e.target.value }))}
                className="input-paper w-full h-20 resize-none"
                placeholder="Script to reassure skeptical users"
              />
            </div>
          )}

          {invocationType === 'send_sms' && (
            <div>
              <label className="block text-coffee-brown font-medium mb-2">
                Recipient Phone Number
              </label>
              <input
                type="text"
                value={config.recipient || ''}
                onChange={(e) => setConfig(prev => ({ ...prev, recipient: e.target.value }))}
                className="input-paper w-full"
                placeholder="Phone number or dynamic variable"
              />
              
              <label className="block text-coffee-brown font-medium mb-2 mt-4">
                Message Content
              </label>
              <textarea
                value={config.message || ''}
                onChange={(e) => setConfig(prev => ({ ...prev, message: e.target.value }))}
                className="input-paper w-full h-20 resize-none"
                placeholder="SMS message content"
              />
            </div>
          )}

          {/* The Consequence */}
          <div>
            <label className="block text-coffee-brown font-medium mb-2">
              The Consequence (Outcome)
            </label>
            <textarea
              value={config.consequence || ''}
              onChange={(e) => setConfig(prev => ({ ...prev, consequence: e.target.value }))}
              className="input-paper w-full h-20 resize-none"
              placeholder="What is the immediate result of this action?"
            />
          </div>

          {/* The Next Stitch */}
          <div>
            <label className="block text-coffee-brown font-medium mb-2">
              The Next Stitch (What Should Happen Next)
            </label>
            <textarea
              value={config.next_stitch || ''}
              onChange={(e) => setConfig(prev => ({ ...prev, next_stitch: e.target.value }))}
              className="input-paper w-full h-20 resize-none"
              placeholder="Which connected nodes should be activated?"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-4 mt-8">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} className="btn-primary flex items-center space-x-2">
            <Check size={16} />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default InvocationEditorPage