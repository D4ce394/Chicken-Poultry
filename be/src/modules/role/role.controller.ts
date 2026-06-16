import { Request, Response, RequestHandler } from 'express'; 
import { RoleModel } from '@/database/models/role.model';

// Create Role
export const createRole: RequestHandler = async (req, res) => {
  try {
    const { name, description, permissions } = req.body;
    const role = await RoleModel.create({ name, description, permissions });
    res.status(201).json({ message: 'Role created', data: role }); 
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to create role', error }); 
  }
};

// Get All Roles
export const getAllRoles: RequestHandler = async (req, res) => {
  try {
    const roles = await RoleModel.findAll();
    res.status(200).json({ message: 'Roles fetched', data: roles }); 
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to fetch roles', error }); 
  }
};

// Update Role
export const updateRole: RequestHandler = async (req, res) => {
  try {
    const { id } = req.params;
    const { name, description, permissions } = req.body;

    const role = await RoleModel.findByPk(id);
    if (!role) {
      res.status(404).json({ message: 'Role not found' }); 
      return; 
    }

    role.name = name || role.name;
    role.description = description || role.description;
    role.permissions = permissions || role.permissions;

    await role.save();

    res.status(200).json({ message: 'Role updated', data: role }); 
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to update role', error }); 
  }
};

// Delete Role
export const deleteRole: RequestHandler = async (req, res) => {
  try {
    const { id } = req.params;

    const role = await RoleModel.findByPk(id);
    if (!role) {
      res.status(404).json({ message: 'Role not found' }); 
      return; 
    }

    await role.destroy();
    res.status(200).json({ message: 'Role deleted' }); 
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to delete role', error }); 
  }
};
