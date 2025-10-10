from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from django.forms import inlineformset_factory

from naya_site import models
from .models import UserProfile, State, Orcamento, ItemOrcamento, ArquivoOrcamento, Product
import re


class ProductForm(forms.ModelForm):
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        required=False
    )

    class Meta:
        model = models.Product
        fields = (
            'name', 'quantity', 'minimum_quantity',
            'unit_value', 'category', 'image',
        )


class RegisterForm(UserCreationForm):
    cpf = forms.CharField(
        max_length=14,
        required=True,
        help_text='Formato: 000.000.000-00',
        # validators=[
        #     RegexValidator(
        #         regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        #         message='CPF deve estar no formato: 000.000.000-00'
        #     )
        # ]
    )

    cep = forms.CharField(max_length=9, validators=[
                          RegexValidator(regex=r'^\d{5}-\d{3}$')])
    logradouro = forms.CharField(max_length=200)
    numero = forms.CharField(max_length=10)
    complemento = forms.CharField(max_length=100, required=False)
    bairro = forms.CharField(max_length=100)
    cidade = forms.CharField(max_length=100)
    state = forms.ChoiceField(
        choices=[('', 'Selecione o estado')] + State.STATE_CHOICES,
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'username', 'cpf', 'state',
            'cidade', 'logradouro', 'cep', 'numero', 'complemento', 'bairro',
        )

    def clean_email(self):
        first_name = forms.CharField(
            required=True,
            min_length=3,
        )

        last_name = forms.CharField(
            required=True,
            min_length=3,
        )

        email = forms.EmailField(
            required=True,
        )

        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            self.add_error(
                'email',
                ValidationError('Já existe este email', code='invalid')
            )

        return email


class RegisterUpdateForm(forms.ModelForm):

    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        help_text='Required.',
        error_messages={
            'min_length': 'Please, add more than 2 letters.'
        }
    )

    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=True,
        help_text='Required.'
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )

    password2 = forms.CharField(
        label="Password 2",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='Use the same password as before.',
        required=False,
    )

    cpf = forms.CharField(
        max_length=14,
        required=True,
        help_text='Formato: 000.000.000-00',
        # validators=[
        #     RegexValidator(
        #         regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
        #         message='CPF deve estar no formato: 000.000.000-00'
        #     )
        # ]
    )

    cep = forms.CharField(max_length=9, validators=[
                          RegexValidator(regex=r'^\d{5}-\d{3}$')])
    logradouro = forms.CharField(max_length=200)
    numero = forms.CharField(max_length=10)
    complemento = forms.CharField(max_length=100, required=False)
    bairro = forms.CharField(max_length=100)
    cidade = forms.CharField(max_length=100)
    state = forms.ModelChoiceField(
        queryset=State.objects.all().order_by('name'),
        required=False,
        empty_label="Selecione o estado"
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'username', 'cpf', 'state',
            'cidade', 'logradouro', 'cep', 'numero', 'complemento', 'bairro',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['cpf'].initial = profile.cpf
            self.fields['cep'].initial = profile.cep
            self.fields['logradouro'].initial = profile.logradouro
            self.fields['numero'].initial = profile.numero
            self.fields['complemento'].initial = profile.complemento
            self.fields['bairro'].initial = profile.bairro
            self.fields['cidade'].initial = profile.cidade
            self.fields['state'].initial = profile.state

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove formatação
            cpf_clean = re.sub(r'[^\d]', '', cpf)

            # Verifica se já existe
            if UserProfile.objects.filter(cpf=cpf).exists():
                # Se estiver editando, verifica se é o mesmo usuário
                if self.instance and self.instance.pk:
                    try:
                        profile = UserProfile.objects.get(user=self.instance)
                        if profile.cpf != cpf:
                            raise forms.ValidationError('CPF já cadastrado')
                    except UserProfile.DoesNotExist:
                        raise forms.ValidationError('CPF já cadastrado')
                else:
                    raise forms.ValidationError('CPF já cadastrado')

            # Validação do CPF
            if not self.validar_cpf(cpf_clean):
                raise forms.ValidationError('CPF inválido')

        return cpf

    def validar_cpf(self, cpf):
        """Validação de CPF"""
        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        # Cálculo dos dígitos verificadores
        def calcular_digito(cpf, peso_inicial):
            soma = 0
            for i, digito in enumerate(cpf[:peso_inicial-1]):
                soma += int(digito) * (peso_inicial - i)
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        digito1 = calcular_digito(cpf, 10)
        digito2 = calcular_digito(cpf, 11)

        return int(cpf[9]) == digito1 and int(cpf[10]) == digito2

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = super().save(commit=commit)
        password = cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if hasattr(user, 'profile'):
            profile = user.profile
        else:
            profile = UserProfile(user=user)

        profile.cpf = self.cleaned_data['cpf']
        profile.cep = self.cleaned_data['cep']
        profile.logradouro = self.cleaned_data['logradouro']
        profile.numero = self.cleaned_data['numero']
        profile.complemento = self.cleaned_data['complemento']
        profile.bairro = self.cleaned_data['bairro']
        profile.cidade = self.cleaned_data['cidade']
        profile.state = self.cleaned_data['state']

        if commit:
            profile.save()
        return user

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                self.add_error(
                    'password2',
                    ValidationError('Senhas não batem')
                )
        return super().clean()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email
        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError('Já existe este e-mail', code='invalid')
                )

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error(
                    'password1',
                    ValidationError(errors)
                )

        return password1


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['data_maxima_entrega', 'observacoes_cliente']
        widgets = {
            'data_maxima_entrega': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'observacoes_cliente': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control',
                       'placeholder': 'Observações gerais sobre o orçamento...'}
            ),
        }


class ItemOrcamentoForm(forms.ModelForm):
    arquivos = MultipleFileField(
        required=False, help_text="Selecione múltiplos arquivos")

    class Meta:
        model = ItemOrcamento
        fields = ['produto', 'quantidade', 'descricao_personalizacao']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control produto-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'descricao_personalizacao': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control',
                       'placeholder': 'Descreva como gostaria que fosse feita a personalização...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produto'].queryset = Product.objects.filter(ativo=True)


class RespostaOrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['valor_frete', 'data_prevista_entrega',
                  'observacoes_empresa', 'nao_possivel_prazo']
        widgets = {
            'valor_frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_prevista_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes_empresa': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'nao_possivel_prazo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ItemRespostaForm(forms.ModelForm):
    arquivos_empresa = MultipleFileField(
        required=False, help_text="Imagens desenvolvidas pela empresa")

    class Meta:
        model = ItemOrcamento
        fields = ['preco_unitario']
        widgets = {
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
