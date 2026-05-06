# 🚀 Guia de Deploy no Vercel — Sistema de Pacientes

## 📁 Estrutura de Arquivos Necessária

```
meu-projeto/
├── api/
│   └── index.py          ← backend Flask (este arquivo)
├── public/
│   ├── login.html
│   ├── index.html
│   ├── paciente.html
│   ├── responsavel.html
│   ├── afericao.html
│   ├── medicacao.html
│   └── ... (todos os seus .html)
├── vercel.json            ← configuração do Vercel
└── requirements.txt       ← dependências Python
```

---

## ⚠️ AVISO IMPORTANTE — Banco de Dados SQLite no Vercel

O Vercel é uma plataforma **serverless** (sem estado persistente).  
O SQLite funcionará em `/tmp`, mas **os dados são apagados quando a função "dorme"** (geralmente após alguns minutos sem uso).

### Opções para banco de dados persistente (recomendado para produção):

| Opção | Plano Gratuito | Facilidade |
|---|---|---|
| **Supabase (PostgreSQL)** | ✅ 500MB grátis | ⭐⭐⭐ Fácil |
| **PlanetScale (MySQL)** | ✅ 5GB grátis | ⭐⭐⭐ Fácil |
| **Turso (SQLite na nuvem)** | ✅ 500MB grátis | ⭐⭐ Médio |
| **Vercel Postgres** | ✅ Plano hobby | ⭐⭐⭐ Fácil |

> Para um projeto de saúde em produção real, **Supabase** é a melhor opção gratuita.

---

## 📋 Passo a Passo para Deploy

### 1. Instale o Vercel CLI (opcional, mas facilita)
```bash
npm install -g vercel
```

### 2. Crie sua conta em vercel.com

### 3. Organize os arquivos
- Coloque `api/index.py`, `vercel.json` e `requirements.txt` na raiz do projeto
- Mova todos os seus arquivos `.html` para a pasta `public/`

### 4. Ajuste os caminhos nos HTMLs
Em cada arquivo `.html`, certifique-se que as chamadas à API usam caminhos relativos:
```javascript
// ✅ Correto (funciona local e no Vercel)
const resposta = await fetch('/api/pacientes');

// ❌ Errado (hardcoded localhost)
const resposta = await fetch('http://localhost:5000/api/pacientes');
```

### 5. Deploy via CLI
```bash
cd meu-projeto
vercel
# Siga as instruções na tela
```

### 6. Deploy via GitHub (recomendado)
1. Suba o projeto para um repositório GitHub
2. Acesse vercel.com → "New Project"
3. Conecte o repositório
4. Clique em "Deploy" — é só isso!

---

## 🔧 Configurações do vercel.json (explicação)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"    ← usa o runtime Python do Vercel
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"    ← rotas /api/* vão para o Flask
    },
    {
      "src": "/(.*)",
      "dest": "api/index.py"    ← todo o resto também vai para o Flask
    }
  ]
}
```

---

## 🔄 Para Desenvolvimento Local (sem Vercel)

```bash
# Instale as dependências
pip install flask flask-cors

# Execute o servidor
python api/index.py

# Acesse: http://localhost:5000
```

---

## 🆙 Migração para Banco Persistente (Supabase)

Se quiser dados que não se perdem, siga estes passos:

1. Crie conta em **supabase.com**
2. Crie um projeto → copie a **DATABASE_URL**
3. Instale psycopg2: adicione `psycopg2-binary` ao `requirements.txt`
4. Substitua `sqlite3` por `psycopg2` no `api/index.py`
5. No Vercel, vá em Settings → Environment Variables → adicione `DATABASE_URL`

---

## ❓ Problemas Comuns

| Erro | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError: flask` | requirements.txt não encontrado | Certifique que está na raiz do projeto |
| `404 Not Found` nas rotas HTML | HTMLs não estão na pasta `public/` | Mova os arquivos HTML para `/public` |
| Dados somem após alguns minutos | SQLite em /tmp é volátil | Use banco externo (ver seção acima) |
| `CORS error` no browser | Frontend em domínio diferente | Já está resolvido com flask-cors |
