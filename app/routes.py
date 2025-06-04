from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import csv
import io
import time
from datetime import datetime
from functools import wraps
from models import db, Usuario, Formulario, Arquivo
from forms import FormularioSolarForm, LoginForm, RegistroForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa extensões
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Cria diretório para uploads
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def init_db():
    max_retries = 5
    retry_interval = 5
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Create all tables
                db.create_all()
                
                # Check if admin user exists
                if not Usuario.query.filter_by(admin=True).first():
                    admin = Usuario(
                        nome='Administrador',
                        email='admin@admin.com',
                        senha=generate_password_hash('admin123'),
                        admin=True,
                        ativo=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("Admin user created successfully")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Failed to connect to database after multiple attempts")
                raise e

@login_manager.user_loader
def carregar_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

def admin_necessario(f):
    @wraps(f)
    def funcao_decorada(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            flash('Acesso negado. Você precisa ser administrador para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return funcao_decorada

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/formulario', methods=['GET', 'POST']) 
def formulario():
    form = FormularioSolarForm()
    
    if form.validate_on_submit():
        novo_formulario = Formulario(
            nome_completo=form.nome_completo.data,
            documento=form.documento.data,
            telefone=form.telefone.data,
            email=form.email.data,
            endereco=form.endereco.data,
            tipo_imovel=form.tipo_imovel.data,
            telhado_livre=form.telhado_livre.data,
            telhado_sol=form.telhado_sol.data,
            gasto_mensal=form.gasto_mensal.data,
            tem_contas=form.tem_contas.data,
            tipo_voltagem=form.tipo_voltagem.data,
            qtd_pessoas=form.qtd_pessoas.data,
            objetivo_projeto=form.objetivo_projeto.data,
            novos_aparelhos=form.novos_aparelhos.data,
            tipo_sistema=form.tipo_sistema.data,
            observacoes=form.observacoes.data
        )
        
        db.session.add(novo_formulario)
        db.session.flush()
        
        # Processar uploads
        if form.foto_telhado.data:
            arquivo_telhado = Arquivo(
                formulario_id=novo_formulario.id,
                tipo='telhado',
                nome_arquivo=secure_filename(form.foto_telhado.data.filename)
            )
            db.session.add(arquivo_telhado)
            form.foto_telhado.data.save(os.path.join(app.config['UPLOAD_FOLDER'], arquivo_telhado.nome_arquivo))
            
        if form.foto_conta.data:
            arquivo_conta = Arquivo(
                formulario_id=novo_formulario.id,
                tipo='conta',
                nome_arquivo=secure_filename(form.foto_conta.data.filename)
            )
            db.session.add(arquivo_conta)
            form.foto_conta.data.save(os.path.join(app.config['UPLOAD_FOLDER'], arquivo_conta.nome_arquivo))
        
        db.session.commit()
        flash('Formulário enviado com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('confirmacao'))
        
    return render_template('formulario.html', form=form)

@app.route('/confirmacao')
def confirmacao():
    return render_template('confirmacao.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        
        if usuario and usuario.ativo and check_password_hash(usuario.senha, form.senha.data):
            login_user(usuario)
            proxima_pagina = request.args.get('next')
            return redirect(proxima_pagina or url_for('admin_dashboard'))
        else:
            flash('Login inválido ou usuário inativo', 'danger')
            
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema', 'info')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/formularios')
@login_required
def admin_formularios():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Inicializa a query
    query = Formulario.query
    
    # Aplica filtros
    busca = request.args.get('busca', '').strip()
    tipo_imovel = request.args.get('tipo_imovel', '')
    data_inicio = request.args.get('data_inicio', '')
    
    if busca:
        query = query.filter(
            db.or_(
                Formulario.nome_completo.ilike(f'%{busca}%'),
                Formulario.documento.ilike(f'%{busca}%')
            )
        )
    
    if tipo_imovel:
        query = query.filter(Formulario.tipo_imovel == tipo_imovel)
    
    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(db.func.date(Formulario.data_criacao) >= data_inicio)
        except ValueError:
            pass
    
    # Ordena por data de criação (mais recente primeiro)
    query = query.order_by(Formulario.data_criacao.desc())
    
    # Paginação
    formularios = query.paginate(page=page, per_page=per_page)
    
    return render_template('admin/formularios.html', 
                         formularios=formularios,
                         busca=busca,
                         tipo_imovel=tipo_imovel,
                         data_inicio=data_inicio)

@app.route('/admin/formulario/<int:id>')
@login_required
def visualizar_formulario(id):
    formulario = Formulario.query.get_or_404(id)
    arquivos = Arquivo.query.filter_by(formulario_id=id).all()
    return render_template('admin/visualizar_formulario.html', formulario=formulario, arquivos=arquivos)

@app.route('/admin/usuarios')
@login_required
@admin_necessario
def admin_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/adicionar_usuario', methods=['GET', 'POST'])
@login_required
@admin_necessario
def adicionar_usuario():
    form = RegistroForm()
    
    if form.validate_on_submit():
        hash_senha = generate_password_hash(form.senha.data)
        
        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data,
            senha=hash_senha,
            admin=form.admin.data,
            ativo=True
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Usuário adicionado com sucesso!', 'success')
        return redirect(url_for('admin_usuarios'))
        
    return render_template('admin/adicionar_usuario.html', form=form)

@app.route('/admin/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_necessario
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    form = RegistroForm(obj=usuario)
    
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.admin = 'admin' in request.form
        usuario.ativo = 'ativo' in request.form
        
        if request.form['senha']:
            usuario.senha = generate_password_hash(request.form['senha'])
            
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin_usuarios'))
        
    return render_template('admin/editar_usuario.html', form=form, usuario=usuario)

@app.route('/admin/alternar_status/<int:id>')
@login_required
@admin_necessario
def alternar_status(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    flash(f'Status do usuário alterado para {"ativo" if usuario.ativo else "inativo"}', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/exportar_csv')
@login_required
def exportar_csv():
    formularios = Formulario.query.order_by(Formulario.data_criacao.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL, delimiter=',', escapechar='\\')
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Data', 'Nome Completo', 'Documento', 'Telefone', 'Email', 
        'Endereço', 'Tipo Imóvel', 'Telhado Livre', 'Telhado Sol', 
        'Gasto Mensal', 'Tem Contas', 'Tipo Voltagem', 'Qtd Pessoas', 
        'Objetivo Projeto', 'Novos Aparelhos', 'Tipo Sistema', 'Observações'
    ])
    
    # Dados
    for f in formularios:
        # Limpa e formata os dados antes de escrever
        nome_completo = f.nome_completo.replace('\n', ' ').strip() if f.nome_completo else ''
        documento = f.documento.replace('\n', ' ').strip() if f.documento else ''
        telefone = f.telefone.replace('\n', ' ').strip() if f.telefone else ''
        email = f.email.replace('\n', ' ').strip() if f.email else ''
        endereco = f.endereco.replace('\n', ' ').strip() if f.endereco else ''
        observacoes = f.observacoes.replace('\n', ' ').strip() if f.observacoes else ''
        
        writer.writerow([
            f.id,
            f.data_criacao.strftime('%d/%m/%Y %H:%M'),
            nome_completo,
            documento,
            telefone,
            email,
            endereco,
            f.tipo_imovel,
            'Sim' if f.telhado_livre else 'Não',
            'Sim' if f.telhado_sol else 'Não',
            f.gasto_mensal if f.gasto_mensal else '',
            'Sim' if f.tem_contas else 'Não',
            f.tipo_voltagem if f.tipo_voltagem else '',
            f.qtd_pessoas if f.qtd_pessoas else '',
            f.objetivo_projeto if f.objetivo_projeto else '',
            'Sim' if f.novos_aparelhos else 'Não',
            f.tipo_sistema if f.tipo_sistema else '',
            observacoes
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'formularios_energia_solar_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    )

@app.route('/uploads/<filename>')
@login_required
def arquivo_upload(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/admin/dashboard/dados')
@login_required
def dashboard_dados():
    # Contagem total de formulários
    total_formularios = Formulario.query.count()
    
    # Formulários do dia
    hoje = datetime.now().date()
    formularios_dia = Formulario.query.filter(
        db.func.date(Formulario.data_criacao) == hoje
    ).count()
    
    # Total de usuários ativos
    total_usuarios = Usuario.query.filter_by(ativo=True).count()
    
    # Total de arquivos
    total_arquivos = Arquivo.query.count()
    
    # Formulários recentes (últimos 5)
    formularios_recentes = Formulario.query.order_by(
        Formulario.data_criacao.desc()
    ).limit(5).all()
    
    # Formatar dados dos formulários recentes
    formularios = [{
        'id': f.id,
        'nome': f.nome_completo,
        'data': f.data_criacao.strftime('%d/%m/%Y'),
        'tipo': 'Casa' if f.tipo_imovel == 'casa' else 'Comércio'
    } for f in formularios_recentes]
    
    return jsonify({
        'totalFormularios': total_formularios,
        'formulariosDia': formularios_dia,
        'totalUsuarios': total_usuarios,
        'totalArquivos': total_arquivos,
        'formularios': formularios
    })

#Rota para exportar o formulário em csv de uma unica pessoa.
@app.route('/admin/formulario/<int:id>/exportar_csv')
@login_required
def exportar_formulario_csv(id):
    formulario = Formulario.query.get_or_404(id)
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL, delimiter=',', escapechar='\\')
    
    # Cabeçalho
    writer.writerow([
        'ID', 'Data', 'Nome Completo', 'Documento', 'Telefone', 'Email', 
        'Endereço', 'Tipo Imóvel', 'Telhado Livre', 'Telhado Sol', 
        'Gasto Mensal', 'Tem Contas', 'Tipo Voltagem', 'Qtd Pessoas', 
        'Objetivo Projeto', 'Novos Aparelhos', 'Tipo Sistema', 'Observações'
    ])
    
    # Limpa e formata os dados antes de escrever
    nome_completo = formulario.nome_completo.replace('\n', ' ').strip() if formulario.nome_completo else ''
    documento = formulario.documento.replace('\n', ' ').strip() if formulario.documento else ''
    telefone = formulario.telefone.replace('\n', ' ').strip() if formulario.telefone else ''
    email = formulario.email.replace('\n', ' ').strip() if formulario.email else ''
    endereco = formulario.endereco.replace('\n', ' ').strip() if formulario.endereco else ''
    observacoes = formulario.observacoes.replace('\n', ' ').strip() if formulario.observacoes else ''
    
    # Dados
    writer.writerow([
        formulario.id,
        formulario.data_criacao.strftime('%d/%m/%Y %H:%M'),
        nome_completo,
        documento,
        telefone,
        email,
        endereco,
        formulario.tipo_imovel,
        'Sim' if formulario.telhado_livre else 'Não',
        'Sim' if formulario.telhado_sol else 'Não',
        formulario.gasto_mensal if formulario.gasto_mensal else '',
        'Sim' if formulario.tem_contas else 'Não',
        formulario.tipo_voltagem if formulario.tipo_voltagem else '',
        formulario.qtd_pessoas if formulario.qtd_pessoas else '',
        formulario.objetivo_projeto if formulario.objetivo_projeto else '',
        'Sim' if formulario.novos_aparelhos else 'Não',
        formulario.tipo_sistema if formulario.tipo_sistema else '',
        observacoes
    ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'formulario_{formulario.id}_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    )

# Inicializar o banco de dados
init_db()