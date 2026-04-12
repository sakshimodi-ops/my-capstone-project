from django.contrib import admin
from .models import User, Pet, Shelter, Product_form, Order_table, Feedback, PetHealth, ChatHistory, PasswordResetToken

admin.site.register(User)
admin.site.register(Pet)
admin.site.register(Shelter)
admin.site.register(Product_form)
admin.site.register(Order_table)
admin.site.register(Feedback)
admin.site.register(PetHealth)
admin.site.register(ChatHistory)
admin.site.register(PasswordResetToken)