"""Formularze strony: formularz kontaktowy w sekcji "Kontakt".

Ochrona przed spamem (bez irytujacych dla ludzi zagadek typu CAPTCHA):
  1. pulapka (honeypot) – ukryte pole "website", ktore wypelniaja tylko boty,
  2. znacznik czasu – formularz wyslany szybciej niz MIN_SECONDS od otwarcia strony to bot,
     a znacznik jest podpisany kluczem strony, wiec nie da sie go podrobic,
  3. limit wysylek z jednego adresu IP – w widoku (core/views.py).
Boty z punktow 1–2 dostaja komunikat "wyslano", ale nic sie nie zapisuje (nie wiedza, ze wpadly).
"""
import time

from django import forms
from django.core import signing

from .models import ContactMessage

TOKEN_SALT = 'formularz-kontaktowy'
MIN_SECONDS = 3            # czlowiek nie wypelni formularza szybciej
MAX_AGE = 4 * 60 * 60      # znacznik wazny 4 godziny (dluzej otwarta karta -> prosba o odswiezenie)


def make_started_token(timestamp=None):
    """Podpisany znacznik czasu otwarcia formularza (ukryte pole "started")."""
    return signing.dumps(timestamp if timestamp is not None else time.time(), salt=TOKEN_SALT)


class ContactForm(forms.ModelForm):
    # Zgoda na przetwarzanie danych – wymagana, ale nie zapisywana w bazie
    consent = forms.BooleanField(
        required=True,
        label='Wyrażam zgodę na przetwarzanie moich danych w celu odpowiedzi na zapytanie.',
        error_messages={'required': 'Zaznacz zgodę, żebyśmy mogli odpowiedzieć.'})
    # Pulapka na boty (honeypot): pole ukryte w CSS, czlowiek go nie widzi i zostawia puste,
    # a automaty wypelniaja wszystkie pola. Wypelnione = spam.
    website = forms.CharField(required=False, label='Strona WWW')

    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'email', 'car', 'message']
        labels = {
            'name': 'Imię',
            'phone': 'Telefon',
            'email': 'E-mail (opcjonalnie)',
            'car': 'Auto (opcjonalnie)',
            'message': 'Wiadomość',
        }
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'name', 'placeholder': 'Jan'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'inputmode': 'tel', 'placeholder': '600 000 000'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'jan@example.com'}),
            'car': forms.TextInput(attrs={'placeholder': 'np. Skoda Octavia 2018'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Co się stało z szybą? Wolisz montaż u nas czy z dojazdem?'}),
        }
        error_messages = {
            'name': {'required': 'Podaj imię.'},
            'phone': {'required': 'Podaj numer telefonu, oddzwonimy.'},
            'email': {'invalid': 'Sprawdź adres e-mail.'},
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = [c for c in phone if c.isdigit()]
        if len(digits) < 9:
            raise forms.ValidationError('Numer telefonu powinien mieć co najmniej 9 cyfr.')
        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_bot = False

    @property
    def started_token(self):
        """Swiezy znacznik do szablonu – takze przy ponownym wyswietleniu formularza z bledami."""
        return make_started_token()

    def clean(self):
        cleaned = super().clean()
        token = self.data.get('started', '')
        expired_msg = 'Formularz był otwarty bardzo długo. Sprawdź dane i kliknij „Wyślij” jeszcze raz.'
        try:
            started = float(signing.loads(token, salt=TOKEN_SALT, max_age=MAX_AGE))
        except signing.SignatureExpired:
            # Ktos zostawil otwarta karte na kilka godzin – to czlowiek, prosimy o ponowne wyslanie
            raise forms.ValidationError(expired_msg)
        except (signing.BadSignature, TypeError, ValueError):
            # Brak albo podrobiony znacznik: wysylka z pominieciem strony – bot
            self.is_bot = True
            return cleaned
        # Sprawdzamy tez czas zapisany w znaczniku (nie tylko wiek podpisu)
        elapsed = time.time() - started
        if elapsed > MAX_AGE:
            raise forms.ValidationError(expired_msg)
        if elapsed < MIN_SECONDS:
            self.is_bot = True
        return cleaned

    def is_spam(self):
        return self.is_bot or bool(self.cleaned_data.get('website'))
