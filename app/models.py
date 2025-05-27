from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Formulario(db.Model):
    __tablename__ = 'formularios'
    
    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Seção "SOBRE VOCÊ"
    nome_completo = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), nullable=False)  # CPF ou CNPJ
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    
    # Seção "ONDE FICA O IMÓVEL"
    endereco = db.Column(db.String(200), nullable=False)
    tipo_imovel = db.Column(db.String(20), nullable=False)  # Casa ou Comércio
    telhado_livre = db.Column(db.Boolean, default=False)
    telhado_sol = db.Column(db.Boolean, default=False)
    
    # Seção "SOBRE SUA CONTA DE LUZ"
    gasto_mensal = db.Column(db.String(50), nullable=True)
    tem_contas = db.Column(db.Boolean, default=False)
    tipo_voltagem = db.Column(db.String(20), nullable=True)  # 110V, 220V ou ambos
    qtd_pessoas = db.Column(db.Integer, nullable=True)
    
    # Seção "OBJETIVO DO PROJETO"
    objetivo_projeto = db.Column(db.String(50), nullable=True)  # Zerar ou diminuir
    novos_aparelhos = db.Column(db.Boolean, default=False)
    tipo_sistema = db.Column(db.String(20), nullable=True)  # on-grid, off-grid, híbrido
    
    # Observações adicionais
    observacoes = db.Column(db.Text, nullable=True)
    
    # Relacionamento com arquivos
    arquivos = db.relationship('Arquivo', backref='formulario', lazy=True)
    
    def __repr__(self):
        return f'<Formulario {self.id} - {self.nome_completo}>'

class Arquivo(db.Model):
    __tablename__ = 'arquivos'
    
    id = db.Column(db.Integer, primary_key=True)
    formulario_id = db.Column(db.Integer, db.ForeignKey('formularios.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'telhado' ou 'conta'
    nome_arquivo = db.Column(db.String(100), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Arquivo {self.id} - {self.tipo}>'