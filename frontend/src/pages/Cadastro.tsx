import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  TextInput,
  PasswordInput,
  Button,
  Alert,
  Stack,
  Paper,
  Title,
  Text,
} from '@mantine/core'
import { authApi } from '../lib/api'
import './Cadastro.css'

export function Cadastro() {
  const [form, setForm] = useState({
    nome: '',
    email: '',
    senha: '',
    cpf: '',
    rg: '',
    data_de_nascimento: '',
    servico: '',
  })
  const [erro, setErro] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErro('')
    setLoading(true)
    try {
      await authApi.cadastro(form)
      navigate('/login')
    } catch (err: unknown) {
      const res = err as { response?: { data?: { detail?: string | string[] } } }
      const detail = res?.response?.data?.detail
      const msg = Array.isArray(detail) ? detail.join(', ') : detail
      setErro(msg || 'Erro ao cadastrar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="cadastro-page">
      <Paper className="cadastro-card" shadow="sm" radius="md" p="xl">
        <Stack gap="lg">
          <div className="cadastro-header">
            <span className="cadastro-icon">📋</span>
            <Title order={2}>Cadastro de Usuário</Title>
            <Text size="sm" c="dimmed">Preencha os dados abaixo</Text>
          </div>
          <form onSubmit={handleSubmit}>
            <Stack gap="lg">
              {erro && (
                <Alert color="red" variant="light" title="Erro">
                  {erro}
                </Alert>
              )}
              <div className="cadastro-grid">
                <TextInput
                  label="Nome completo"
                  name="nome"
                  placeholder="João Silva"
                  value={form.nome}
                  onChange={handleChange}
                  required
                  minLength={3}
                  size="md"
                  w="100%"
                />
                <TextInput
                  label="E-mail"
                  name="email"
                  type="email"
                  placeholder="seu@email.com"
                  value={form.email}
                  onChange={handleChange}
                  required
                  size="md"
                  w="100%"
                />
                <PasswordInput
                  label="Senha"
                  description="Mín. 8 caracteres, 1 maiúscula, 1 número, 1 especial"
                  name="senha"
                  value={form.senha}
                  onChange={handleChange}
                  required
                  minLength={8}
                  size="md"
                  w="100%"
                />
                <TextInput
                  label="CPF (11 dígitos)"
                  name="cpf"
                  placeholder="12345678900"
                  value={form.cpf}
                  onChange={handleChange}
                  required
                  pattern="\d{11}"
                  maxLength={11}
                  size="md"
                  w="100%"
                />
                <TextInput
                  label="RG"
                  name="rg"
                  placeholder="MG123456"
                  value={form.rg}
                  onChange={handleChange}
                  required
                  minLength={5}
                  size="md"
                  w="100%"
                />
                <TextInput
                  label="Data de nascimento"
                  name="data_de_nascimento"
                  type="date"
                  value={form.data_de_nascimento}
                  onChange={handleChange}
                  required
                  size="md"
                  w="100%"
                />
                <TextInput
                  className="cadastro-field-full"
                  label="Serviço prestado"
                  name="servico"
                  placeholder="Ex.: Corretor, Administrador"
                  value={form.servico}
                  onChange={handleChange}
                  required
                  minLength={1}
                  maxLength={150}
                  size="md"
                  w="100%"
                />
              </div>
              <Button type="submit" loading={loading} fullWidth size="md">
                {loading ? 'Cadastrando...' : 'Cadastrar'}
              </Button>
            </Stack>
          </form>
          <Text size="sm" c="dimmed" ta="center">
            Já tem conta? <Link to="/login">Entrar</Link>
          </Text>
        </Stack>
      </Paper>
    </div>
  )
}
