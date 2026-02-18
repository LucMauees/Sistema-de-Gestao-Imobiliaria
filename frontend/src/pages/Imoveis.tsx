import { useState } from 'react'
import {
  TextInput,
  NumberInput,
  Button,
  Alert,
  Stack,
  Paper,
  SimpleGrid,
} from '@mantine/core'
import './Imoveis.css'

export function Imoveis() {
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    rua: '',
    numero: '',
    complemento: '',
    bairro: '',
    municipio: '',
    estado: '',
    cep: '',
    area_total_m2: '',
    cliente_id: '',
  })
  const [erro, setErro] = useState('')
  const [sucesso, setSucesso] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const setFormValue = (key: string, value: string | number) => {
    setForm((prev) => ({ ...prev, [key]: String(value) }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErro('')
    setSucesso('')
    try {
      const { imoveisApi } = await import('../lib/api')
      await imoveisApi.criar({
        rua: form.rua,
        numero: form.numero || undefined,
        complemento: form.complemento || undefined,
        bairro: form.bairro,
        municipio: form.municipio,
        estado: form.estado,
        cep: form.cep,
        area_total_m2: parseFloat(form.area_total_m2),
        cliente_id: parseInt(form.cliente_id, 10),
      })
      setSucesso('Imóvel cadastrado com sucesso!')
      setForm({
        rua: '',
        numero: '',
        complemento: '',
        bairro: '',
        municipio: '',
        estado: '',
        cep: '',
        area_total_m2: '',
        cliente_id: '',
      })
      setShowForm(false)
    } catch (err: unknown) {
      const res = err as { response?: { data?: { detail?: string | string[] } } }
      const detail = res?.response?.data?.detail
      const msg = Array.isArray(detail) ? detail.join(', ') : detail
      setErro(msg || 'Erro ao cadastrar imóvel')
    }
  }

  return (
    <div className="imoveis">
      <div className="imoveis-header">
        <div>
          <h1 className="imoveis-title">Imóveis</h1>
          <p className="imoveis-subtitle">Cadastro e gestão de imóveis</p>
        </div>
        <Button
          variant="filled"
          onClick={() => setShowForm(!showForm)}
          size="md"
        >
          {showForm ? 'Cancelar' : '+ Novo imóvel'}
        </Button>
      </div>

      {sucesso && (
        <Alert color="blue" variant="light" mb="md">
          {sucesso}
        </Alert>
      )}
      {erro && (
        <Alert color="red" variant="light" mb="md" title="Erro">
          {erro}
        </Alert>
      )}

      {showForm && (
        <Paper withBorder p="lg" radius="md" mb="lg" className="imoveis-form">
          <form onSubmit={handleSubmit}>
            <Stack gap="md">
              <SimpleGrid cols={{ base: 1, xs: 2, sm: 3 }} spacing="md">
                <TextInput
                  label="Rua"
                  name="rua"
                  value={form.rua}
                  onChange={handleChange}
                  required
                  size="md"
                />
                <TextInput
                  label="Número"
                  name="numero"
                  value={form.numero}
                  onChange={handleChange}
                  size="md"
                />
                <TextInput
                  label="Complemento"
                  name="complemento"
                  value={form.complemento}
                  onChange={handleChange}
                  size="md"
                />
                <TextInput
                  label="Bairro"
                  name="bairro"
                  value={form.bairro}
                  onChange={handleChange}
                  required
                  size="md"
                />
                <TextInput
                  label="Município"
                  name="municipio"
                  value={form.municipio}
                  onChange={handleChange}
                  required
                  size="md"
                />
                <TextInput
                  label="Estado (UF)"
                  name="estado"
                  placeholder="MG"
                  value={form.estado}
                  onChange={handleChange}
                  required
                  maxLength={2}
                  size="md"
                />
                <TextInput
                  label="CEP"
                  name="cep"
                  value={form.cep}
                  onChange={handleChange}
                  required
                  size="md"
                />
                <NumberInput
                  label="Área total (m²)"
                  value={form.area_total_m2 ? parseFloat(form.area_total_m2) : undefined}
                  onChange={(v) => setFormValue('area_total_m2', v ?? '')}
                  min={0}
                  decimalScale={2}
                  required
                  size="md"
                />
                <NumberInput
                  label="ID do cliente"
                  value={form.cliente_id ? parseInt(form.cliente_id, 10) : undefined}
                  onChange={(v) => setFormValue('cliente_id', v ?? '')}
                  min={1}
                  required
                  size="md"
                />
              </SimpleGrid>
              <Button type="submit" size="md">
                Cadastrar imóvel
              </Button>
            </Stack>
          </form>
        </Paper>
      )}

      <p className="imoveis-dica">
        Use o botão acima para cadastrar um novo imóvel. O ID do cliente deve corresponder a um cliente existente no sistema.
      </p>
    </div>
  )
}
