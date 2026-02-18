import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import { authApi } from '../lib/api'

interface AuthContextType {
  token: string | null
  /** Autentica e retorna o token; NÃO persiste até o usuário confirmar entrada. */
  login: (email: string, senha: string) => Promise<string>
  /** Persiste o token e considera o usuário "dentro" do sistema (uso após confirmação). */
  confirmarEntrada: (token: string) => void
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  }, [token])

  const login = async (email: string, senha: string): Promise<string> => {
    const { data } = await authApi.login(email, senha)
    return data.access_token
  }

  const confirmarEntrada = (newToken: string) => {
    setToken(newToken)
  }

  const logout = () => setToken(null)

  return (
    <AuthContext.Provider
      value={{
        token,
        login,
        confirmarEntrada,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
