import { api } from '$lib/axios';
import type { SignUpPayload } from './types';

export const signUpApi = async (data: SignUpPayload) => {
	const response = await api.post('/auth/register', data);
	return response.data;
};
