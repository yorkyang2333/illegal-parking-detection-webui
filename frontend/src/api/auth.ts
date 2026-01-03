import type { LoginRequest, RegisterRequest, AuthResponse, UserResponse } from './types'

const API_BASE = '/api/auth'

/**
 * Login user
 */
export async function loginApi(username: string, password: string, rememberMe: boolean = false): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ username, password, remember_me: rememberMe } as LoginRequest),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || '登录失败')
  }

  return response.json()
}

/**
 * Register new user
 */
export async function registerApi(
  username: string,
  email: string,
  password: string
): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ username, email, password } as RegisterRequest),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || '注册失败')
  }

  return response.json()
}

/**
 * Logout user
 */
export async function logoutApi(): Promise<void> {
  const response = await fetch(`${API_BASE}/logout`, {
    method: 'POST',
    credentials: 'include',
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || '登出失败')
  }
}

/**
 * Get current user info
 */
export async function getMeApi(): Promise<UserResponse> {
  const response = await fetch(`${API_BASE}/me`, {
    method: 'GET',
    credentials: 'include',
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('UNAUTHORIZED')
    }
    const error = await response.json()
    throw new Error(error.error || '获取用户信息失败')
  }

  return response.json()
}

/**
 * Update user profile
 */
export async function updateProfileApi(
  username: string,
  email: string,
  password?: string
): Promise<UserResponse> {
  const body: { username: string; email: string; password?: string } = { username, email }
  if (password) {
    body.password = password
  }

  const response = await fetch(`${API_BASE}/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || '更新失败')
  }

  return response.json()
}

