"""
Workflows router
The Invocation Editor's Interface
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from database.connection import get_database
from models.user import User
from models.workflow import ScribeWorkflow
from routers.auth import get_current_user

router = APIRouter()

class WorkflowCreate(BaseModel):
    name: str
    workflow_data: Dict[str, Any]

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    workflow_data: Dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str

@router.get("/", response_model=List[WorkflowResponse])
async def get_user_workflows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get user's workflows
    The Scribe's Saved Scripts
    """
    try:
        result = await db.execute(
            select(ScribeWorkflow).where(
                ScribeWorkflow.user_id == current_user.id
            ).order_by(ScribeWorkflow.updated_at.desc())
        )
        workflows = result.scalars().all()
        
        return [
            WorkflowResponse(
                id=workflow.id,
                name=workflow.name,
                workflow_data=workflow.workflow_data,
                is_active=workflow.is_active,
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat()
            )
            for workflow in workflows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get workflows")

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Create new workflow
    The Scribe's New Script
    """
    try:
        # Validate workflow data structure
        if not isinstance(workflow_data.workflow_data, dict):
            raise HTTPException(status_code=400, detail="Invalid workflow data format")
        
        # Check for required workflow components
        required_keys = ["nodes", "connections"]
        if not all(key in workflow_data.workflow_data for key in required_keys):
            raise HTTPException(status_code=400, detail="Workflow must contain nodes and connections")
        
        # Create workflow
        new_workflow = ScribeWorkflow(
            user_id=current_user.id,
            name=workflow_data.name,
            workflow_data=workflow_data.workflow_data,
            is_active=True
        )
        
        db.add(new_workflow)
        await db.commit()
        await db.refresh(new_workflow)
        
        return WorkflowResponse(
            id=new_workflow.id,
            name=new_workflow.name,
            workflow_data=new_workflow.workflow_data,
            is_active=new_workflow.is_active,
            created_at=new_workflow.created_at.isoformat(),
            updated_at=new_workflow.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create workflow")

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get specific workflow
    The Scribe's Script Details
    """
    try:
        result = await db.execute(
            select(ScribeWorkflow).where(
                ScribeWorkflow.id == workflow_id,
                ScribeWorkflow.user_id == current_user.id
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            workflow_data=workflow.workflow_data,
            is_active=workflow.is_active,
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get workflow")

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Update workflow
    The Scribe's Script Revision
    """
    try:
        # Get existing workflow
        result = await db.execute(
            select(ScribeWorkflow).where(
                ScribeWorkflow.id == workflow_id,
                ScribeWorkflow.user_id == current_user.id
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update fields
        update_data = {}
        if workflow_update.name is not None:
            update_data["name"] = workflow_update.name
        if workflow_update.workflow_data is not None:
            # Validate workflow data
            if not isinstance(workflow_update.workflow_data, dict):
                raise HTTPException(status_code=400, detail="Invalid workflow data format")
            update_data["workflow_data"] = workflow_update.workflow_data
        if workflow_update.is_active is not None:
            update_data["is_active"] = workflow_update.is_active
        
        if update_data:
            await db.execute(
                update(ScribeWorkflow).where(
                    ScribeWorkflow.id == workflow_id
                ).values(**update_data)
            )
            await db.commit()
            
            # Refresh workflow
            await db.refresh(workflow)
        
        return WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            workflow_data=workflow.workflow_data,
            is_active=workflow.is_active,
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update workflow")

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Delete workflow
    The Scribe's Script Removal
    """
    try:
        # Check if workflow exists and belongs to user
        result = await db.execute(
            select(ScribeWorkflow).where(
                ScribeWorkflow.id == workflow_id,
                ScribeWorkflow.user_id == current_user.id
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Delete workflow
        await db.execute(
            delete(ScribeWorkflow).where(ScribeWorkflow.id == workflow_id)
        )
        await db.commit()
        
        return {"message": "Workflow deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete workflow")

@router.get("/{workflow_id}/validate")
async def validate_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Validate workflow structure
    The Scribe's Script Verification
    """
    try:
        result = await db.execute(
            select(ScribeWorkflow).where(
                ScribeWorkflow.id == workflow_id,
                ScribeWorkflow.user_id == current_user.id
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Validate workflow structure
        validation_result = _validate_workflow_structure(workflow.workflow_data)
        
        return {
            "is_valid": validation_result["is_valid"],
            "errors": validation_result["errors"],
            "warnings": validation_result["warnings"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to validate workflow")

def _validate_workflow_structure(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate workflow structure and logic
    """
    errors = []
    warnings = []
    
    try:
        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", [])
        
        # Check for required components
        if not nodes:
            errors.append("Workflow must contain at least one node")
        
        # Validate nodes
        node_ids = set()
        for node in nodes:
            if "id" not in node:
                errors.append("All nodes must have an ID")
                continue
            
            node_id = node["id"]
            if node_id in node_ids:
                errors.append(f"Duplicate node ID: {node_id}")
            node_ids.add(node_id)
            
            if "type" not in node:
                errors.append(f"Node {node_id} missing type")
            
            if "config" not in node:
                warnings.append(f"Node {node_id} has no configuration")
        
        # Validate connections
        for connection in connections:
            if "from" not in connection or "to" not in connection:
                errors.append("All connections must have 'from' and 'to' fields")
                continue
            
            from_id = connection["from"]
            to_id = connection["to"]
            
            if from_id not in node_ids:
                errors.append(f"Connection references non-existent node: {from_id}")
            
            if to_id not in node_ids:
                errors.append(f"Connection references non-existent node: {to_id}")
        
        # Check for orphaned nodes (no connections)
        connected_nodes = set()
        for connection in connections:
            connected_nodes.add(connection["from"])
            connected_nodes.add(connection["to"])
        
        orphaned_nodes = node_ids - connected_nodes
        if len(orphaned_nodes) > 1:  # Allow one starting node
            warnings.append(f"Orphaned nodes detected: {list(orphaned_nodes)}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [f"Validation error: {str(e)}"],
            "warnings": []
        }