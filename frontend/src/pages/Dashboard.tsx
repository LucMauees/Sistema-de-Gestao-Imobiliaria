import { Link } from 'react-router-dom'
import './Dashboard.css'

export function Dashboard() {
  return (
    <div className="dashboard">
      <h1 className="dashboard-title">Dashboard</h1>
      <p className="dashboard-subtitle">Bem-vindo ao Sistema de Gestão Imobiliária</p>

      <div className="dashboard-cards">
        <Link to="/usuarios" className="dashboard-card">
          <span className="dashboard-card-icon">👥</span>
          <h3>Usuários</h3>
          <p>Gerenciar usuários do sistema</p>
        </Link>
        <Link to="/imoveis" className="dashboard-card">
          <span className="dashboard-card-icon">🏠</span>
          <h3>Imóveis</h3>
          <p>Cadastro de imóveis e unidades</p>
        </Link>
      </div>
    </div>
  )
}
