"""Formularze strony: formularz kontaktowy w sekcji "Kontakt"."""
from django import forms

from .models import ContactMessage


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

    def is_spam(self):
        return bool(self.cleaned_data.get('website'))
