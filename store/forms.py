from django import forms
from store.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # ফর্মে কোন কোন ফিল্ড দেখাতে চান, তা এখানে বলে দিন
        fields = ['product_name', 'slug', 'description', 'price', 'images', 'stock', 'is_available', 'category']
        
        # ফর্মটিকে বুটস্ট্র্যাপ দিয়ে সুন্দর করার জন্য widgets ব্যবহার করা হলো
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'product-url-name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'images': forms.FileInput(attrs={'class': 'form-control'}),
        }