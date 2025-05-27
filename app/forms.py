from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, RadioField, IntegerField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError
from models import Usuario

class FormularioSolarForm(FlaskForm):
    # Seção "SOBRE VOCÊ"
    nome_completo = StringField('Nome completo', validators=[DataRequired(), Length(min=3, max=100)])
    documento = StringField('CPF ou CNPJ', validators=[DataRequired(), Length(min=11, max=18)])
    telefone = StringField('Telefone (WhatsApp)', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    
    # Seção "ONDE FICA O IMÓVEL"
    endereco = TextAreaField('Endereço completo', validators=[DataRequired(), Length(max=200)])
    tipo_imovel = SelectField('É casa ou comércio?', choices=[
        ('casa', 'Casa'), 
        ('comercio', 'Comércio')
    ], validators=[DataRequired()])
    telhado_livre = BooleanField('Tem telhado livre para instalar os painéis solares?')
    telhado_sol = BooleanField('O telhado pega sol direto a maior parte do dia?')
    
    # Seção "SOBRE SUA CONTA DE LUZ"
    gasto_mensal = StringField('Gasta mais ou menos quanto por mês com luz?', validators=[DataRequired()])
    tem_contas = BooleanField('Tem as contas dos últimos meses?')
    tipo_voltagem = SelectField('A luz é 110V, 220V ou tem as duas?', choices=[
        ('110v', '110V'), 
        ('220v', '220V'), 
        ('ambos', 'Ambos')
    ], validators=[DataRequired()])
    qtd_pessoas = IntegerField('Quantas pessoas moram ou trabalham no local?', validators=[DataRequired()])
    
    # Seção "OBJETIVO DO PROJETO"
    objetivo_projeto = SelectField('Quer zerar a conta de luz ou só diminuir?', choices=[
        ('zerar', 'Zerar a conta'), 
        ('diminuir', 'Diminuir a conta')
    ], validators=[DataRequired()])
    novos_aparelhos = BooleanField('Pensa em colocar mais aparelhos no futuro?')
    tipo_sistema = SelectField('Prefere que a energia solar funcione junto com a rede elétrica ou quer que funcione mesmo sem luz da rua?', choices=[
        ('on-grid', 'Só quando tiver energia da rua (on-grid)'), 
        ('off-grid', 'Mesmo sem energia da rua (off-grid)'), 
        ('hibrido', 'Os dois (híbrido)')
    ], validators=[DataRequired()])
    
    # Uploads e observações
    foto_telhado = FileField('Foto do telhado', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens são permitidas.')
    ])
    foto_conta = FileField('Foto da conta de luz mais recente', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Apenas imagens ou PDF são permitidos.')
    ])
    observacoes = TextAreaField('Tem alguma dúvida ou algo que queira comentar?', validators=[Optional(), Length(max=500)])

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])

class RegistroForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[
        DataRequired(), 
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres')
    ])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(), 
        EqualTo('senha', message='As senhas devem ser iguais')
    ])
    admin = BooleanField('Administrador')
    ativo = BooleanField('Ativo', default=True)
    
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este e-mail já está em uso. Por favor, escolha outro.')