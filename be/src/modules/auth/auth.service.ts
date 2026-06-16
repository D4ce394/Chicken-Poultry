// src/modules/auth/auth.service.ts
import type { UserCreationData, User } from '@/interfaces/user.interfaces';
import { validateSignIn, validateSignUp } from './auth.validator';
import repo from './auth.repo';
import { compareSync, hash } from 'bcrypt';
import { generateJWT } from '@/middlewares/jwt.service';
import { JWT_ACCESS_TOKEN_SECRET } from '@/config'; 
import { CustomError } from '@/utils/custom-error';

export const signUpService = async (userData: UserCreationData) => {
    const { error } = validateSignUp(userData);
    if (error) {
        throw new CustomError(error.details[0].message, 400);
    }

    const findUser = await repo.findUserByEmail(userData.email);
    if (findUser) {
        throw new CustomError(`Email ${userData.email} already exists`, 409);
    }

    const randomId = (Date.now() + Math.floor(Math.random() * 100)).toString(36);
    const username = `${userData.email.split('@')[0]}-${randomId}`;
    const hashedPassword = await hash(userData.password, 10);

    const newUser = await repo.createUser({
        email: userData.email,
        name: userData.name,
        username,
        password: hashedPassword,
    });

    return { user: newUser };
};

export const signInService = async (userData: UserCreationData) => {
    const { error } = validateSignIn(userData);
    if (error) {
        throw new CustomError(error.details[0].message, 400);
    }

    const user = await repo.findUserByEmail(userData.email);
    if (!user) {
        throw new CustomError('Email or password is invalid', 401);
    }

    const validPassword = compareSync(userData.password, user.password);
    if (!validPassword) {
        throw new CustomError('Email or password is invalid', 401);
    }

    const payload = {
        userId: user.id,
    };

    // Ensure JWT_ACCESS_TOKEN_SECRET is not undefined here
    if (!JWT_ACCESS_TOKEN_SECRET) {
        throw new Error('JWT_ACCESS_TOKEN_SECRET is not configured.');
    }

    const accessToken = await generateJWT(
        payload,
        JWT_ACCESS_TOKEN_SECRET, // Use the imported secret
    );

    return { user, accessToken };
};
