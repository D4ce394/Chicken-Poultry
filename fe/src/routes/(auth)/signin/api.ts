import { api } from '$lib/axios';
import type { SignInPayload } from './types';

export const signInApi = async (data: SignInPayload) => {
	const response = await api.post('/auth/signin', data);

	return response.data;
};
