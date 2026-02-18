import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { TextInput, PasswordInput, Button, Alert, Stack, Paper, Title, Text } from '@mantine/core'
import { useAuth } from '../contexts/AuthContext'
import './Auth.css'

export function Login() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [loading, setLoading] = useState(false)
  const [tokenRecebido, setTokenRecebido] = useState<string | null>(null)
  const { login, confirmarEntrada } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? '/'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErro('')
    setLoading(true)
    try {
      const token = await login(email, senha)
      setTokenRecebido(token)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setErro(msg || 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  const handleEntrarNoSistema = () => {
    if (tokenRecebido) {
      confirmarEntrada(tokenRecebido)
      setTokenRecebido(null)
      navigate(from, { replace: true })
    }
  }

  const handleVoltar = () => {
    setTokenRecebido(null)
    setErro('')
  }

  if (tokenRecebido) {
    return (
      <div className="auth-page">
        <Paper className="auth-card" shadow="sm" radius="md" p="lg">
          <Stack gap="md">
            <div className="auth-header">
              <span className="auth-icon">✓</span>
              <Title order={2}>Login realizado</Title>
              <Text size="sm" c="dimmed">
                Deseja entrar no sistema?
              </Text>
            </div>
            <Stack gap="sm">
              <Button onClick={handleEntrarNoSistema} fullWidth size="md">
                Entrar no sistema
              </Button>
              <Button variant="subtle" onClick={handleVoltar} fullWidth size="md">
                Voltar
              </Button>
            </Stack>
          </Stack>
        </Paper>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <Paper className="auth-card" shadow="sm" radius="md" p="lg">
        <Stack gap="md">
          <div className="auth-header">
            <span className="auth-icon">🔐</span>
            <Title order={2}>Entrar</Title>
            <Text size="sm" c="dimmed">Sistema de Gestão Imobiliária</Text>
          </div>
          <form onSubmit={handleSubmit}>
            <Stack gap="md">
              {erro && (
                <Alert color="red" variant="light" title="Erro">
                  {erro}
                </Alert>
              )}
              <TextInput
                label="E-mail"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                size="md"
              />
              <PasswordInput
                label="Senha"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                required
                autoComplete="current-password"
                size="md"
              />
              <Button type="submit" loading={loading} fullWidth size="md">
                {loading ? 'Entrando...' : 'Entrar'}
              </Button>
            </Stack>
          </form>
          <Text size="sm" c="dimmed" ta="center">
            Não tem conta? <Link to="/cadastro">Cadastre-se</Link>
          </Text>
        </Stack>
      </Paper>
    </div>
  )
}
