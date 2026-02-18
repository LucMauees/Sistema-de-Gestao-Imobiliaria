import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const authApi = {
  login: (email: string, senha: string) =>
    api.post('/auth/login', { email, senha }),
  cadastro: (data: {
    nome: string
    email: string
    senha: string
    cpf: string
    rg: string
    data_de_nascimento: string
  }) => api.post('/auth/CadastroUsuarios', data),
  usuarios: (skip = 0, limit = 100) =>
    api.get('/auth/usuarios', { params: { skip, limit } }),
}

// Imóveis
export const imoveisApi = {
  criar: (data: {
    rua: string
    numero?: string
    complemento?: string
    bairro: string
    municipio: string
    estado: string
    cep: string
    area_total_m2: number
    cliente_id: number
  }) => api.post('/imoveis/', data),
  obter: (id: number) => api.get(`/imoveis/${id}`),
  criarUnidade: (imovelId: number, data: {
    nome_unidade: string
    area_m2: number
    descricao?: string
    contrato_id?: number
  }) => api.post(`/imoveis/${imovelId}/unidades`, data),
  calcularIptu: (imovelId: number, valor_total_iptu: number, desconto_cota_unica?: number) =>
    api.post(`/imoveis/${imovelId}/iptu/calc`, {
      valor_total_iptu,
      desconto_cota_unica: desconto_cota_unica ?? 0,
    }),
}
