import { useState } from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Layout.css'

export function Layout() {
  const { logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    setMenuOpen(false)
    navigate('/login')
  }

  const closeMenu = () => setMenuOpen(false)

  return (
    <div className="layout">
      <header className="layout-header">
        <Link to="/" className="layout-brand" onClick={closeMenu}>
          <span className="layout-brand-icon">🏢</span>
          Sistema Gestão Imobiliária
        </Link>
        {isAuthenticated && (
          <>
            <button
              type="button"
              className="layout-menu-toggle"
              onClick={() => setMenuOpen((o) => !o)}
              aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
            >
              {menuOpen ? '✕' : '☰'}
            </button>
            <nav className={`layout-nav ${menuOpen ? 'is-open' : ''}`}>
              <Link to="/" onClick={closeMenu}>Dashboard</Link>
              <Link to="/usuarios" onClick={closeMenu}>Usuários</Link>
              <Link to="/imoveis" onClick={closeMenu}>Imóveis</Link>
              <button className="layout-logout" onClick={handleLogout}>
                Sair
              </button>
            </nav>
          </>
        )}
      </header>
      <main className="layout-main">
        <Outlet />
      </main>
    </div>
  )
}
