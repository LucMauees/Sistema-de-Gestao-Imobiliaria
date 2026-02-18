import { useState, useEffect } from 'react'
import { authApi } from '../lib/api'
import './Usuarios.css'

interface Usuario {
  id: number
  nome: string
  email: string
  cpf: string
}

export function Usuarios() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  useEffect(() => {
    authApi
      .usuarios()
      .then((res) => setUsuarios(res.data))
      .catch((err) => setErro(err.response?.data?.detail || 'Erro ao carregar'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="usuarios-loading">Carregando...</div>
  if (erro) return <div className="usuarios-erro">{erro}</div>

  return (
    <div className="usuarios">
      <h1 className="usuarios-title">Usuários</h1>
      <p className="usuarios-subtitle">{usuarios.length} usuário(s) cadastrado(s)</p>

      <div className="usuarios-table-wrap">
        <table className="usuarios-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nome</th>
              <th>E-mail</th>
              <th>CPF</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u) => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.nome}</td>
                <td>{u.email}</td>
                <td>{u.cpf}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
