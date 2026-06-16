import {
    signUpService,
    signInService,
} from '@modules/auth/auth.service';
import { CustomError } from '@utils/custom-error';
import repo from '@modules/auth/auth.repo';
import { User, UserCreationData } from '@/interfaces/user.interfaces';
import { DB } from '@database/index';
import { hash } from 'bcrypt';
import { validateSignUp, validateSignIn } from '@modules/auth/auth.validator';
import { generateJWT } from '@/middlewares/jwt.service';

jest.mock('../../../src/modules/auth/auth.repo');
jest.mock('../../../src/database', () => ({
    DB: {
        sequelize: {
            close: jest.fn(),
            authenticate: jest.fn(),
        },
    },
}));

jest.mock('bcrypt', () => ({
    hash: jest.fn(() => Promise.resolve('hashedPassword')),
    compareSync: jest.fn(() => true),
}));

jest.mock('../../../src/modules/auth/auth.validator', () => ({
    validateSignUp: jest.fn(),
    validateSignIn: jest.fn(() => ({ error: null })),
}));

jest.mock('../../../src/middlewares/jwt.service');

afterAll(async () => {
    await DB.sequelize.close();
});


describe('signUpService', () => {
    it('should throw error if email already exists', async () => {
        const userData: UserCreationData = {
            email: 'existing@example.com',
            name: 'Existing User',
            username: 'existinguser',
            password: 'Password123!',
        };

        (repo.findUserByEmail as jest.Mock).mockResolvedValue({
            id: '1',
            email: 'existing@example.com',
            name: null,
            username: null,
            password: '',
            isApproved: false,
            created_at: new Date(),
            updated_at: new Date(),
        });

        (validateSignUp as jest.Mock).mockReturnValue({ error: null });

        await expect(signUpService(userData)).rejects.toThrow(`Email ${userData.email} already exists`);
    });

    it('should throw error if validation fails', async () => {
        const userData: UserCreationData = {
            email: 'invalid-email',
            name: 'Invalid User',
            username: 'invaliduser',
            password: 'Password123!',
        };

        (validateSignUp as jest.Mock).mockReturnValue({
            error: { details: [{ message: 'Email format is invalid' }] },
        });

        await expect(signUpService(userData)).rejects.toThrow('Email format is invalid');
    });

    it('should create new user if email is available', async () => {
        const userData: UserCreationData = {
            email: 'new@example.com',
            name: 'New User',
            username: 'newuser',
            password: 'Password123!',
        };

        (repo.findUserByEmail as jest.Mock).mockResolvedValue(null);
        (validateSignUp as jest.Mock).mockReturnValue({ error: null });

        const newUser: User = {
            id: '1',
            email: 'new@example.com',
            name: 'New User',
            username: 'newuser',
            password: 'hashedPassword',
            isApproved: false,
            created_at: new Date(),
            updated_at: new Date(),
        };

        (repo.createUser as jest.Mock).mockResolvedValue(newUser);

        const result = await signUpService(userData);
        expect(result).toEqual({ user: newUser });
        expect(hash).toHaveBeenCalledWith(userData.password, 10);
    });
});

// signInService tests
describe('signInService', () => {
    const mockUser: User = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        username: 'testuser',
        password: 'hashed_password',
        isApproved: false,
        created_at: new Date(),
        updated_at: new Date(),
    };

    it('should return user and accessToken if credentials are correct', async () => {
        (repo.findUserByEmail as jest.Mock).mockResolvedValue(mockUser);
        (generateJWT as jest.Mock).mockResolvedValue('mocked_access_token');
        jest.spyOn(require('bcrypt'), 'compareSync').mockReturnValue(true);

        const userData: UserCreationData = {
            email: 'test@example.com',
            password: 'correct_password',
            name: 'Test User',
            username: 'testuser',
        };

        const result = await signInService(userData);
        expect(repo.findUserByEmail).toHaveBeenCalledWith('test@example.com');
        expect(result).toEqual({ user: mockUser, accessToken: 'mocked_access_token' });
    });

    it('should throw 401 error if user is not found', async () => {
        (repo.findUserByEmail as jest.Mock).mockResolvedValue(null);

        const userData: UserCreationData = {
            email: 'test@example.com',
            password: 'wrong_password',
            name: 'Test User',
            username: 'testuser',
        };

        await expect(signInService(userData)).rejects.toThrow('Email or password is invalid');
    });

    it('should throw 401 error if password is incorrect', async () => {
        (repo.findUserByEmail as jest.Mock).mockResolvedValue(mockUser);
        jest.spyOn(require('bcrypt'), 'compareSync').mockReturnValue(false);

        const userData: UserCreationData = {
            email: 'test@example.com',
            password: 'wrong_password',
            name: 'Test User',
            username: 'testuser',
        };

        await expect(signInService(userData)).rejects.toThrow('Email or password is invalid');
    });

    it('should throw 400 error if validation fails', async () => {
        (validateSignIn as jest.Mock).mockReturnValue({
            error: { details: [{ message: 'Email and password are required' }] },
        });

        const userData: UserCreationData = {
            email: '',
            password: '',
            name: '',
            username: '',
        };

        await expect(signInService(userData)).rejects.toThrow('Email and password are required');
    });
});
