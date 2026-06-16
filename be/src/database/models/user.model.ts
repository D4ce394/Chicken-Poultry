import { User } from '@/interfaces/user.interfaces';
import { Sequelize, DataTypes, Model, Optional } from 'sequelize';
import { RoleModel } from './role.model';

export type UserCreationAttributes = Optional<User, 'id' | 'username' | 'created_at' | 'updated_at' | 'isApproved' | 'roleId' | 'department' | 'isOnline' | 'lastLogin'>;

export class UserModel
    extends Model<User, UserCreationAttributes>
    implements User
{
    public id!: string;
    public email!: string;
    public name!: string;
    public username!: string | null;
    public password!: string;
    public isApproved!: boolean;
    public created_at!: Date;
    public updated_at!: Date;

    public roleId!: number | null; 
    public department!: string | null; 
    public isOnline!: boolean; 
    public lastLogin!: Date | null;

    public readonly role?: RoleModel; 

    public readonly createdAt!: Date;
    public readonly updatedAt!: Date;
}

export default function (sequelize: Sequelize): typeof UserModel {
    UserModel.init(
        {
            id: {
                primaryKey: true,
                type: DataTypes.UUID,
                defaultValue: DataTypes.UUIDV4,
            },
            email: {
                allowNull: false,
                type: DataTypes.STRING,
                unique: true,
            },
            name: {
                allowNull: false,
                type: DataTypes.STRING,
            },
            username: {
                allowNull: true,
                type: DataTypes.STRING,
                unique: true,
            },
            password: {
                allowNull: false,
                type: DataTypes.STRING(255),
            },
            isApproved: {
                type: DataTypes.BOOLEAN,
                field: 'is_approved',
                allowNull: false,
                defaultValue: false,
            },
            roleId: {
                type: DataTypes.INTEGER,
                allowNull: true,
                references: {
                    model: 'Roles',
                    key: 'id',
                },
                onUpdate: 'CASCADE',
                onDelete: 'SET NULL',
            },
            department: {
                type: DataTypes.STRING,
                allowNull: true, 
            },
            isOnline: {
                type: DataTypes.BOOLEAN,
                field: 'is_online', 
                allowNull: false,
                defaultValue: false,
            },
            lastLogin: {
                type: DataTypes.DATE,
                field: 'last_login', 
                allowNull: true,
            },
            created_at: DataTypes.DATE,
            updated_at: DataTypes.DATE,
        },
        {
            tableName: 'users',
            sequelize,
            createdAt: 'created_at',
            updatedAt: 'updated_at',
            timestamps: true,
        },
    );

    return UserModel;
}
