from django import forms
from .models import PendaftaranPKL

class PendaftaranPKLForm(forms.ModelForm):
    class Meta:
        model = PendaftaranPKL
        fields = ['perusahaan', 'kelas', 'alasan', 'cv']
        widgets = {
            'perusahaan': forms.Select(attrs={
                'class': 'w-full border border-green-300 rounded-lg p-2'
            }),
            'kelas': forms.Select(attrs={
                'class': 'w-full border border-green-300 rounded-lg p-2'
            }),
            'alasan': forms.Textarea(attrs={
                'class': 'w-full border border-green-300 rounded-lg p-2',
                'rows': 4,
                'placeholder': 'Tuliskan alasan memilih perusahaan ini...'
            }),
            'cv': forms.FileInput(attrs={
                'class': 'w-full border border-green-300 rounded-lg p-2',
                'accept': '.pdf'  # hanya PDF di browser
            }),
        }

    def clean_cv(self):
        cv = self.cleaned_data.get('cv', False)
        if cv:
            if not cv.name.endswith('.pdf'):
                raise forms.ValidationError("File CV harus berupa PDF!")
            if cv.size > 5*1024*1024:
                raise forms.ValidationError("Ukuran file CV maksimal 5MB.")
        return cv
