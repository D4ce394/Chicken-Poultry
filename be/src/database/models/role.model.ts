import { Role } from '@/interfaces/role.interfaces';
import { Sequelize, DataTypes, Model, Optional } from 'sequelize';

export type RoleCreationAttributes = Optional<Role, 'id' | 'created_at' | 'updated_at'>;

export class RoleModel extends Model<Role, RoleCreationAttributes> implements Role {
  public id!: number;
  public name!: string;
  public description!: string;
  public permissions!: string[]; 
  public created_at!: Date;
  public updated_at!: Date;
}

export default function (sequelize: Sequelize): typeof RoleModel {
  RoleModel.init(
    {
      id: {
        type: DataTypes.UUID,
        allowNull: false,
        primaryKey: true,
        defaultValue: DataTypes.UUIDV4,
        autoIncrement: true
      },
      name: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true,
      },
      description: {
        type: DataTypes.STRING,
        allowNull: false,
      },
      permissions: {
        type: DataTypes.ARRAY(DataTypes.STRING),
        allowNull: false,
        defaultValue: [], 
      },      
      
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW,
      },
      updated_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW,
      },
    },
    {
      sequelize,
      tableName: 'roles',
      timestamps: true,
      createdAt: 'created_at',
      updatedAt: 'updated_at',
    }
  );

  return RoleModel;
  
}
